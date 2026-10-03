"""
atk.connect.mcs 的单元测试 — McsBuilder。
"""
# pyright: reportArgumentType=none

import pytest
from unittest.mock import MagicMock

from tests.connect.conftest import MockATKConnection


class TestMcsBuilder:
    """McsBuilder 的测试。"""

    def test_initial_state_keplerian(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        mcs.initial_state_keplerian(sma=6678, ecc=0, inc=28.5, raan=0, argp=0, ta=0)

        insert_calls = [c for c in conn.calls if c[0] == "InsertSegment"]
        assert len(insert_calls) == 1
        assert "Initial_State" in insert_calls[0][2]

        setvalue_calls = [c for c in conn.calls if c[0] == "SetValue"]
        sma_call = [c for c in setvalue_calls if "sma" in c[2]][0]
        assert "6678" in sma_call[2]

    def test_propagate_until(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        mcs.propagate_until("10 Jan 2024 12:00:00.000")

        insert_calls = [c for c in conn.calls if c[0] == "InsertSegment"]
        assert any("Propagate" in c[2] for c in insert_calls)

    def test_impulsive_burn(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        mcs.impulsive_burn(dv=[0.5, 0.1, -0.2])

        insert_calls = [c for c in conn.calls if c[0] == "InsertSegment"]
        assert any("ImpulsiveBurn" in c[2] for c in insert_calls)

        dv_calls = [c for c in conn.calls if "dvX" in c[2] or "dvY" in c[2] or "dvZ" in c[2]]
        assert len(dv_calls) == 3

    def test_impulsive_burn_wrong_dv_length_raises(self) -> None:
        from atk.connect.mcs import McsBuilder
        from atk import exceptions as atk_exc

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")

        with pytest.raises(atk_exc.ATKValueError, match="3 components"):
            mcs.impulsive_burn(dv=[0.5, 0.1])  # 仅 2 个分量

    def test_run_calls_runmcs(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        mcs.run()

        assert ("RunMCS", "*/Satellite/Sat1", "") in conn.calls

    def test_apply_changes(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        mcs.apply_changes()

        assert ("ApplyAllProfileChanges", "*/Satellite/Sat1", "") in conn.calls

    def test_segment_count_increments(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        assert mcs.get_segment_count() == 0

        mcs.initial_state_keplerian(sma=6678, ecc=0, inc=0, raan=0, argp=0, ta=0)
        assert mcs.get_segment_count() == 1

        mcs.propagate_until("10 Jan 2024")
        assert mcs.get_segment_count() == 2


class TestInsertSegment:
    """4.2 新增：通用 insert_segment（含 RPO 段）。"""

    def test_insert_rpo_segment_known_type(self) -> None:
        import warnings
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            mcs.insert_segment("ConeApproach")

        assert conn.calls[-1] == (
            "InsertSegment", "*/Satellite/Sat1", " ConeApproach Segment_0"
        )
        assert mcs.get_segment_count() == 1

    def test_insert_segment_with_custom_name(self) -> None:
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        mcs.insert_segment("FastRendezvous", name="MySeg")

        assert conn.calls[-1] == (
            "InsertSegment", "*/Satellite/Sat1", " FastRendezvous MySeg"
        )

    def test_unknown_segment_type_warns_but_passes_through(self) -> None:
        import warnings
        from atk.connect.mcs import McsBuilder

        conn = MockATKConnection()
        mcs = McsBuilder(conn, "*/Satellite/Sat1")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            mcs.insert_segment("WeirdType")

        assert len(caught) == 1
        assert conn.calls[-1] == (
            "InsertSegment", "*/Satellite/Sat1", " WeirdType Segment_0"
        )
