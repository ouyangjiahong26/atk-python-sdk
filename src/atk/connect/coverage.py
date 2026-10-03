"""
ATK Connect 模式 — 覆盖分析辅助工具

提供流式 API，用于创建覆盖定义、添加资产/地面站，
以及计算访问统计。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from atk import exceptions as _ex
from atk import utils

if TYPE_CHECKING:
    from atk.connect.session import ATKConnection

# Cov_RM 的 <ReportStyle> 合法取值（见帮助文档 Cov_RM Access 页）
COV_RM_STYLES = frozenset({
    "Coverage",
    "Figure Of Merit",
    "Satisfaction",
    "Daily Coverage",
    "Coverage Gaps",
})


# Cov_RM 的 <ReportStyle> 合法取值（见帮助文档 Cov_RM Access 页）
COV_RM_STYLES = frozenset({
    "Coverage",
    "Figure Of Merit",
    "Satisfaction",
    "Daily Coverage",
    "Coverage Gaps",
})

class CoverageBuilder:
    """
    ATK CoverageDefinition 对象的流式构建器。

    通过 ``atk.create_coverage('CoverageName')`` 创建。

    示例::

        cov = atk.create_coverage('GroundCoverage')
        cov.add_asset('*/Satellite/Sat1')
        cov.add_facility('*/Facility/Station1')
        cov.set_grid_resolution(lat_step=1.0, lon_step=1.0)
        stats = cov.compute_stats()
    """

    def __init__(self, conn: "ATKConnection", name: str):
        self._conn = conn
        self._name = utils.validate_name(name)
        self._path = f"*/CoverageDefinition/{self._name}"
        self._assets: list[str] = []
        self._facilities: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    def create(self) -> "CoverageBuilder":
        """在 ATK 中创建覆盖定义对象。"""
        self._conn.send("New", self._path, "")
        return self

    def add_asset(self, sat_path: str) -> "CoverageBuilder":
        """
        添加卫星作为覆盖资产。

        Parameters
        ----------
        sat_path : str
            卫星的 ATK 路径（如 ``"*/Satellite/Sat1"``）。

        Returns
        -------
        self
        """
        sat_path = utils.resolve_path(sat_path)
        self._assets.append(sat_path)
        # ATK format: Cov */CoverageDefinition/{name} Asset {sat_path} Assign
        self._conn.send("Cov", self._path, f" Asset {sat_path} Assign")
        return self

    def add_facility(self, facility_path: str) -> "CoverageBuilder":
        """
        添加地面站作为覆盖目标。

        Parameters
        ----------
        facility_path : str
            地面站的 ATK 路径（如 ``"*/Facility/Station1"``）。

        Returns
        -------
        self
        """
        facility_path = utils.resolve_path(facility_path)
        self._facilities.append(facility_path)
        # ATK format: Cov */CoverageDefinition/{name} Facility {facility_path} Assign
        self._conn.send("Cov", self._path, f" Facility {facility_path} Assign")
        return self

    def set_grid_resolution(
        self,
        lat_step: float = 1.0,
        lon_step: float = 1.0,
        grid_type: str = "LatLon",
    ) -> "CoverageBuilder":
        """
        设置覆盖网格分辨率。

        Parameters
        ----------
        lat_step : float
            纬度步长（度）。
        lon_step : float
            经度步长（度）。
        grid_type : str
            网格类型（如 ``"LatLon"``、``"Custom"``）。

        Returns
        -------
        self
        """
        self._conn.send(
            "Cov",
            self._path,
            f' Grid "{grid_type}" {lat_step} {lon_step}',
        )
        return self

    def set_fom(
        self,
        fom_name: str,
        asset_path: str | None = None,
    ) -> "CoverageBuilder":
        """
        将品质因数 (FOM) 附加到覆盖定义。

        Parameters
        ----------
        fom_name : str
            FOM 名称（如 ``"SimpleAER"``、``"Distance"``）。
        asset_path : str, optional
            FOM 的资产路径。

        Returns
        -------
        self
        """
        if asset_path:
            self._conn.send(
                "Cov",
                self._path,
                f' FOM "{fom_name}" "{utils.resolve_path(asset_path)}"',
            )
        else:
            self._conn.send("Cov", self._path, f' FOM "{fom_name}"')
        return self

    def compute_stats(
        self,
        time_period: str = "*",
    ) -> CoverageStats:
        """
        计算覆盖统计。

        Parameters
        ----------
        time_period : str
            时间段字符串（如 ``"*"`` 表示全部时间）。

        Returns
        -------
        CoverageStats
            包含访问次数、总访问时间等的对象。
        """
        raw = self._conn.send("Cov", self._path, f" Compute {time_period}")
        return CoverageStats(raw)

    # ------------------------------------------------------------------
    # 4.2 新增：覆盖时间区间 / 覆盖计算 / 报告
    # ------------------------------------------------------------------

    def set_interval(self, start: str, stop: str) -> "CoverageBuilder":
        """
        设置对象覆盖性计算的时间区间。

        对应命令 ``Cov <CovDefnObjectPath> Interval "<Start>" "<Stop>"``。

        Parameters
        ----------
        start, stop : str
            时间区间（ATK 时间格式）。

        Returns
        -------
        self
        """
        self._conn.send(
            "Cov", self._path, f' Interval "{start}" "{stop}"'
        )
        return self

    def access_compute(self, start: str, stop: str) -> "CoverageBuilder":
        """
        计算对象覆盖性（清空之前结果后重新计算）。

        对应命令 ``Cov <ObjectPath> Access Compute "<Start>" "<Stop>"``。

        Returns
        -------
        self
        """
        self._conn.send(
            "Cov", self._path, f' Access Compute "{start}" "{stop}"'
        )
        return self

    def access_clear(self) -> "CoverageBuilder":
        """
        清除对象覆盖定义计算。

        对应命令 ``Cov <ObjectPath> Access Clear``。

        Returns
        -------
        self
        """
        self._conn.send("Cov", self._path, " Access Clear")
        return self

    def access_rm(
        self,
        style: str,
        start: str | None = None,
        stop: str | None = None,
    ) -> list[str]:
        """
        获取覆盖性报告。

        对应命令 ``Cov_RM <ObjectPath> Access Compute "<ReportStyle>"
        [{TimeIntervals} | UseObjectTimes]``。

        Parameters
        ----------
        style : str
            报告样式，合法取值见 :data:`COV_RM_STYLES`
            （``"Coverage"``、``"Figure Of Merit"``、``"Satisfaction"``、
            ``"Daily Coverage"``、``"Coverage Gaps"``）。
        start, stop : str, optional
            时间区间；都省略时使用对象自身时间。

        Returns
        -------
        list[str]
            解析后的报告数据行。
        """
        if style not in COV_RM_STYLES:
            raise _ex.ATKValueError(
                f"Unknown Cov_RM style {style!r}. "
                f"Valid styles: {sorted(COV_RM_STYLES)}"
            )
        interval = f'"{start}" "{stop}"' if start else "UseObjectTimes"
        result = self._conn.send(
            "Cov_RM",
            self._path,
            f' Access Compute "{style}" {interval}',
        )
        return utils.result_to_list(result)

    def fom_rm(
        self,
        fom_type: str,
        params: str = "",
    ) -> list[str]:
        """
        返回覆盖品质参数（FOM）计算结果。

        对应命令 ``Cov_RM <CovDefnObjectPath> FOMDefine Definition
        <FOMType> {Parameters}``。

        Parameters
        ----------
        fom_type : str
            FOM 类型（如 ``"CoverageTime"``、``"AccessDuration"``、
            ``"RevisitTime"``、``"NAsset"``）。
        params : str, optional
            FOM 参数（如 ``"Compute Total"``、``"Compute maximum"``）。

        Returns
        -------
        list[str]
            解析后的品质参数数据行。
        """
        param = f"FOMDefine Definition {fom_type} {params}".strip()
        result = self._conn.send("Cov_RM", self._path, f" {param}")
        return utils.result_to_list(result)

    def __repr__(self) -> str:
        return f"<CoverageBuilder name={self._name!r}>"


class CoverageStats:
    """
    解析后的覆盖计算结果。

    Attributes
    ----------
    raw : CMDRESULT
        原始 ATK 结果对象。
    access_count : int
        访问区间数量。
    total_access_time : float
        总访问时间（秒）。
    mean_access_duration : float
        每次访问区间的平均持续时间。
    """

    def __init__(self, raw):
        self.raw = raw
        self._data = utils.result_to_list(raw)
        self._parsed = self._parse()

    def _parse(self) -> dict:
        """将原始 CMDRESULT 数据解析为字典。"""
        data = self._data
        if not data:
            return {}
        # 优先尝试 key=value 格式
        result = {}
        positional = []
        for item in data:
            if "=" in item:
                key, val = item.split("=", 1)
                result[key.strip()] = val.strip()
            else:
                positional.append(item)
        # 如果既没有 key=value 也没有足够的 position 数据，抛出异常
        if not result and len(positional) < 3:
            raise _ex.ATKError(
                f"Unexpected CoverageStats format, expected 'key=value' pairs or "
                f"at least 3 positional values, got: {data}"
            )
        # 如果没有 key=value 对，尝试位置解析
        if not result and len(positional) >= 3:
            # [count, total_time, mean_dur, ...]
            try:
                int(positional[0])
                float(positional[1])
                float(positional[2])
            except (ValueError, TypeError):
                raise _ex.ATKError(
                    f"Unexpected CoverageStats format, expected 'key=value' pairs or "
                    f"at least 3 positional numeric values, got: {data}"
                )
            result["AccessCount"] = positional[0]
            result["TotalAccessTime"] = positional[1]
            result["MeanAccessDuration"] = positional[2] if len(positional) > 2 else "0"
        return result

    @property
    def access_count(self) -> int:
        try:
            return int(self._parsed.get("AccessCount", 0))
        except (ValueError, TypeError) as exc:
            raise _ex.ATKError(f"Failed to parse access_count: {exc}") from exc

    @property
    def total_access_time(self) -> float:
        try:
            return float(self._parsed.get("TotalAccessTime", 0.0))
        except (ValueError, TypeError) as exc:
            raise _ex.ATKError(f"Failed to parse total_access_time: {exc}") from exc

    @property
    def mean_access_duration(self) -> float:
        try:
            return float(self._parsed.get("MeanAccessDuration", 0.0))
        except (ValueError, TypeError) as exc:
            raise _ex.ATKError(f"Failed to parse mean_access_duration: {exc}") from exc

    def __repr__(self) -> str:
        return (
            f"<CoverageStats access_count={self.access_count} "
            f"total_time={self.total_access_time:.2f}s>"
        )


class CoverageMultiBuilder:
    """
    Connect 模式下批量覆盖性分析（CovMulti）的"先配置后计算"框架。

    通过 ``atk.coverage_multi()`` 创建。

    工作流：:meth:`add_assets` 指定覆盖资产 → :meth:`add_objects`
    指定访问对象 → :meth:`compute` 执行批量计算 →
    :meth:`multi_fom_rm` 获取品质参数。

    示例::

        multi = atk.coverage_multi()
        multi.add_assets('*/Satellite/Sat1/Sensor/Sensor1')
        multi.add_objects('*/Facility/Target1', '*/Facility/Target2')
        multi.compute('26 Sep 2035 12:00:00.00', '28 Sep 2035 12:00:00.00')
        rows = multi.multi_fom_rm('RevisitTime', 'Compute maximum')
    """

    def __init__(self, conn: "ATKConnection"):
        self._conn = conn

    def add_assets(self, *paths: str) -> "CoverageMultiBuilder":
        """
        覆盖性选择多个目标对象（资产）。

        对应命令 ``CovMulti / Assets <AssetObjectPath>...``。

        Parameters
        ----------
        *paths : str
            资产对象路径，可传多个。

        Returns
        -------
        self
        """
        if not paths:
            raise _ex.ATKValueError("add_assets requires at least one path")
        joined = " ".join(utils.resolve_path(p) for p in paths)
        self._conn.send("CovMulti", "/", f" Assets {joined}")
        return self

    def add_objects(self, *paths: str) -> "CoverageMultiBuilder":
        """
        覆盖性选择多个访问对象。

        对应命令 ``CovMulti / Objects <CovObjectPath>...``。

        Returns
        -------
        self
        """
        if not paths:
            raise _ex.ATKValueError("add_objects requires at least one path")
        joined = " ".join(utils.resolve_path(p) for p in paths)
        self._conn.send("CovMulti", "/", f" Objects {joined}")
        return self

    def compute(self, start: str, stop: str) -> Any:
        """
        清空并计算对象覆盖性。

        对应命令 ``CovMulti / Access Compute "<Start>" "<Stop>"``。

        Returns
        -------
        原始 ATK 响应。
        """
        return self._conn.send(
            "CovMulti", "/", f' Access Compute "{start}" "{stop}"'
        )

    def multi_fom_rm(
        self,
        fom_type: str,
        params: str = "",
    ) -> list[str]:
        """
        返回批量覆盖品质参数。

        对应命令 ``CovMulti_RM / MultiFOMDefine Definition
        <FOMType> {Parameters}``。

        Parameters
        ----------
        fom_type : str
            FOM 类型（如 ``"RevisitTime"``、``"CoverageTime"``）。
        params : str, optional
            FOM 参数（如 ``"Compute maximum"``）。

        Returns
        -------
        list[str]
            解析后的品质参数数据行。
        """
        param = f"MultiFOMDefine Definition {fom_type} {params}".strip()
        result = self._conn.send("CovMulti_RM", "/", f" {param}")
        return utils.result_to_list(result)

    def __repr__(self) -> str:
        return "<CoverageMultiBuilder>"


# ---------------------------------------------------------------------------
# 将 create_coverage() 添加到 ATKConnection
# ---------------------------------------------------------------------------

def _patch_connection():
    from atk.connect import session as _s

    def create_coverage(self, name: str) -> CoverageBuilder:
        """创建新的 CoverageDefinition 并返回 CoverageBuilder。"""
        builder = CoverageBuilder(self, name)
        builder.create()
        return builder

    _s.ATKConnection.create_coverage = create_coverage
    _s.ATKConnection.coverage_multi = lambda self: CoverageMultiBuilder(self)


_patch_connection()
del _patch_connection
