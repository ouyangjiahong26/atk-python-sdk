"""
atk.component.facility 的单元测试 — FacilityBuilder / SensorBuilder。

使用 unittest.mock 模拟 IFacility / ISensor SWIG 对象。
"""

import pytest
from unittest.mock import MagicMock, patch

from atk import exceptions as atk_exc


def _reload_component_modules(mock_atk):
    """patch 模块定位函数并重载 session，返回可用的模块引用。"""
    import importlib
    with patch("atk.component.session._find_component_module", return_value=mock_atk):
        import atk.component.session
        importlib.reload(atk.component.session)
        import atk.component.facility
        importlib.reload(atk.component.facility)
        import atk.component.scenario
        importlib.reload(atk.component.scenario)
    import atk.component.session as session_mod
    import atk.component.facility as facility_mod
    import atk.component.scenario as scenario_mod
    return session_mod, facility_mod, scenario_mod


def _make_mock_atk():
    mock_atk = MagicMock()
    mock_atk.eFacility = "eFacility"
    mock_atk.eSensor = "eSensor"
    mock_atk.eGeodetic = "eGeodetic"
    mock_atk.eCartesian = "eCartesian"
    mock_atk.e123 = "e123"
    mock_atk.e313 = "e313"
    return mock_atk


class TestFacilityBuilderPosition:
    """FacilityBuilder 位置设置的测试。"""

    def test_set_position_geodetic_calls_assign_geodetic(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_facility = MagicMock()
        builder = facility_mod.FacilityBuilder(mock_facility)
        builder.set_position_geodetic(lat=39.9, lon=116.4, alt=50)

        mock_facility.GetPosition.return_value.AssignGeodetic.assert_called_once_with(
            39.9, 116.4, 50
        )

    @pytest.mark.parametrize("lat,lon", [(91, 0), (-91, 0), (0, 181), (0, -181)])
    def test_set_position_geodetic_rejects_out_of_range(self, lat, lon):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        builder = facility_mod.FacilityBuilder(MagicMock())
        with pytest.raises(atk_exc.ATKValueError):
            builder.set_position_geodetic(lat=lat, lon=lon)

    def test_set_position_cartesian_calls_assign_cartesian(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_facility = MagicMock()
        builder = facility_mod.FacilityBuilder(mock_facility)
        builder.set_position_cartesian(-2127, 5266, 3000)

        mock_facility.GetPosition.return_value.AssignCartesian.assert_called_once_with(
            -2127, 5266, 3000
        )

    def test_get_position_geodetic_converts_and_reads(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_geodetic = MagicMock()
        mock_geodetic.GetLat.return_value = 28.0
        mock_geodetic.GetLon.return_value = 112.0
        mock_geodetic.GetAlt.return_value = 50.0

        mock_position = MagicMock()
        mock_position.ConvertTo.side_effect = (
            lambda etype: mock_geodetic if etype == "eGeodetic" else MagicMock()
        )
        mock_facility = MagicMock()
        mock_facility.GetPosition.return_value = mock_position

        builder = facility_mod.FacilityBuilder(mock_facility)
        assert builder.get_position_geodetic() == (28.0, 112.0, 50.0)
        mock_position.ConvertTo.assert_called_once_with("eGeodetic")

    def test_get_position_cartesian_converts_and_reads(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_cartesian = MagicMock()
        mock_cartesian.GetX.return_value = -2127.0
        mock_cartesian.GetY.return_value = 5266.0
        mock_cartesian.GetZ.return_value = 3000.0

        mock_position = MagicMock()
        mock_position.ConvertTo.side_effect = (
            lambda etype: mock_cartesian if etype == "eCartesian" else MagicMock()
        )
        mock_facility = MagicMock()
        mock_facility.GetPosition.return_value = mock_position

        builder = facility_mod.FacilityBuilder(mock_facility)
        assert builder.get_position_cartesian() == (-2127.0, 5266.0, 3000.0)


class TestFacilityBuilderSensor:
    """FacilityBuilder 传感器创建的测试。"""

    def test_create_sensor_returns_sensor_builder(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_sensor = MagicMock()
        mock_children = MagicMock()
        mock_children.New.return_value = mock_sensor
        mock_facility = MagicMock()
        mock_facility.GetChildren.return_value = mock_children

        builder = facility_mod.FacilityBuilder(mock_facility)
        sensor = builder.create_sensor("Sensor1")

        mock_children.New.assert_called_once_with("eSensor", "Sensor1")
        assert isinstance(sensor, facility_mod.SensorBuilder)
        assert sensor.sensor is mock_sensor

    def test_set_color_calls_graphics(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_facility = MagicMock()
        builder = facility_mod.FacilityBuilder(mock_facility)
        builder.set_color(-65280)

        mock_facility.GetGraphics.return_value.SetColor.assert_called_once_with(-65280)


class TestSensorBuilder:
    """SensorBuilder 视场与指向的测试。"""

    def test_set_pattern_simple_conic(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_sensor = MagicMock()
        builder = facility_mod.SensorBuilder(mock_sensor)
        builder.set_pattern_simple_conic(cone_angle=40, angular_resolution=0.5)

        mock_sensor.GetCommonTasks.return_value.SetPatternSimpleConic.assert_called_once_with(
            40, 0.5
        )

    def test_set_pattern_simple_conic_rejects_bad_angle(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        builder = facility_mod.SensorBuilder(MagicMock())
        with pytest.raises(atk_exc.ATKValueError):
            builder.set_pattern_simple_conic(cone_angle=120)

    def test_set_pattern_rectangular(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_sensor = MagicMock()
        builder = facility_mod.SensorBuilder(mock_sensor)
        builder.set_pattern_rectangular(
            vertical_half_angle=46, horizontal_half_angle=47
        )

        mock_sensor.GetCommonTasks.return_value.SetPatternRectangular.assert_called_once_with(
            46, 47
        )

    def test_point_fixed_euler_resolves_sequence_enum(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_sensor = MagicMock()
        builder = facility_mod.SensorBuilder(mock_sensor)
        builder.point_fixed_euler(sequence=123, a=11.31, b=8.97, c=11.31)

        mock_sensor.GetCommonTasks.return_value.SetPointingFixedEuler.assert_called_once_with(
            "e123", 11.31, 8.97, 11.31
        )

    def test_point_fixed_euler_accepts_string_sequence(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_sensor = MagicMock()
        builder = facility_mod.SensorBuilder(mock_sensor)
        builder.point_fixed_euler(sequence="313", a=1, b=2, c=3)

        mock_sensor.GetCommonTasks.return_value.SetPointingFixedEuler.assert_called_once_with(
            "e313", 1, 2, 3
        )

    def test_point_fixed_euler_rejects_unknown_sequence(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        builder = facility_mod.SensorBuilder(MagicMock())
        with pytest.raises(atk_exc.ATKValueError, match="euler sequence"):
            builder.point_fixed_euler(sequence=999, a=1, b=2, c=3)

    def test_point_fixed_quaternion(self):
        mock_atk = _make_mock_atk()
        _, facility_mod, _ = _reload_component_modules(mock_atk)

        mock_sensor = MagicMock()
        builder = facility_mod.SensorBuilder(mock_sensor)
        builder.point_fixed_quaternion(x=0.2, y=0.08, z=0.0, s=1.0)

        mock_sensor.GetCommonTasks.return_value.SetPointingFixedQuat.assert_called_once_with(
            0.2, 0.08, 0.0, 1.0
        )


class TestScenarioCreateFacility:
    """ScenarioBuilder.create_facility() 的测试。"""

    def test_create_facility_calls_new_on_children(self):
        mock_atk = _make_mock_atk()
        _, _, scenario_mod = _reload_component_modules(mock_atk)

        mock_session = MagicMock()
        mock_scenario = MagicMock()
        mock_children = MagicMock()
        mock_facility = MagicMock()
        mock_scenario.GetChildren.return_value = mock_children
        mock_children.New.return_value = mock_facility

        builder = scenario_mod.ScenarioBuilder(mock_session, mock_scenario)
        result = builder.create_facility("Beijing")

        mock_children.New.assert_called_once_with("eFacility", "Beijing")
        assert result is mock_facility
