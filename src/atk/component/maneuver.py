"""
ATK Component 模式 — 机动检测（基于定轨数据）

封装 ``IMnvPODDataBaseDetection``：设置 A/B 两目标轨道状态与
传播参数，检测目标机动的时刻、分量与轨道要素偏差。
"""

from __future__ import annotations

from typing import Any

from atk import exceptions as _ex
from atk.component.session import _ATK, _resolve_propagator_type


class ManeuverDetectionAnalysis:
    """
    ``IMnvPODDataBaseDetection`` 的 Python 风格封装。

    通过 :meth:`ComponentSession.maneuver_detection()
    <atk.component.session.ComponentSession.maneuver_detection>` 创建，
    内部经 ``satellite.GetManeuverDetection().GetPODDataBaseDetection()``
    获取底层对象。

    示例::

        md = session.maneuver_detection('Satellite/Sat1')
        md.set_orbit_propagator('PropagatorTwoBody')
        md.set_object_a_time('1 Jul 2024 00:00:00.000')
        md.set_object_a_j2000(x, y, z, vx, vy, vz)
        md.set_object_b_time('1 Jul 2024 00:00:00.000')
        md.set_object_b_j2000(x, y, z, vx, vy, vz)
        result = md.compute()
    """

    def __init__(self, satellite_obj: Any):
        self._detection = satellite_obj.GetManeuverDetection()
        self._pod = self._detection.GetPODDataBaseDetection()

    @property
    def raw(self) -> Any:
        """底层 ``IMnvPODDataBaseDetection`` SWIG 对象。"""
        return self._pod

    @property
    def tle_database(self) -> "TLEManeuverDetection":
        """
        基于 TLE 数据库的历史机动检测（``IMnvTLEDataBaseDetection`` 封装）。

        Returns
        -------
        TLEManeuverDetection
        """
        return TLEManeuverDetection(self._detection.GetTLEDataBaseDetection())

    # ------------------------------------------------------------------
    # 传播配置
    # ------------------------------------------------------------------

    def set_orbit_propagator(self, propagator: Any) -> "ManeuverDetectionAnalysis":
        """
        设置轨道传播器。

        Parameters
        ----------
        propagator : str or 枚举值
            传播器名（如 ``"PropagatorTwoBody"``）或原始枚举值，
            名字经 ``_resolve_propagator_type`` 解析。
        """
        self._pod.SetOrbitPropagator(_resolve_propagator_type(propagator))
        return self

    def set_step_of_cross_propagation(self, step: float) -> "ManeuverDetectionAnalysis":
        """设置交叉传播步长（秒）。"""
        self._pod.SetStepOfCrossPropagation(step)
        return self

    # ------------------------------------------------------------------
    # A/B 目标状态（J2000 惯性系或 VVLH）
    # ------------------------------------------------------------------

    def set_object_a_time(self, time: str) -> "ManeuverDetectionAnalysis":
        """设置 A 目标状态历元。"""
        self._pod.SetObjectATime(time)
        return self

    def set_object_a_j2000(
        self,
        x: float, y: float, z: float,
        vx: float, vy: float, vz: float,
    ) -> "ManeuverDetectionAnalysis":
        """设置 A 目标 J2000 惯性系状态（位置米、速度米/秒）。"""
        self._pod.SetObjectAJ2000Frame(x, y, z, vx, vy, vz)
        return self

    def set_object_a_vvlh(
        self,
        x: float, y: float, z: float,
        vx: float, vy: float, vz: float,
    ) -> "ManeuverDetectionAnalysis":
        """设置 A 目标 VVLH（轨道坐标系）状态。"""
        self._pod.SetObjectAVVLHFrame(x, y, z, vx, vy, vz)
        return self

    def set_object_b_time(self, time: str) -> "ManeuverDetectionAnalysis":
        """设置 B 目标状态历元。"""
        self._pod.SetObjectBTime(time)
        return self

    def set_object_b_j2000(
        self,
        x: float, y: float, z: float,
        vx: float, vy: float, vz: float,
    ) -> "ManeuverDetectionAnalysis":
        """设置 B 目标 J2000 惯性系状态（位置米、速度米/秒）。"""
        self._pod.SetObjectBJ2000Frame(x, y, z, vx, vy, vz)
        return self

    def set_object_b_vvlh(
        self,
        x: float, y: float, z: float,
        vx: float, vy: float, vz: float,
    ) -> "ManeuverDetectionAnalysis":
        """设置 B 目标 VVLH（轨道坐标系）状态。"""
        self._pod.SetObjectBVVLHFrame(x, y, z, vx, vy, vz)
        return self

    # ------------------------------------------------------------------
    # 计算
    # ------------------------------------------------------------------

    def compute(self) -> dict[str, Any]:
        """
        执行机动检测计算并读取出参。

        .. attention::
           ATK 4.2.0-alpha.1 的 SWIG 封装把 ``strDetectDVutc`` 声明为
           ``std::string &`` 出参，Python 侧无法构造兼容对象，
           导致 ``Compute`` 在该版本下从 Python 调用必然抛
           ``TypeError``（已实测 str/bytes/bytearray 均被拒绝）。
           待 ATK 修正 SWIG typemap 后本方法即可用；
           当前请改用 :class:`TLEManeuverDetection`（基于 TLE 的
           历史机动检测，``Compute`` 出参全为 double，可正常调用）。

        Returns
        -------
        dict[str, Any]
            键：``mnv_res``（0-同目标未机动 / 1-同目标机动 /
            2-相异目标）、``detect_dv_utc``（恒为 None，见上）、
            ``detect_dv``（[Vx, Vy, Vz]）、``sma`` / ``inc`` / ``ecc`` /
            ``raan``（要素偏差）、``time``（UTC 时间列表）、
            ``mahalanobis_dist``（马氏距离列表）。
        """
        n_mnv_res = _ATK.new_int_p()
        d_dv_x = _ATK.new_double_p()
        d_dv_y = _ATK.new_double_p()
        d_dv_z = _ATK.new_double_p()
        d_sma = _ATK.new_double_p()
        d_inc = _ATK.new_double_p()
        d_ecc = _ATK.new_double_p()
        d_raan = _ATK.new_double_p()
        str_time = _ATK.vector_string()
        d_mah_dist = _ATK.vector_double()
        # strDetectDVutc 为 std::string& 出参：ATK 4.2.0-alpha.1 的
        # SWIG 封装不接受任何 Python 类型（str/bytes/bytearray/None
        # 均被拒，模块亦无字符串指针助手），调用必然 TypeError。
        # 转译为带替代方案的明确错误，避免用户面对底层报错。
        try:
            self._pod.Compute(
                n_mnv_res, "",
                d_dv_x, d_dv_y, d_dv_z,
                d_sma, d_inc, d_ecc, d_raan,
                str_time, d_mah_dist,
            )
        except TypeError as exc:
            if "std::string" in str(exc):
                raise _ex.ATKComponentError(
                    "IMnvPODDataBaseDetection.Compute 在 ATK "
                    "4.2.0-alpha.1 的 SWIG 封装下不可调用"
                    "（strDetectDVutc 为 std::string& 出参，Python 无法"
                    "构造兼容实参）。请改用 TLEManeuverDetection"
                    "（.tle_database，基于 TLE 的历史机动检测，可正常"
                    "调用）。"
                ) from exc
            raise

        def _try_read(ptr: Any) -> Any:
            try:
                return ptr.value
            except AttributeError:
                return None

        def _vec_to_list(vec: Any) -> list:
            if vec is None:
                return []
            try:
                return list(vec)
            except TypeError:
                return [vec]

        return {
            "mnv_res": _try_read(n_mnv_res),
            "detect_dv_utc": None,
            "detect_dv": [
                _try_read(d_dv_x), _try_read(d_dv_y), _try_read(d_dv_z),
            ],
            "sma": _try_read(d_sma),
            "inc": _try_read(d_inc),
            "ecc": _try_read(d_ecc),
            "raan": _try_read(d_raan),
            "time": _vec_to_list(str_time),
            "mahalanobis_dist": _vec_to_list(d_mah_dist),
        }


class TLEManeuverDetection:
    """
    ``IMnvTLEDataBaseDetection`` 的 Python 风格封装 — 基于 TLE 的历史机动检测。

    通过 :attr:`ManeuverDetectionAnalysis.tle_database` 获得。
    相比 POD 变体，本类的 ``Compute`` 出参全为 double，
    在 ATK 4.2.0-alpha.1 下可从 Python 正常调用。

    示例::

        tle = session.maneuver_detection('Satellite/Sat1').tle_database
        tle.set_tle_data(r'C:\\data\\tle.txt')
        result = tle.compute('1 Jul 2035 00:00:00.000')
    """

    def __init__(self, detection: Any):
        self._tle = detection

    @property
    def raw(self) -> Any:
        """底层 ``IMnvTLEDataBaseDetection`` SWIG 对象。"""
        return self._tle

    def set_tle_data(self, file_path: str) -> "TLEManeuverDetection":
        """设置 TLE 数据文件路径。"""
        self._tle.SetTLEData(file_path)
        return self

    def set_jud_method_type(self, method_type: Any) -> "TLEManeuverDetection":
        """设置判定方法类型（``EJudMethodType`` 枚举值）。"""
        self._tle.SetJudMethodType(method_type)
        return self

    def set_jud_method_id(self, value: float) -> "TLEManeuverDetection":
        """设置判定方法参数（如马氏距离法的 n-sigma 值）。"""
        self._tle.SetJudMethodID(value)
        return self

    def set_orbital_elem(self, elem_type: Any) -> "TLEManeuverDetection":
        """设置轨道要素类型（枚举值）。"""
        self._tle.SetOrbitalElem(elem_type)
        return self

    def set_est_method_type(self, method_type: Any) -> "TLEManeuverDetection":
        """设置估计方法类型（枚举值）。"""
        self._tle.SetEstMethodType(method_type)
        return self

    def set_step_of_cross_propagation(self, step: float) -> "TLEManeuverDetection":
        """设置交叉传播步长（秒）。"""
        self._tle.SetStepOfCrossPropagation(step)
        return self

    def compute(self, time: str | list[str]) -> dict[str, Any]:
        """
        执行历史机动检测计算。

        Parameters
        ----------
        time : str or list of str
            计算历元（ATK 时间字符串），可传单个或多个。

        Returns
        -------
        dict[str, Any]
            键：``outliers``（异常点数）、``sma_dev``（半长轴偏差）、
            ``radial`` / ``transverse`` / ``normal``（RTN 三轴偏差）。
        """
        # SWIG 签名：Compute(vector<string> times, double* x5)
        times = _ATK.vector_string()
        if isinstance(time, str):
            times.push_back(time)
        else:
            for t in time:
                times.push_back(str(t))
        v_outliers = _ATK.vector_double()
        v_sma_dev = _ATK.vector_double()
        v_radial = _ATK.vector_double()
        v_transverse = _ATK.vector_double()
        v_normal = _ATK.vector_double()
        self._tle.Compute(
            times, v_outliers, v_sma_dev,
            v_radial, v_transverse, v_normal,
        )

        def _vec_to_list(vec: Any) -> list:
            if vec is None:
                return []
            try:
                return list(vec)
            except TypeError:
                return [vec]

        return {
            "outliers": _vec_to_list(v_outliers),
            "sma_dev": _vec_to_list(v_sma_dev),
            "radial": _vec_to_list(v_radial),
            "transverse": _vec_to_list(v_transverse),
            "normal": _vec_to_list(v_normal),
        }
