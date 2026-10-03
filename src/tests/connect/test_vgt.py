"""
atk.connect.vgt 的单元测试 — VectorToolBuilder。
"""

import pytest

from atk import exceptions as atk_exc
from atk.connect.vgt import VectorToolBuilder


class TestVectorToolBuilderCreate:
    """VectorTool Create/Modify/Delete 的测试。"""

    def test_create_with_type_and_params(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1").create(
            "Vector", "V1", "Displacement", '"O" "D" On On Transmit "R"'
        )
        assert mock_conn.calls[-1] == (
            "VectorTool", "*",
            ' Satellite/Sat1 Create Vector V1 "Displacement" '
            '"O" "D" On On Transmit "R"',
        )

    def test_create_without_type_uses_default(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1").create(
            "Angle", "A1", "Between Planes"
        )
        assert mock_conn.calls[-1] == (
            "VectorTool", "*",
            ' Satellite/Sat1 Create Angle A1 "Between Planes"',
        )

    def test_create_rejects_unknown_kind(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            VectorToolBuilder(mock_conn, "Satellite/Sat1").create(
                "Bogus", "X"
            )

    def test_create_rejects_unknown_type(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            VectorToolBuilder(mock_conn, "Satellite/Sat1").create(
                "Vector", "V1", "NoSuchType"
            )

    def test_modify_requires_type(self, mock_conn):
        builder = VectorToolBuilder(mock_conn, "Satellite/Sat1")
        with pytest.raises(atk_exc.ATKValueError):
            builder.modify("Vector", "V1", None, "params")

    def test_modify_sends_type_and_params(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1").modify(
            "Angle", "A1", "Between Vectors", '"F" "T"'
        )
        assert mock_conn.calls[-1] == (
            "VectorTool", "*",
            ' Satellite/Sat1 Modify Angle A1 "Between Vectors" "F" "T"',
        )

    def test_delete(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1").delete("Vector", "V1")
        assert mock_conn.calls[-1] == (
            "VectorTool", "*", " Satellite/Sat1 Delete Vector V1"
        )

    def test_parent_object_accepts_wildcard_prefix(self, mock_conn):
        builder = VectorToolBuilder(mock_conn, "*/Satellite/Sat1")
        assert builder.parent_object == "Satellite/Sat1"

    def test_parent_object_rejects_empty(self, mock_conn):
        with pytest.raises(atk_exc.ATKValueError):
            VectorToolBuilder(mock_conn, "  ")


class TestVectorToolTypedHelpers:
    """类型化便捷方法的测试。"""

    def test_create_vector_displacement(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1") \
            .create_vector_displacement(
                "V1", "CentralBody/Earth ICRF.Origin",
                "CentralBody/Moon ICRF.Origin", "CentralBody/Earth J2000",
            )
        assert mock_conn.calls[-1] == (
            "VectorTool", "*",
            ' Satellite/Sat1 Create Vector V1 "Displacement" '
            '"CentralBody/Earth ICRF.Origin" "CentralBody/Moon ICRF.Origin" '
            'On On Transmit "CentralBody/Earth J2000"',
        )

    def test_create_vector_cross_product(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1") \
            .create_vector_cross_product("V2", "VecA", "VecB")
        assert mock_conn.calls[-1] == (
            "VectorTool", "*",
            ' Satellite/Sat1 Create Vector V2 "Cross Product" "VecA" "VecB"',
        )

    def test_create_angle_between_vectors(self, mock_conn):
        VectorToolBuilder(mock_conn, "Satellite/Sat1") \
            .create_angle_between_vectors("A1", "From", "To")
        assert mock_conn.calls[-1] == (
            "VectorTool", "*",
            ' Satellite/Sat1 Create Angle A1 "Between Vectors" "From" "To"',
        )
