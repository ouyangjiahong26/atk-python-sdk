"""
atk.connect.access 的单元测试 — AccessBuilder / AccessMultiBuilder。
"""

import pytest

from atk import exceptions as atk_exc
from atk.connect.access import AccessBuilder, AccessMultiBuilder


class TestAccessBuilder:
    """Access / AER / Access_RM 命令封装的测试。"""

    def test_compute_sends_access_with_time_period(self, mock_conn):
        builder = AccessBuilder(mock_conn)
        builder.compute(
            "*/Satellite/Sat1", "*/Facility/Fac1",
            "14 Mar 2024 00:00:00.000", "15 Mar 2024 00:00:00.000",
        )
        assert mock_conn.calls[-1] == (
            "Access", "*/Satellite/Sat1",
            '*/Facility/Fac1 TimePeriod "14 Mar 2024 00:00:00.000" '
            '"15 Mar 2024 00:00:00.000"',
        )

    def test_compute_resolves_truncated_paths(self, mock_conn):
        AccessBuilder(mock_conn).compute(
            "Satellite/Sat1", "Facility/Fac1", "s", "e"
        )
        assert mock_conn.calls[-1] == (
            "Access", "*/Satellite/Sat1",
            '*/Facility/Fac1 TimePeriod "s" "e"',
        )

    def test_aer_sends_aer_command(self, mock_conn):
        AccessBuilder(mock_conn).aer(
            "Satellite/Sat1", "Satellite/Sat2", "s", "e"
        )
        assert mock_conn.calls[-1][0] == "AER"

    def test_access_rm_with_interval(self, mock_conn):
        rows = AccessBuilder(mock_conn).access_rm(
            "Satellite/Sat1", "Range Rate", "s", "e"
        )
        assert mock_conn.calls[-1] == (
            "Access_RM", "*/Satellite/Sat1",
            'Access Compute "Range Rate" "s" "e"',
        )
        assert rows == ["OK"]

    def test_access_rm_defaults_to_use_object_times(self, mock_conn):
        AccessBuilder(mock_conn).access_rm("Satellite/Sat1", "Access")
        assert mock_conn.calls[-1] == (
            "Access_RM", "*/Satellite/Sat1",
            'Access Compute "Access" UseObjectTimes',
        )

    def test_access_rm_rejects_unknown_style(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            AccessBuilder(mock_conn).access_rm("Satellite/Sat1", "Bogus")

    def test_access_rm_rejects_half_interval(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            AccessBuilder(mock_conn).access_rm(
                "Satellite/Sat1", "Access", start="s"
            )


class TestAccessMultiBuilder:
    """AccessMulti 先配置后计算框架的测试。"""

    def test_add_assets_joins_resolved_paths(self, mock_conn):
        AccessMultiBuilder(mock_conn).add_assets(
            "Satellite/Sat1/Sensor/Sen1", "Satellite/Sat2/Sensor/Sen1"
        )
        assert mock_conn.calls[-1] == (
            "AccessMulti", "/",
            " Assets */Satellite/Sat1/Sensor/Sen1 */Satellite/Sat2/Sensor/Sen1",
        )

    def test_add_objects_joins_resolved_paths(self, mock_conn):
        AccessMultiBuilder(mock_conn).add_objects(
            "Facility/T1", "Facility/T2"
        )
        assert mock_conn.calls[-1] == (
            "AccessMulti", "/",
            " Objects */Facility/T1 */Facility/T2",
        )

    def test_compute_with_interval(self, mock_conn):
        AccessMultiBuilder(mock_conn).compute("s", "e")
        assert mock_conn.calls[-1] == (
            "AccessMulti", "/", ' Access Compute "s" "e"'
        )

    def test_compute_defaults_to_use_object_times(self, mock_conn):
        AccessMultiBuilder(mock_conn).compute()
        assert mock_conn.calls[-1] == (
            "AccessMulti", "/", " Access Compute UseObjectTimes"
        )

    def test_add_assets_requires_path(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            AccessMultiBuilder(mock_conn).add_assets()

    def test_add_objects_requires_path(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            AccessMultiBuilder(mock_conn).add_objects()
