"""
ATK Component 模式 — 可见性（Access）分析

封装 ``IAtkAccess`` 与 ``IAccessConstraintCollection``：
一对一可见性计算、可见区间获取、可见性报告输出与约束管理。
"""

from __future__ import annotations

from typing import Any

from atk import exceptions as _ex
from atk.component.session import _ATK, _get_enum


def _available_report_keys() -> list[str]:
    """扫描模块属性，列出全部 eACCESS/eNACCESS 报告枚举对应的 key。"""
    keys = []
    for name in dir(_ATK):
        if (name.startswith("eACCESS_") or name.startswith("eNACCESS_")) \
                and name.endswith("_REP"):
            keys.append(name[1:-4])
    return sorted(keys)


def _resolve_report_enum(report_type: str) -> Any:
    """
    将报告类型字符串解析为 eACCESS/eNACCESS 枚举值。

    接受大写下划线形式（如 ``"AER_SUMMARY"`` → ``eACCESS_AER_SUMMARY_REP``、
    ``"NACCESS_INTRVL"`` → ``eNACCESS_INTRVL_REP``）。
    """
    norm = report_type.strip().upper()
    for name in (f"eACCESS_{norm}_REP", f"e{norm}_REP"):
        if hasattr(_ATK, name):
            return _get_enum(name)
    raise _ex.ATKValueError(
        f"Unknown access report type {report_type!r}. "
        f"Valid types: {_available_report_keys()}"
    )


class AccessCalculator:
    """
    ``IAtkAccess`` 的 Python 风格封装 — 单对象对的可见性分析。

    通过 :meth:`ComponentSession.access_calculator()
    <atk.component.session.ComponentSession.access_calculator>` 创建，
    或直接包装 ``obj.GetAccess(target_path)`` 的返回值。

    示例::

        access = session.access_calculator('Satellite/Sat1',
                                           'Facility/Fac1')
        access.set_time_period('1 Jul 2024 00:00:00.000',
                               '2 Jul 2024 00:00:00.000')
        access.compute()
        intervals = access.intervals()
    """

    def __init__(self, obj: Any, target_path: str):
        self._obj = obj
        self._target_path = target_path
        self._access = obj.GetAccess(target_path)

    @property
    def raw(self) -> Any:
        """底层 ``IAtkAccess`` SWIG 对象。"""
        return self._access

    # ------------------------------------------------------------------
    # 计算配置
    # ------------------------------------------------------------------

    def set_time_period(self, start: str, stop: str) -> "AccessCalculator":
        """设置可见性计算时间区间（ATK 时间字符串）。"""
        self._access.SetAccessTimePeriod(start, stop)
        return self

    def set_time_step(self, step: float) -> "AccessCalculator":
        """设置计算时间步长（秒）。"""
        self._access.SetTimeStep(step)
        return self

    def set_use_ltd(self, flag: bool) -> "AccessCalculator":
        """设置是否使用光行差（LTD）修正。"""
        self._access.SetUseLTD(flag)
        return self

    # ------------------------------------------------------------------
    # 计算与结果
    # ------------------------------------------------------------------

    def compute(self) -> "AccessCalculator":
        """执行可见性计算。"""
        self._access.ComputeAccess()
        return self

    def intervals(self) -> list[Any]:
        """返回计算得到的可见区间（尽力归一化为 list）。"""
        result = self._access.ComputedAccessIntervalTimes()
        if result is None:
            return []
        try:
            return list(result)
        except TypeError:
            return [result]

    def output_report(self, report_type: str) -> Any:
        """
        输出可见性报告。

        Parameters
        ----------
        report_type : str
            大写下划线形式的报告类型，如 ``"INTRVL"``、``"AER"``、
            ``"AER_SUMMARY"``、``"RANGE_RATE"``、``"NACCESS_INTRVL"``；
            合法集合即 ATKComponentPythonModule 中全部
            ``eACCESS_*_REP`` / ``eNACCESS_*_REP`` 枚举。

        Returns
        -------
        底层报告输出（通常为输出文件路径或状态值）。
        """
        return self._access.OutputAccessReport(
            _resolve_report_enum(report_type)
        )

    def clear(self) -> "AccessCalculator":
        """清除可见性计算结果。"""
        self._access.ClearAccess()
        return self

    def remove(self) -> "AccessCalculator":
        """移除此可见性分析对象。"""
        self._access.RemoveAccess()
        return self

    # ------------------------------------------------------------------
    # 约束
    # ------------------------------------------------------------------

    def constraints(self) -> "AccessConstraints":
        """
        返回该对象的可见性约束管理器。

        Returns
        -------
        AccessConstraints
        """
        return AccessConstraints(self._obj.GetAccessConstraints())


class AccessConstraints:
    """
    ``IAccessConstraintCollection`` 的轻封装 — 按名称管理可见性约束。
    """

    def __init__(self, collection: Any):
        self._collection = collection

    def add(self, name: str) -> "AccessConstraints":
        """按名称激活约束（如 ``"LineOfSight"``）。"""
        self._collection.AddNamedConstraint(name)
        return self

    def remove(self, name: str) -> "AccessConstraints":
        """按名称取消约束。"""
        self._collection.RemoveNamedConstraint(name)
        return self

    def available(self) -> list[Any]:
        """返回可用约束列表（尽力归一化为 list）。"""
        result = self._collection.AvailableConstraints()
        if result is None:
            return []
        try:
            return list(result)
        except TypeError:
            return [result]

    def count(self) -> int:
        """返回当前激活的约束数量。"""
        return self._collection.GetCount()

    def is_active(self, name: str) -> bool:
        """查询命名约束是否激活。"""
        return bool(self._collection.IsNamedConstraintActive(name))
