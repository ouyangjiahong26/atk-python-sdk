"""
atk.connect.coverage 的单元测试 — CoverageBuilder 和 CoverageStats。
"""

import pytest
from unittest.mock import MagicMock

from atk import exceptions as atk_exc


class TestCoverageStats:
    """CoverageStats 的测试。"""

    def test_unexpected_format_raises(self):
        from atk.connect.coverage import CoverageStats

        mock_raw = MagicMock()
        mock_raw.m_vectData = "completely unexpected format without equals signs"

        with pytest.raises(atk_exc.ATKError, match="Unexpected CoverageStats format"):
            _ = CoverageStats(mock_raw)

    def test_valid_key_value_format(self):
        from atk.connect.coverage import CoverageStats

        mock_raw = MagicMock()
        mock_raw.m_vectData = ["AccessCount=5", "TotalAccessTime=120.5", "MeanAccessDuration=24.1"]

        stats = CoverageStats(mock_raw)
        assert stats.access_count == 5
        assert stats.total_access_time == 120.5
        assert stats.mean_access_duration == 24.1

    def test_valid_positional_format(self):
        from atk.connect.coverage import CoverageStats

        mock_raw = MagicMock()
        mock_raw.m_vectData = ["10", "300.0", "30.0"]

        stats = CoverageStats(mock_raw)
        assert stats.access_count == 10
        assert stats.total_access_time == 300.0
        assert stats.mean_access_duration == 30.0


class TestCoverageBuilder42:
    """4.2 新增：Cov 时间区间 / Access 计算 / Cov_RM 报告。"""

    def test_set_interval(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        CoverageBuilder(mock_conn, "Cov1").set_interval("s", "e")
        assert mock_conn.calls[-1] == (
            "Cov", "*/CoverageDefinition/Cov1", ' Interval "s" "e"'
        )

    def test_access_compute(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        CoverageBuilder(mock_conn, "Cov1").access_compute("s", "e")
        assert mock_conn.calls[-1] == (
            "Cov", "*/CoverageDefinition/Cov1", ' Access Compute "s" "e"'
        )

    def test_access_clear(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        CoverageBuilder(mock_conn, "Cov1").access_clear()
        assert mock_conn.calls[-1] == (
            "Cov", "*/CoverageDefinition/Cov1", " Access Clear"
        )

    def test_access_rm_with_style_and_interval(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        rows = CoverageBuilder(mock_conn, "Cov1").access_rm(
            "Coverage", "s", "e"
        )
        assert mock_conn.calls[-1] == (
            "Cov_RM", "*/CoverageDefinition/Cov1",
            ' Access Compute "Coverage" "s" "e"',
        )
        assert rows == ["OK"]

    def test_access_rm_rejects_unknown_style(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        with pytest.raises(atk_exc.ATKValueError):
            CoverageBuilder(mock_conn, "Cov1").access_rm("Bogus")

    def test_fom_rm(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        CoverageBuilder(mock_conn, "Cov1").fom_rm(
            "CoverageTime", "Compute Total"
        )
        assert mock_conn.calls[-1] == (
            "Cov_RM", "*/CoverageDefinition/Cov1",
            " FOMDefine Definition CoverageTime Compute Total",
        )


class TestCoverageMultiBuilder:
    """CovMulti / CovMulti_RM 框架的测试。"""

    def test_full_workflow(self, mock_conn):
        from atk.connect.coverage import CoverageMultiBuilder

        multi = CoverageMultiBuilder(mock_conn)
        multi.add_assets("Satellite/S1/Sensor/Sen1")
        multi.add_objects("Facility/T1", "Facility/T2")
        multi.compute("s", "e")
        rows = multi.multi_fom_rm("RevisitTime", "Compute maximum")

        assert mock_conn.calls[-4] == (
            "CovMulti", "/", " Assets */Satellite/S1/Sensor/Sen1"
        )
        assert mock_conn.calls[-3] == (
            "CovMulti", "/", " Objects */Facility/T1 */Facility/T2"
        )
        assert mock_conn.calls[-2] == (
            "CovMulti", "/", ' Access Compute "s" "e"'
        )
        assert mock_conn.calls[-1] == (
            "CovMulti_RM", "/",
            " MultiFOMDefine Definition RevisitTime Compute maximum",
        )
        assert rows == ["OK"]

    def test_add_assets_requires_path(self, mock_conn):
        from atk.connect.coverage import CoverageMultiBuilder

        with pytest.raises(atk_exc.ATKValueError):
            CoverageMultiBuilder(mock_conn).add_assets()


class TestTimePairValidation:
    """时间区间参数成对校验（统一 utils.validate_time_pair 语义）。"""

    def test_access_rm_rejects_half_pair(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        builder = CoverageBuilder(mock_conn, "Cov1")
        with pytest.raises(atk_exc.ATKValueError):
            builder.access_rm("Coverage", start="s")
        with pytest.raises(atk_exc.ATKValueError):
            builder.access_rm("Coverage", stop="e")

    def test_access_rm_use_object_times_when_both_absent(self, mock_conn):
        from atk.connect.coverage import CoverageBuilder

        CoverageBuilder(mock_conn, "Cov1").access_rm("Coverage")
        assert mock_conn.calls[-1] == (
            "Cov_RM", "*/CoverageDefinition/Cov1",
            ' Access Compute "Coverage" UseObjectTimes',
        )
