"""
atk.connect.constellation（ConstellationCreator）与
atk.connect.reports（quick_report / exec_report 族）的单元测试。
"""

from unittest.mock import MagicMock, patch

import pytest

from atk.connect.constellation import ConstellationCreator
from atk.connect.reports import ExecReport


ELEM = ("Semimajoraxis 6678137 Eccentricity 0 Inclination 28.5 "
        "RAAN 0 ArgumentOfPerigee 180 TureAnomaly 180")


class TestWalkerDelta:
    """WalkerDelta 命令封装的测试。"""

    def test_from_elements_matches_doc_example(self, mock_conn):
        ConstellationCreator(mock_conn).walker_delta_from_elements(
            6678137, 0, 28.5, 0, 180, 180,
            num_planes=2, sats_per_plane=8,
            inter_plane_phase=1, raan_spread=360, color_by_plane=True,
        )
        assert mock_conn.calls[-1] == (
            "WalkerDelta", "/",
            f" {ELEM} NumPlanes 2 NumSatsPerPlane 8 "
            "InterPlanePhaseIncrement 1 RAANSpread 360 ColorByPlane Yes",
        )

    def test_from_seed_uses_seed_path(self, mock_conn):
        ConstellationCreator(mock_conn).walker_delta_from_seed(
            "Satellite/Sat1", 2, 11, 1, 360
        )
        cmd, path, param = mock_conn.calls[-1]
        assert (cmd, path) == ("WalkerDelta", "*/Satellite/Sat1")
        assert param.startswith(
            " NumPlanes 2 NumSatsPerPlane 11 "
            "InterPlanePhaseIncrement 1 RAANSpread 360"
        )
        assert param.endswith("ColorByPlane No")


class TestOtherConstellations:
    """WalkerCustom / Rosette / Flower / AsymmetricFlower 的测试。"""

    def test_walker_custom_from_elements(self, mock_conn):
        ConstellationCreator(mock_conn).walker_custom_from_elements(
            6678137, 0, 28.5, 0, 180, 180,
            2, 20, 20, 20, color_by_plane=True,
        )
        cmd, _, param = mock_conn.calls[-1]
        assert cmd == "WalkerCustom"
        assert "NumPlanes 2 TotalNumSats 20" in param
        assert "InterPlaneTrueAnomalyIncrement 20" in param
        assert "RAANIncrement 20" in param
        assert "TureAnomaly 180" in param

    def test_rosette_from_seed(self, mock_conn):
        ConstellationCreator(mock_conn).rosette_from_seed(
            "Satellite/Sat1", 20, 20, 1, color_by_plane=True
        )
        assert mock_conn.calls[-1] == (
            "Rosette", "*/Satellite/Sat1",
            " NumPlanes 20 TotalNumSats 20 Molecule 1 ColorByPlane Yes",
        )

    def test_flower_from_elements(self, mock_conn):
        ConstellationCreator(mock_conn).flower_from_elements(
            6678137, 0, 28.5, 0, 180, 180,
            16, 1, 16, 1, 16, 360, color_by_plane=True,
        )
        cmd, _, param = mock_conn.calls[-1]
        assert cmd == "Flower"
        assert "TotalNumSats 16 InterPlanePhaseIncrement 1" in param
        assert "ReturnCircle 16 ReturnDay 1" in param
        assert "PhaseDensity 16 RAANSpread 360" in param

    def test_asymmetric_flower_from_seed(self, mock_conn):
        ConstellationCreator(mock_conn).asymmetric_flower_from_seed(
            "Satellite/Sat1", 16, 16, 1, 30
        )
        assert mock_conn.calls[-1] == (
            "AsymmetricFlower", "*/Satellite/Sat1",
            " TotalNumSats 16 ReturnCircle 16 ReturnDay 1 "
            "RAANIncrement 30 ColorByPlane No",
        )


def _real_conn():
    """构造真实 ATKConnection 并 mock 底层 SWIG。"""
    from atk.connect.session import ATKConnection
    patcher = patch("atk.connect.session._ATK")
    mock_atk = patcher.start()
    mock_result = MagicMock()
    mock_result.m_vectData = "OK"
    mock_atk.atkConnect.return_value = mock_result
    conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
    return conn, mock_atk, patcher


class TestQuickReportCommands:
    """quick_report_* 连接方法补丁的测试。"""

    def test_quick_report_create(self):
        conn, mock_atk, patcher = _real_conn()
        try:
            conn.quick_report_create("QR1")
            mock_atk.atkConnect.assert_called_once_with(
                1, "QuickReportCreate", '* "QR1"'
            )
        finally:
            patcher.stop()

    def test_quick_report_add(self):
        conn, mock_atk, patcher = _real_conn()
        try:
            conn.quick_report_add(
                "Sat Pos-Vel", "J2000 Position Velocity",
                "Satellite/Satellite1",
            )
            mock_atk.atkConnect.assert_called_once_with(
                1, "QuickReportAdd",
                '* Name "Sat Pos-Vel" Type Report '
                'Style "J2000 Position Velocity" '
                "Object Satellite/Satellite1",
            )
        finally:
            patcher.stop()

    def test_quick_report_add_with_from_object(self):
        conn, mock_atk, patcher = _real_conn()
        try:
            conn.quick_report_add(
                "A", "S", "Satellite/Sat1", from_object="Facility/F1"
            )
            assert mock_atk.atkConnect.call_args[0][2].endswith(
                "FromObject Facility/F1"
            )
        finally:
            patcher.stop()

    def test_quick_report_list(self):
        conn, _, patcher = _real_conn()
        try:
            rows = conn.quick_report_list()
            assert rows == ["OK"]
        finally:
            patcher.stop()

    def test_quick_report_get(self):
        conn, mock_atk, patcher = _real_conn()
        try:
            conn.quick_report_get("QR1")
            mock_atk.atkConnect.assert_called_once_with(
                1, "QuickReport_RM", '* GetReport "QR1"'
            )
        finally:
            patcher.stop()


class TestExecReport:
    """ExecReport（Exec_ReportCreate / Exec_Report_RM）的测试。"""

    def test_create_with_all_options(self, mock_conn):
        ExecReport(mock_conn, "Satellite/Sat1", "Position").create(
            file="linshi.rsf",
            start="2023-07-29 09:19:01.000",
            stop="2023-07-29 10:09:38.000",
            time_step=60,
        )
        assert mock_conn.calls[-1] == (
            "Exec_ReportCreate", "*/Satellite/Sat1",
            ' Style "Position" File "linshi.rsf" '
            'TimePeriod "2023-07-29 09:19:01.000" '
            '"2023-07-29 10:09:38.000" TimeStep 60',
        )

    def test_rm_returns_report_result(self, mock_conn):
        result = ExecReport(mock_conn, "Satellite/Sat1", "Position").rm(
            start="s", stop="e"
        )
        assert mock_conn.calls[-1][0] == "Exec_Report_RM"
        assert result.data == ["OK"]

    def test_rejects_half_time_period(self, mock_conn):
        with pytest.raises(Exception):
            ExecReport(mock_conn, "Satellite/Sat1", "Position").rm(start="s")

    def test_connection_level_shortcuts(self):
        conn, mock_atk, patcher = _real_conn()
        try:
            conn.exec_report_create("Satellite/S1", "Position", time_step=60)
            assert mock_atk.atkConnect.call_args[0][1] == "Exec_ReportCreate"
            conn.exec_report_rm("Satellite/S1", "Position")
            assert mock_atk.atkConnect.call_args[0][1] == "Exec_Report_RM"
        finally:
            patcher.stop()
