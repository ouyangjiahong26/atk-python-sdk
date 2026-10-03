"""
ATK Connect 模式 — 可见性（Access）分析

封装 4.2 新增的 Access / AER / Access_RM / AccessMulti 命令：

- :class:`AccessBuilder` — 一对一可见性计算与报告获取
- :class:`AccessMultiBuilder` — 先配置后计算的批量可见性框架
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from atk import exceptions as _ex
from atk import utils

if TYPE_CHECKING:
    from atk.connect.session import ATKConnection

# Access_RM 的 <ReportStyle> 合法取值（见帮助文档 Access_RM Access 页）
ACCESS_RM_STYLES = frozenset({
    "Access",
    "AER",
    "AER Rate",
    "UnAccessible",
    "UnAccessible AER",
    "Access Summary",
    "AER Summary",
    "UnAccessible Summary",
    "Range Rate",
})


def _time_param(start: str | None, stop: str | None) -> str:
    """构造 ``TimePeriod "s" "e"`` 或 ``UseObjectTimes`` 参数片段。"""
    if start:
        if not stop:
            raise _ex.ATKValueError(
                "stop must be provided together with start"
            )
        return f'TimePeriod "{start}" "{stop}"'
    if stop:
        raise _ex.ATKValueError(
            "start must be provided together with stop"
        )
    return "UseObjectTimes"


def _interval_param(start: str | None, stop: str | None) -> str:
    """构造 ``"s" "e"`` 或 ``UseObjectTimes`` 参数片段（无 TimePeriod 前缀）。"""
    if start:
        if not stop:
            raise _ex.ATKValueError(
                "stop must be provided together with start"
            )
        return f'"{start}" "{stop}"'
    if stop:
        raise _ex.ATKValueError(
            "start must be provided together with stop"
        )
    return "UseObjectTimes"


class AccessBuilder:
    """
    Connect 模式下单个对象可见性分析的构建器。

    通过 ``atk.access_builder()`` 创建。

    示例::

        access = atk.access_builder()
        access.compute('*/Satellite/Sat1', '*/Facility/Fac1',
                       '14 Mar 2024 00:00:00.000', '15 Mar 2024 00:00:00.000')
        report = access.access_rm('*/Satellite/Sat1', 'Access Summary')
    """

    def __init__(self, conn: "ATKConnection"):
        self._conn = conn

    def compute(
        self,
        obj_path: str,
        target_path: str,
        start: str,
        stop: str,
    ) -> Any:
        """
        计算两个对象之间的可见性，仅输出可见性报告。

        对应命令 ``Access <ObjectPath> <AccessObjectPath>
        TimePeriod "<Start>" "<Stop>"``。

        Parameters
        ----------
        obj_path : str
            发起可见性计算的对象路径（如 ``"*/Satellite/Sat1"``）。
        target_path : str
            被访问目标对象路径（如 ``"*/Facility/Fac1"``）。
        start, stop : str
            可见性计算时间范围（ATK 时间格式）。

        Returns
        -------
        原始 ATK 响应（``ACK`` 字符串或 ``CMDRESULT``）。
        """
        return self._conn.send(
            "Access",
            utils.resolve_path(obj_path),
            f'{utils.resolve_path(target_path)} '
            f'TimePeriod "{start}" "{stop}"',
        )

    def aer(
        self,
        obj_path: str,
        target_path: str,
        start: str,
        stop: str,
    ) -> Any:
        """
        计算可见性视线参数（AER）分析报告。

        对应命令 ``AER <ObjectPath> <AccessObjectPath>
        TimePeriod "<Start>" "<Stop>"``。

        Returns
        -------
        原始 ATK 响应（``ACK`` 字符串或 ``CMDRESULT``）。
        """
        return self._conn.send(
            "AER",
            utils.resolve_path(obj_path),
            f'{utils.resolve_path(target_path)} '
            f'TimePeriod "{start}" "{stop}"',
        )

    def access_rm(
        self,
        obj_path: str,
        style: str,
        start: str | None = None,
        stop: str | None = None,
    ) -> list[str]:
        """
        获取可见性报告（9 种样式可选）。

        对应命令 ``Access_RM <ObjectPath> Access Compute
        "<ReportStyle>" [{TimeInterval} | UseObjectTimes]``。

        Parameters
        ----------
        obj_path : str
            对象路径。
        style : str
            报告样式，取值见 :data:`ACCESS_RM_STYLES`
            （如 ``"Access"``、``"AER Summary"``、``"Range Rate"``）。
        start, stop : str, optional
            时间区间；都省略时使用对象自身时间（UseObjectTimes）。

        Returns
        -------
        list[str]
            解析后的报告数据行。
        """
        if style not in ACCESS_RM_STYLES:
            raise _ex.ATKValueError(
                f"Unknown Access_RM style {style!r}. "
                f"Valid styles: {sorted(ACCESS_RM_STYLES)}"
            )
        result = self._conn.send(
            "Access_RM",
            utils.resolve_path(obj_path),
            f'Access Compute "{style}" {_interval_param(start, stop)}',
        )
        return utils.result_to_list(result)


class AccessMultiBuilder:
    """
    Connect 模式下批量可见性（AccessMulti）的"先配置后计算"框架。

    通过 ``atk.access_multi()`` 创建。

    工作流：:meth:`add_assets` 指定观测者（卫星传感器等）→
    :meth:`add_objects` 指定被观测目标（地面站等）→
    :meth:`compute` 执行批量计算。

    示例::

        multi = atk.access_multi()
        multi.add_assets('*/Satellite/Sat1/Sensor/Sensor1')
        multi.add_objects('*/Facility/Target1', '*/Facility/Target2')
        multi.compute('26 Sep 2035 12:00:00.00', '28 Sep 2035 12:00:00.00')
    """

    def __init__(self, conn: "ATKConnection"):
        self._conn = conn

    def add_assets(self, *paths: str) -> "AccessMultiBuilder":
        """
        指定批量可见性计算的来源对象（观测者）。

        对应命令 ``AccessMulti / Assets <AssetObjectPath>...``。

        Parameters
        ----------
        *paths : str
            来源对象路径（如传感器路径），可传多个。

        Returns
        -------
        self
        """
        if not paths:
            raise _ex.ATKValueError("add_assets requires at least one path")
        joined = " ".join(utils.resolve_path(p) for p in paths)
        self._conn.send("AccessMulti", "/", f" Assets {joined}")
        return self

    def add_objects(self, *paths: str) -> "AccessMultiBuilder":
        """
        指定批量可见性计算的目标对象（被观测者）。

        对应命令 ``AccessMulti / Objects <CovObjectPath>...``。

        Returns
        -------
        self
        """
        if not paths:
            raise _ex.ATKValueError("add_objects requires at least one path")
        joined = " ".join(utils.resolve_path(p) for p in paths)
        self._conn.send("AccessMulti", "/", f" Objects {joined}")
        return self

    def compute(
        self,
        start: str | None = None,
        stop: str | None = None,
    ) -> Any:
        """
        清空之前的计算结果并基于当前配置重新批量计算可见性。

        对应命令 ``AccessMulti / Access Compute [{TimeInterval} | UseObjectTimes]``。

        Parameters
        ----------
        start, stop : str, optional
            计算时间区间；都省略时使用对象自身时间。

        Returns
        -------
        原始 ATK 响应。
        """
        return self._conn.send(
            "AccessMulti", "/", f" Access Compute {_interval_param(start, stop)}"
        )


# ---------------------------------------------------------------------------
# ATKConnection 扩展 — 添加工厂
# ---------------------------------------------------------------------------

def _patch_connection():
    from atk.connect import session as _s

    _s.ATKConnection.access_builder = lambda self: AccessBuilder(self)
    _s.ATKConnection.access_multi = lambda self: AccessMultiBuilder(self)


_patch_connection()
del _patch_connection
