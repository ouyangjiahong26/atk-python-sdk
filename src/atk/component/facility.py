"""
ATK Component 模式 — 地面站与传感器构建器

用 Python 风格的流式 API 封装 ``IFacility``、``IPosition`` 和 ``ISensor``，
依据 ATK 二次开发 COMPONENT 模式接口文档（地面站类、敏感器类）实现。
"""

from __future__ import annotations

from typing import Any

from atk import exceptions as _ex
from atk.component.session import _get_enum


# 欧拉旋转序列整数/字符串 → SWIG 枚举名（EEulerOrientationSequence）
_EULER_SEQUENCES = {
    121: "e121", 123: "e123", 131: "e131", 132: "e132",
    212: "e212", 213: "e213", 231: "e231", 232: "e232",
    312: "e312", 313: "e313", 321: "e321", 323: "e323",
}


def _resolve_euler_sequence(sequence: Any) -> Any:
    """
    将欧拉旋转序列转换为 SWIG 枚举值。

    接受整数（如 ``123``）、字符串（如 ``"123"``）或原始枚举值。
    """
    if isinstance(sequence, str) and sequence.isdigit():
        sequence = int(sequence)
    if isinstance(sequence, int):
        enum_name = _EULER_SEQUENCES.get(sequence)
        if enum_name is None:
            raise _ex.ATKValueError(
                f"Unknown euler sequence {sequence}. "
                f"Valid sequences: {sorted(_EULER_SEQUENCES)}"
            )
        return _get_enum(enum_name)
    return sequence


class FacilityBuilder:
    """
    ATK Component 模式下 ``IFacility`` 的 Python 风格封装。

    通过 :meth:`ScenarioBuilder.create_facility() <atk.component.scenario.ScenarioBuilder.create_facility>`
    创建，或直接包装已有的 ``IFacility`` SWIG 对象。

    示例::

        facility = scenario.create_facility('Beijing')
        facility.set_position_geodetic(lat=39.9, lon=116.4, alt=50)
        sensor = facility.create_sensor('Sensor1')
        sensor.set_pattern_simple_conic(cone_angle=40)
    """

    def __init__(self, facility: Any):
        self._facility = facility

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._facility.GetInstanceName()

    @property
    def path(self) -> str:
        return self._facility.GetPath()

    @property
    def facility(self) -> Any:
        """返回原始 ``IFacility`` SWIG 对象。"""
        return self._facility

    # ------------------------------------------------------------------
    # 位置
    # ------------------------------------------------------------------

    def set_position_geodetic(
        self, lat: float, lon: float, alt: float = 0.0
    ) -> "FacilityBuilder":
        """
        以大地坐标设置地面站位置。

        Parameters
        ----------
        lat : float
            纬度（度，-90 ~ +90）。
        lon : float
            经度（度，-180 ~ +180）。
        alt : float
            椭球高（米），默认 0.0。
        """
        if not (-90.0 <= lat <= 90.0):
            raise _ex.ATKValueError(f"lat must be in [-90, 90], got {lat}")
        if not (-180.0 <= lon <= 180.0):
            raise _ex.ATKValueError(f"lon must be in [-180, 180], got {lon}")
        self._facility.GetPosition().AssignGeodetic(lat, lon, alt)
        return self

    def set_position_cartesian(
        self, x: float, y: float, z: float
    ) -> "FacilityBuilder":
        """
        以固定坐标系笛卡尔坐标设置地面站位置。

        Parameters
        ----------
        x, y, z : float
            笛卡尔坐标分量（米）。
        """
        self._facility.GetPosition().AssignCartesian(x, y, z)
        return self

    def get_position_geodetic(self) -> tuple[float, float, float]:
        """
        返回地面站的大地坐标。

        Returns
        -------
        (lat, lon, alt) : tuple[float, float, float]
            纬度、经度（度）与椭球高（米）。
        """
        geodetic = self._facility.GetPosition().ConvertTo(
            _get_enum("eGeodetic")
        )
        return (geodetic.GetLat(), geodetic.GetLon(), geodetic.GetAlt())

    def get_position_cartesian(self) -> tuple[float, float, float]:
        """
        返回地面站的笛卡尔坐标。

        Returns
        -------
        (x, y, z) : tuple[float, float, float]
            笛卡尔坐标分量（米）。
        """
        cartesian = self._facility.GetPosition().ConvertTo(
            _get_enum("eCartesian")
        )
        return (cartesian.GetX(), cartesian.GetY(), cartesian.GetZ())

    # ------------------------------------------------------------------
    # 显示
    # ------------------------------------------------------------------

    def set_color(self, color: int) -> "FacilityBuilder":
        """
        设置二维显示颜色。

        Parameters
        ----------
        color : int
            颜色值，例如绿色为 -65280。
        """
        self._facility.GetGraphics().SetColor(color)
        return self

    def get_color(self) -> int:
        """返回二维显示颜色。"""
        return self._facility.GetGraphics().GetColor()

    # ------------------------------------------------------------------
    # 传感器
    # ------------------------------------------------------------------

    def create_sensor(self, name: str) -> "SensorBuilder":
        """
        在此地面站下创建传感器（敏感器）。

        Parameters
        ----------
        name : str
            传感器名称。

        Returns
        -------
        SensorBuilder
        """
        children = self._facility.GetChildren()
        sensor = children.New(_get_enum("eSensor"), name)
        return SensorBuilder(sensor)

    def __repr__(self) -> str:
        return f"<FacilityBuilder name={self.name!r}>"


class SensorBuilder:
    """
    ATK Component 模式下 ``ISensor`` 的 Python 风格封装。

    通过 :meth:`FacilityBuilder.create_sensor()` 创建，
    或直接包装挂在任意对象（地面站、卫星等）下的 ``ISensor``。

    示例::

        sensor = facility.create_sensor('Sensor1')
        sensor.set_pattern_simple_conic(cone_angle=40)
        sensor.point_fixed_euler(sequence=123, a=180, b=0, c=0)
    """

    def __init__(self, sensor: Any):
        self._sensor = sensor

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._sensor.GetInstanceName()

    @property
    def path(self) -> str:
        return self._sensor.GetPath()

    @property
    def sensor(self) -> Any:
        """返回原始 ``ISensor`` SWIG 对象。"""
        return self._sensor

    # ------------------------------------------------------------------
    # 视场形状
    # ------------------------------------------------------------------

    def set_pattern_simple_conic(
        self, cone_angle: float, angular_resolution: float = 0.1
    ) -> "SensorBuilder":
        """
        设置圆锥视场。

        Parameters
        ----------
        cone_angle : float
            半锥角（度）。
        angular_resolution : float
            视场边缘点之间的角分离（度），默认 0.1。
        """
        if not (0.0 < cone_angle < 90.0):
            raise _ex.ATKValueError(
                f"cone_angle must be in (0, 90) degrees, got {cone_angle}"
            )
        self._sensor.GetCommonTasks().SetPatternSimpleConic(
            cone_angle, angular_resolution
        )
        return self

    def set_pattern_rectangular(
        self, vertical_half_angle: float, horizontal_half_angle: float
    ) -> "SensorBuilder":
        """
        设置矩形视场。

        Parameters
        ----------
        vertical_half_angle : float
            垂直半张角（度）。
        horizontal_half_angle : float
            水平半张角（度）。
        """
        self._sensor.GetCommonTasks().SetPatternRectangular(
            vertical_half_angle, horizontal_half_angle
        )
        return self

    # ------------------------------------------------------------------
    # 指向
    # ------------------------------------------------------------------

    def point_fixed_euler(
        self, sequence: Any, a: float, b: float, c: float
    ) -> "SensorBuilder":
        """
        以固定欧拉角设置传感器指向。

        Parameters
        ----------
        sequence : int | str
            欧拉旋转序列（如 ``123`` 或 ``"313"``）。
        a, b, c : float
            欧拉角分量（度）。
        """
        enum = _resolve_euler_sequence(sequence)
        self._sensor.GetCommonTasks().SetPointingFixedEuler(enum, a, b, c)
        return self

    def point_fixed_quaternion(
        self, x: float, y: float, z: float, s: float
    ) -> "SensorBuilder":
        """
        以固定四元数设置传感器指向。

        Parameters
        ----------
        x, y, z, s : float
            四元数分量。
        """
        self._sensor.GetCommonTasks().SetPointingFixedQuat(x, y, z, s)
        return self

    def __repr__(self) -> str:
        return f"<SensorBuilder name={self.name!r}>"
