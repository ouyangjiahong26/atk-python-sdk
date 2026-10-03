"""
ATK Component 模式 — 接近分析（CAT）

封装 ``ICat`` / ``ICATAdvance``：设置主/次目标（场景对象或 TLE 数据库）、
时间窗、距离门限并计算接近事件，读取计算结果。
"""

from __future__ import annotations

from typing import Any, Iterable

from atk.component.session import _ATK


def _as_vector_string(values: Iterable[str]) -> Any:
    """构造并填充 SWIG ``vector_string``。"""
    vec = _ATK.vector_string()
    for v in values:
        vec.push_back(str(v))
    return vec


def _to_list(vec: Any) -> list:
    """SWIG 向量 → Python list（尽力归一化）。"""
    if vec is None:
        return []
    try:
        return list(vec)
    except TypeError:
        return [vec]

class CatAnalysis:
    """
    ``ICat`` 的 Python 风格封装 — 接近分析（Closest Approach Tool）。

    通过 :meth:`ComponentSession.cat_analysis()
    <atk.component.session.ComponentSession.cat_analysis>` 创建。

    示例::

        cat = session.cat_analysis()
        cat.set_primary_satellites(
            ['Satellite/Sat1'], tle_file_path, exclude_ssc=['25544'])
        cat.set_time_period('1 Jul 2024 00:00:00.000',
                            '2 Jul 2024 00:00:00.000')
        cat.compute()
        results = cat.get_results()
    """

    def __init__(self, session: Any):
        self._session = session
        self._cat = session.root.GetCat()

    @property
    def raw(self) -> Any:
        """底层 ``ICat`` SWIG 对象。"""
        return self._cat

    # ------------------------------------------------------------------
    # 目标设置（均需提供 TLE 数据库文件路径）
    # ------------------------------------------------------------------

    def set_primary_satellites(
        self,
        satellite_names: Iterable[str],
        tle_file_path: str,
        exclude_ssc: Iterable[str] = (),
    ) -> "CatAnalysis":
        """
        以场景卫星为主目标，TLE 数据库对象为次目标。

        Parameters
        ----------
        satellite_names : iterable of str
            场景内卫星名称列表。
        tle_file_path : str
            TLE 数据文件路径。
        exclude_ssc : iterable of str, optional
            排除的 SSC 编号列表。
        """
        self._cat.SetSatelliteFromScenario(
            _as_vector_string(satellite_names),
            tle_file_path,
            _as_vector_string(exclude_ssc),
        )
        return self

    def set_missiles_or_launch_vehicles(
        self,
        object_names: Iterable[str],
        tle_file_path: str,
        exclude_ssc: Iterable[str] = (),
    ) -> "CatAnalysis":
        """以场景导弹/火箭为主目标，TLE 数据库对象为次目标。"""
        self._cat.SetMissOrLauVehFromScenario(
            _as_vector_string(object_names),
            tle_file_path,
            _as_vector_string(exclude_ssc),
        )
        return self

    def set_ssc_num_objects(
        self,
        ssc_numbers: Iterable[str],
        tle_file_path: str,
        exclude_ssc: Iterable[str] = (),
    ) -> "CatAnalysis":
        """以指定 SSC 编号的库文件目标为主目标。"""
        self._cat.SetInputSSCNumObject(
            _as_vector_string(ssc_numbers),
            tle_file_path,
            _as_vector_string(exclude_ssc),
        )
        return self

    def set_all_tle_objects(
        self,
        tle_file_path: str,
        exclude_ssc: Iterable[str] = (),
    ) -> "CatAnalysis":
        """遍历 TLE 数据库全部目标进行计算。"""
        self._cat.SetAllTLEObjects(
            tle_file_path,
            _as_vector_string(exclude_ssc),
        )
        return self

    # ------------------------------------------------------------------
    # 时间与门限
    # ------------------------------------------------------------------

    def use_scenario_time(self, flag: bool) -> "CatAnalysis":
        """是否使用场景时间区间。"""
        self._cat.SetUseScenarioTimePeriod(flag)
        return self

    def set_time_period(self, start: str, stop: str) -> "CatAnalysis":
        """设置仿真分析时间窗（ATK 时间字符串）。"""
        self._cat.SetTimePeriod(start, stop)
        return self

    def set_max_range(self, meters: float) -> "CatAnalysis":
        """设置相对距离门限（米）。"""
        self._cat.SetMaxRange(meters)
        return self

    # ------------------------------------------------------------------
    # 计算与结果
    # ------------------------------------------------------------------

    def compute(self) -> "CatAnalysis":
        """执行接近分析计算。"""
        self._cat.Compute()
        return self

    def get_results(self) -> dict[str, list]:
        """
        读取计算结果。

        内部构造 12 个 SWIG 出参向量（主/次目标 SSC、等效距离、相对
        距离、RTN 三轴距离、接近夹角、相对速度、TCA 及起止时刻），
        调用 ``GetResults`` 后归一化为 dict of list。

        Returns
        -------
        dict[str, list]
            键：``primary_ssc`` / ``secondary_ssc`` / ``equiv_dist`` /
            ``miss_distance`` / ``miss_dist_r`` / ``miss_dist_t`` /
            ``miss_dist_n`` / ``angle_ca`` / ``relative_velocity`` /
            ``tca`` / ``tin`` / ``tout``；无结果时各项为空列表。
        """
        primary_ssc = _ATK.vector_string()
        secondary_ssc = _ATK.vector_string()
        equiv_dist = _ATK.vector_double()
        miss_distance = _ATK.vector_double()
        miss_dist_r = _ATK.vector_double()
        miss_dist_t = _ATK.vector_double()
        miss_dist_n = _ATK.vector_double()
        angle_ca = _ATK.vector_double()
        relative_velocity = _ATK.vector_double()
        tca = _ATK.vector_string()
        tin = _ATK.vector_string()
        tout = _ATK.vector_string()
        self._cat.GetResults(
            primary_ssc, secondary_ssc,
            equiv_dist, miss_distance, miss_dist_r, miss_dist_t, miss_dist_n,
            angle_ca, relative_velocity, tca, tin, tout,
        )
        return {
            "primary_ssc": _to_list(primary_ssc),
            "secondary_ssc": _to_list(secondary_ssc),
            "equiv_dist": _to_list(equiv_dist),
            "miss_distance": _to_list(miss_distance),
            "miss_dist_r": _to_list(miss_dist_r),
            "miss_dist_t": _to_list(miss_dist_t),
            "miss_dist_n": _to_list(miss_dist_n),
            "angle_ca": _to_list(angle_ca),
            "relative_velocity": _to_list(relative_velocity),
            "tca": _to_list(tca),
            "tin": _to_list(tin),
            "tout": _to_list(tout),
        }

    # ------------------------------------------------------------------
    # 高级参数
    # ------------------------------------------------------------------

    @property
    def advance(self) -> "CatAdvanceConfig":
        """高级参数配置（``ICATAdvance`` 的流式封装）。"""
        return CatAdvanceConfig(self._cat.GetAdvance())


class CatAdvanceConfig:
    """
    ``ICATAdvance`` 的流式封装 — 接近分析高级参数（滤波器、门限等）。
    """

    def __init__(self, advance: Any):
        self._advance = advance

    def set_method(self, method_type: Any) -> "CatAdvanceConfig":
        """设置分析方法（``eCatMethodType`` 枚举值）。"""
        self._advance.SetMethod(method_type)
        return self

    def set_date_filter(self, use: bool, out_of_date: float | None = None) -> "CatAdvanceConfig":
        """设置历元过期滤波器。"""
        self._advance.SetUseDateFilter(use)
        if out_of_date is not None:
            self._advance.SetOutOfDate(out_of_date)
        return self

    def set_peri_apo_filter(self, use: bool, peri_apo_dist: float | None = None) -> "CatAdvanceConfig":
        """设置远/近地点滤波器。"""
        self._advance.SetUsePeriApoFilter(use)
        if peri_apo_dist is not None:
            self._advance.SetPeriApoDist(peri_apo_dist)
        return self

    def set_path_filter(self, use: bool, orbit_path: float | None = None) -> "CatAdvanceConfig":
        """设置轨道路径滤波器。"""
        self._advance.SetUsePathFilter(use)
        if orbit_path is not None:
            self._advance.SetOrbitPath(orbit_path)
        return self

    def set_time_filter(self, use: bool, time_dist: float | None = None) -> "CatAdvanceConfig":
        """设置时间滤波器。"""
        self._advance.SetUseTimeFilter(use)
        if time_dist is not None:
            self._advance.SetTimeDist(time_dist)
        return self

    def set_simulation_step(self, step: float) -> "CatAdvanceConfig":
        """设置仿真步长。"""
        self._advance.SetSimulationStep(step)
        return self

    def set_yellow_threshold(self, value: float) -> "CatAdvanceConfig":
        """设置黄色预警距离门限（米）。"""
        self._advance.SetYellowDistThreshold(value)
        return self

    def set_red_threshold(self, value: float) -> "CatAdvanceConfig":
        """设置红色预警距离门限（米）。"""
        self._advance.SetRedDistThreshold(value)
        return self

    def set_equival_factor(self, value: float) -> "CatAdvanceConfig":
        """设置椭球等效比例因子。"""
        self._advance.SetEquivalFactor(value)
        return self
