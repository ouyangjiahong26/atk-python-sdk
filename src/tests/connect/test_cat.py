"""
atk.connect.cat 的单元测试 — AdvCatBuilder（高级接近分析）。
"""

import pytest

from atk import exceptions as atk_exc
from atk.connect.cat import AdvCatBuilder


class TestAdvCatCreate:
    """AdvCat 创建与全局参数的测试。"""

    def test_create_sends_new_command(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").create()
        assert mock_conn.calls[-1] == ("New", "/", " AdvCat AdvCat1")

    def test_set_threshold(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").set_threshold(50000)
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1", " Threshold 50000"
        )

    def test_set_time_period(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").set_time_period("s", "e")
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1", ' TimePeriod "s" "e"'
        )

    def test_set_ssc_file_path_is_quoted(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").set_ssc_file("/tmp/SSC.rad")
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1", ' SSCFile "/tmp/SSC.rad"'
        )

    def test_set_ssc_file_on_off_unquoted(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").set_ssc_file("Off")
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1", " SSCFile Off"
        )


class TestAdvCatTargets:
    """主/次目标管理的测试。"""

    def test_add_primary_with_covariance(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").add_primary(
            "Satellite/Satellite1", 21000.0, 11000.0, 6000.0
        )
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1",
            ' Primary Add "Satellite/Satellite1" Fixed 21000.0 11000.0 6000.0',
        )

    def test_add_primary_with_hard_body_radius(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").add_primary(
            "Satellite/Satellite1", 1.0, 2.0, 3.0, hard_body_radius=10.0
        )
        assert mock_conn.calls[-1][2].endswith("HardBodyRadius 10.0")

    def test_add_primary_multi_joins_in_one_quote(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").add_primary_multi(
            ["Satellite/S2", "Satellite/S3"], 1.0, 2.0, 3.0
        )
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1",
            ' PrimaryMulti Add "Satellite/S2 Satellite/S3" Fixed 1.0 2.0 3.0',
        )

    def test_add_secondary_tle_file(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").add_secondary(
            r"E:\AstroData\atkAllTLE.tce", 1.0, 2.0, 3.0
        )
        assert mock_conn.calls[-1][2].startswith(
            ' Secondary Add "E:\\AstroData\\atkAllTLE.tce" Fixed'
        )

    def test_add_secondary_multi(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").add_secondary_multi(
            ["Satellite/S6", "Satellite/S7"], 1.0, 2.0, 3.0
        )
        assert mock_conn.calls[-1][2].startswith(
            ' SecondaryMulti Add "Satellite/S6 Satellite/S7" Fixed'
        )

    def test_remove_primary(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").remove_primary("Satellite/S1")
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1", ' Primary Remove "Satellite/S1"'
        )

    def test_remove_all_sends_both(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").remove_all()
        assert mock_conn.calls[-2:] == [
            ("ACAT", "*/AdvCat/AdvCat1", " Primary RemoveAll"),
            ("ACAT", "*/AdvCat/AdvCat1", " Secondary RemoveAll"),
        ]

    def test_compute(self, mock_conn):
        AdvCatBuilder(mock_conn, "AdvCat1").compute()
        assert mock_conn.calls[-1] == (
            "ACAT", "*/AdvCat/AdvCat1", " Compute On"
        )

    def test_add_primary_multi_requires_targets(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            AdvCatBuilder(mock_conn, "AdvCat1").add_primary_multi([])

    def test_add_secondary_multi_requires_targets(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            AdvCatBuilder(mock_conn, "AdvCat1").add_secondary_multi([])
