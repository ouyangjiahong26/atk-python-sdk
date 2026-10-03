"""
ATK Connect 模式 — 向量几何工具（VGT / VectorTool）

封装 4.2 的 VectorTool 命令族，用于在场景对象上创建、修改、删除
向量几何组件（Vector / Angle / Axes / Plane / Point / System）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from atk import exceptions as _ex
from atk import utils

if TYPE_CHECKING:
    from atk.connect.session import ATKConnection

# 组件类别（<ParentObject> {Action} {Kind} <Name> 中的 Kind）
VGT_KINDS = ("Vector", "Angle", "Axes", "Plane", "Point", "System")

# 各类别的组件类型合法取值（来自帮助文档 VectorTool 各分页的类型表）
VGT_TYPE_TABLE: dict[str, frozenset[str]] = {
    "Vector": frozenset({
        "Acceleration",
        "Angular Velocity",
        "Cross Product",
        "Derivative",
        "Displacement",
        "Fixed in Axes",
        "Intersection",
        "Linear Combination",
        "Orbit Normal",
        "Projection",
        "Projection Along Vector",
        "Reflection",
        "Scaled",
        "Velocity",
    }),
    "Angle": frozenset({
        "Between Planes",
        "Between Vectors",
        "Dihedral Angle",
        "Rotation",
        "To Plane",
        "Constant",
    }),
    "Axes": frozenset({
        "Aligned and Constrained",
        "Angular Offset",
        "Fixed at Epoch",
        "Fixed in Axes",
        "Libration",
        "Spinning",
        "Trajectory",
        "Launch",
        "Launch Inertial",
        "Topocentric",
    }),
    "Plane": frozenset({
        "Containing Two Vectors",
        "Normal",
        "Quadrant",
        "Trajectory",
        "Triad",
    }),
    "Point": frozenset({
        "B-Plane",
        "Fixed in System",
        "Fixed at Epoch",
        "Intersection",
        "Libration",
        "Projection",
    }),
    "System": frozenset({
        "Assembled",
        "Launch",
        "LaunchInertial",
        "Topocentric",
    }),
}


def _validate(kind: str, ctype: str | None, require_type: bool) -> str | None:
    """校验类别与组件类型，返回原样 ctype。"""
    if kind not in VGT_KINDS:
        raise _ex.ATKValueError(
            f"Unknown VectorTool kind {kind!r}. Valid kinds: {list(VGT_KINDS)}"
        )
    if ctype is None:
        if require_type:
            raise _ex.ATKValueError(
                f"ctype is required for kind {kind!r} "
                f"(valid types: {sorted(VGT_TYPE_TABLE[kind])})"
            )
        return None
    if ctype not in VGT_TYPE_TABLE[kind]:
        raise _ex.ATKValueError(
            f"Unknown {kind} type {ctype!r}. "
            f"Valid types: {sorted(VGT_TYPE_TABLE[kind])}"
        )
    return ctype


class VectorToolBuilder:
    """
    Connect 模式下 VectorTool（向量几何工具）的流式构建器。

    通过 ``atk.vector_tool(parent_object)`` 创建。

    Parameters
    ----------
    parent_object : str
        组件挂靠的父对象（场景内截断路径，如 ``"Satellite/Satellite1"``）。

    示例::

        vt = atk.vector_tool('Satellite/Satellite1')
        vt.create('Vector', 'V1', 'Displacement',
                  '"CentralBody/Earth ICRF.Origin" "CentralBody/Moon ICRF.Origin" '
                  'On On Transmit "CentralBody/Earth J2000"')
        vt.create('Angle', 'A1', 'Between Vectors',
                  '"CentralBody/Earth ICRF.Axes.X" "Satellite/Sat2 VVLH.Axes.Y"')
        vt.delete('Vector', 'V1')
    """

    def __init__(self, conn: "ATKConnection", parent_object: str):
        self._conn = conn
        # 父对象使用场景内截断路径（不带 */ 前缀）
        parent = parent_object.strip()
        if parent.startswith("*/"):
            parent = parent[2:]
        parent = parent.strip("/")
        if not parent:
            raise _ex.ATKValueError(
                "parent_object must be a scenario-relative path "
                "(e.g. 'Satellite/Satellite1')"
            )
        self._parent = parent

    @property
    def parent_object(self) -> str:
        return self._parent

    def create(
        self,
        kind: str,
        name: str,
        ctype: str | None = None,
        params: str = "",
    ) -> "VectorToolBuilder":
        """
        创建向量几何组件。

        对应命令 ``VectorTool * <Parent> Create {Kind} <Name>
        ["<Type>" <TypeParams>]``。未指定 ``ctype`` 时使用 ATK 默认值。

        Parameters
        ----------
        kind : str
            组件类别，见 :data:`VGT_KINDS`。
        name : str
            组件名称。
        ctype : str, optional
            组件类型（如 ``"Displacement"``），合法性按类别校验，
            见 :data:`VGT_TYPE_TABLE`。
        params : str, optional
            类型参数串（原样拼接，格式见帮助文档各类型示例）。

        Returns
        -------
        self
        """
        ctype = _validate(kind, ctype, require_type=False)
        param = f"{self._parent} Create {kind} {name}"
        if ctype is not None:
            param += f' "{ctype}" {params}'.rstrip()
        self._conn.send("VectorTool", "*", f" {param}")
        return self

    def modify(
        self,
        kind: str,
        name: str,
        ctype: str,
        params: str,
    ) -> "VectorToolBuilder":
        """
        修改现有向量几何组件（类型不可改，参数必填）。

        对应命令 ``VectorTool * <Parent> Modify {Kind} <Name>
        "<Type>" <TypeParams>``。

        Returns
        -------
        self
        """
        ctype = _validate(kind, ctype, require_type=True)
        param = f'{self._parent} Modify {kind} {name} "{ctype}" {params}'.rstrip()
        self._conn.send("VectorTool", "*", f" {param}")
        return self

    def delete(self, kind: str, name: str) -> "VectorToolBuilder":
        """
        删除向量几何组件。

        对应命令 ``VectorTool * <Parent> Delete {Kind} <Name>``。

        Returns
        -------
        self
        """
        _validate(kind, None, require_type=False)
        self._conn.send(
            "VectorTool", "*", f" {self._parent} Delete {kind} {name}"
        )
        return self

    # ------------------------------------------------------------------
    # 类型化便捷方法（参数格式照帮助文档示例）
    # ------------------------------------------------------------------

    def create_vector_displacement(
        self,
        name: str,
        origin_point: str,
        dest_point: str,
        ref_system: str,
        apparent: str = "On",
        ignore_aberration: str = "On",
        signal_sense: str = "Transmit",
    ) -> "VectorToolBuilder":
        """
        创建位移（Displacement）向量：从原点指向终点的向量。

        对应参数 ``"<Origin>" "<Dest>" {Apparent} {IgnoreAberration}
        {Receive|Transmit} "<RefSystem>"``。

        Parameters
        ----------
        name : str
            向量名称。
        origin_point, dest_point : str
            起/终点 VGT 路径（如 ``"CentralBody/Earth ICRF.Origin"``）。
        ref_system : str
            参考坐标系（如 ``"CentralBody/Earth J2000"``）。
        apparent, ignore_aberration : str
            ``On``/``Off``。
        signal_sense : str
            ``Transmit`` 或 ``Receive``。

        Returns
        -------
        self
        """
        return self.create(
            "Vector", name, "Displacement",
            f'"{origin_point}" "{dest_point}" {apparent} {ignore_aberration} '
            f'{signal_sense} "{ref_system}"',
        )

    def create_vector_cross_product(
        self,
        name: str,
        vector_a: str,
        vector_b: str,
    ) -> "VectorToolBuilder":
        """
        创建叉积（Cross Product）向量。

        Parameters
        ----------
        name : str
            向量名称。
        vector_a, vector_b : str
            参与叉积的向量 VGT 路径。

        Returns
        -------
        self
        """
        return self.create(
            "Vector", name, "Cross Product",
            f'"{vector_a}" "{vector_b}"',
        )

    def create_angle_between_vectors(
        self,
        name: str,
        from_vector: str,
        to_vector: str,
    ) -> "VectorToolBuilder":
        """
        创建两向量夹角（Between Vectors）角度组件。

        Parameters
        ----------
        name : str
            角度组件名称。
        from_vector, to_vector : str
            起/止向量 VGT 路径。

        Returns
        -------
        self
        """
        return self.create(
            "Angle", name, "Between Vectors",
            f'"{from_vector}" "{to_vector}"',
        )


# ---------------------------------------------------------------------------
# ATKConnection 扩展 — 添加工厂
# ---------------------------------------------------------------------------

def _patch_connection():
    from atk.connect import session as _s

    def vector_tool(self, parent_object: str) -> VectorToolBuilder:
        """为指定父对象创建 VectorToolBuilder。"""
        return VectorToolBuilder(self, parent_object)

    _s.ATKConnection.vector_tool = vector_tool


_patch_connection()
del _patch_connection
