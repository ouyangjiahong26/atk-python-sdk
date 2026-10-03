"""
ATK Component 模式 — 向量几何工具（VGT）

封装 ``ICrdnProvider`` 及其六个组件组（Angle / Axes / Plane / Point /
System / Vector），提供创建、删除、查询与类型化便捷方法。
"""

from __future__ import annotations

from typing import Any

from atk import exceptions as _ex
from atk.component.session import _ATK

# 组名 → ICrdnProvider 取组方法名
_GROUP_GETTER = {
    "angle": "GetAngles",
    "axes": "GetAxes",
    "plane": "GetPlanes",
    "point": "GetPoints",
    "system": "GetSystems",
    "vector": "GetVectors",
}

# 组名 → SWIG 枚举前缀（如 eCrdnVectorTypeDisplacement）
_GROUP_ENUM_PREFIX = {g: f"eCrdn{g.capitalize()}Type" for g in _GROUP_GETTER}


def _group_types(group: str) -> list[str]:
    """扫描模块属性，列出该组的全部组件类型枚举名。"""
    prefix = _GROUP_ENUM_PREFIX[group]
    return sorted(
        name for name in dir(_ATK)
        if name.startswith(prefix)
    )


def _resolve_vgt_enum(group: str, vgt_type: str) -> Any:
    """
    将组件类型字符串解析为 SWIG 枚举值。

    接受两种形式：

    - 完整枚举名（如 ``"eCrdnVectorTypeDisplacement"``）；
    - 去前缀短名（如 ``"Displacement"``），按枚举后缀匹配，
      大小写与空格不敏感（如 ``"Between Vectors"`` →
      ``eCrdnAngleTypeBetweenVectors``）。
    """
    if group not in _GROUP_GETTER:
        raise _ex.ATKValueError(
            f"Unknown VGT group {group!r}. "
            f"Valid groups: {sorted(_GROUP_GETTER)}"
        )
    prefix = _GROUP_ENUM_PREFIX[group]
    t = vgt_type.strip()
    if t.startswith("eCrdn") and hasattr(_ATK, t):
        return getattr(_ATK, t)
    target = t.replace(" ", "").casefold()
    for name in _group_types(group):
        if name[len(prefix):].replace(" ", "").casefold() == target:
            return getattr(_ATK, name)
    raise _ex.ATKValueError(
        f"Unknown VGT {group} type {vgt_type!r}. "
        f"Available types: {_group_types(group)}"
    )


class VgtBuilder:
    """
    ``ICrdnProvider``（对象 VGT）的 Python 风格封装。

    通过 ``obj.GetVGT()`` 获得 provider；一般配合
    :meth:`ComponentSession.get_object()
    <atk.component.session.ComponentSession.get_object>` 使用。

    示例::

        sat = session.get_object('Satellite/Sat1')
        vgt = VgtBuilder(sat)
        v = vgt.create_vector_displacement(
            'Disp', 'CentralBody/Earth ICRF.Origin',
            'CentralBody/Moon ICRF.Origin')
        vgt.contains('vector', 'Disp')   # -> True
        vgt.remove('vector', 'Disp')
    """

    def __init__(self, obj: Any):
        self._obj = obj
        self._provider = obj.GetVGT()

    @property
    def raw(self) -> Any:
        """底层 ``ICrdnProvider`` SWIG 对象。"""
        return self._provider

    def _group(self, group: str) -> Any:
        try:
            getter = _GROUP_GETTER[group]
        except KeyError:
            raise _ex.ATKValueError(
                f"Unknown VGT group {group!r}. "
                f"Valid groups: {sorted(_GROUP_GETTER)}"
            ) from None
        return getattr(self._provider, getter)()

    # ------------------------------------------------------------------
    # 通用操作
    # ------------------------------------------------------------------

    def create(
        self,
        group: str,
        name: str,
        description: str,
        vgt_type: str,
    ) -> Any:
        """
        在指定组中创建组件，返回底层 SWIG 组件对象。

        Parameters
        ----------
        group : str
            组件组（``"vector"`` / ``"angle"`` / ``"axes"`` /
            ``"plane"`` / ``"point"`` / ``"system"``）。
        name, description : str
            组件名称与描述。
        vgt_type : str
            组件类型枚举名或去前缀短名，见 :func:`_resolve_vgt_enum`。

        Returns
        -------
        底层 SWIG 组件对象（如 ``ICrdnVectorDisplacement``）。
        """
        enum = _resolve_vgt_enum(group, vgt_type)
        return self._group(group).Create(name, description, enum)

    def remove(self, group: str, name: str) -> "VgtBuilder":
        """删除指定组中的组件。"""
        self._group(group).Remove(name)
        return self

    def contains(self, group: str, name: str) -> bool:
        """查询指定组中是否已存在同名组件。"""
        return bool(self._group(group).Contains(name))

    def item(self, group: str, name: str) -> Any:
        """按名称取组内组件，返回底层 SWIG 对象。"""
        return self._group(group).Item(name)

    def supported_types(self, group: str) -> list[Any]:
        """返回该组支持的组件类型（尽力归一化为 list）。"""
        result = self._group(group).GetSupportedVGTTypes()
        if result is None:
            return []
        try:
            return list(result)
        except TypeError:
            return [result]

    # ------------------------------------------------------------------
    # 类型化便捷方法
    # ------------------------------------------------------------------

    def create_vector_displacement(
        self,
        name: str,
        origin_point: str,
        dest_point: str,
        ref_system: str | None = None,
        description: str = "",
    ) -> Any:
        """
        创建位移向量并设置起/终点。

        ``Create`` 返回的对象按 SWIG 即 ``ICrdnVectorDisplacement``
        具体类型，直接调用其 Set 方法完成配置。

        Parameters
        ----------
        name : str
            向量名称。
        origin_point, dest_point : str
            起/终点 VGT 路径（如 ``"CentralBody/Earth ICRF.Origin"``）。
        ref_system : str, optional
            参考坐标系路径。

        Returns
        -------
        ICrdnVectorDisplacement
            配置完成的底层向量对象。
        """
        vec = self.create(
            "vector", name, description, "eCrdnVectorTypeDisplacement"
        )
        vec.SetStartPoint(origin_point)
        vec.SetEndPoint(dest_point)
        if ref_system is not None:
            vec.SetReferenceSystem(ref_system)
        return vec

    def create_vector_cross_product(
        self,
        name: str,
        vector_a: str,
        vector_b: str,
        description: str = "",
    ) -> Any:
        """
        创建叉积向量（向量路径为参与叉积的两向量 VGT 路径）。

        Returns
        -------
        ICrdnVectorCrossProduct
        """
        vec = self.create(
            "vector", name, description, "eCrdnVectorTypeCrossProduct"
        )
        vec.SetVectorA(vector_a)
        vec.SetVectorB(vector_b)
        return vec

    def create_angle_between_vectors(
        self,
        name: str,
        from_vector: str,
        to_vector: str,
        description: str = "",
    ) -> Any:
        """
        创建两向量夹角组件。

        Returns
        -------
        ICrdnAngleBetweenVector
        """
        angle = self.create(
            "angle", name, description, "eCrdnAngleTypeBetweenVectors"
        )
        angle.SetVectorFrom(from_vector)
        angle.SetVectorTo(to_vector)
        return angle
