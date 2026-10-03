"""
ATK Component 模式 — 批量坐标转换

封装 ``IATKBatchCrdnTransform``：配置时间类型、源/目的坐标系、
单位与数据列序，从文件导入数据并导出转换结果。
"""

from __future__ import annotations

from typing import Any, Iterable

from atk import exceptions as _ex
from atk.component.session import _ATK, _get_enum

# 导入/导出文件类型 → SWIG 枚举名
_IMPORT_FILE_TYPES = {
    "txt": "eTxt",
    "ephemeris": "eEPHEMERIS",
}

# 常用坐标系名（SetSrcCoordinate / SetDstCoordinate 直接接受字符串）
COORDINATE_SYSTEMS = (
    "J2000",
    "Fixed",
    "ICRF",
    "TrueOfDate",
    "MeanOfDate",
    "TEMEOfDate",
    "TrueEclipticOfDate",
    "MeanEclipticOfDate",
    "J2000Ecliptic",
)


def _resolve_import_type(file_type: str) -> Any:
    key = file_type.strip().lower()
    enum_name = _IMPORT_FILE_TYPES.get(key)
    if enum_name is None:
        raise _ex.ATKValueError(
            f"Unknown import file type {file_type!r}. "
            f"Valid types: {sorted(_IMPORT_FILE_TYPES)}"
        )
    return _get_enum(enum_name)


class BatchCoordinateTransform:
    """
    ``IATKBatchCrdnTransform`` 的 Python 风格封装。

    通过 :meth:`ComponentSession.batch_coord_transform()
    <atk.component.session.ComponentSession.batch_coord_transform>` 创建。

    示例::

        t = session.batch_coord_transform()
        t.set_time_utc('UTCG')
        t.set_source('Earth', 'J2000')
        t.set_destination('Earth', 'Fixed')
        t.set_units('m', 's')
        t.set_import_file(r'C:\\data\\in.txt', file_type='txt')
        t.set_data_sequence(0, 1, 2, 3)
        t.export(r'C:\\data\\out.txt')
    """

    def __init__(self, session: Any):
        self._session = session
        self._t = session.root.GetBatchCrdnTransform()

    @property
    def raw(self) -> Any:
        """底层 ``IATKBatchCrdnTransform`` SWIG 对象。"""
        return self._t

    # ------------------------------------------------------------------
    # 时间类型
    # ------------------------------------------------------------------

    def set_time_utc(self, utc_type: str) -> "BatchCoordinateTransform":
        """
        使用 UTC 时间类型（如 ``"UTCG"``）。"""
        self._t.SetTimeType(_get_enum("eUTCTIME"))
        self._t.SetUTCTimeType(utc_type)
        return self

    def set_time_relative(self, start: str) -> "BatchCoordinateTransform":
        """使用相对时间，起点为 ``start``。"""
        self._t.SetTimeType(_get_enum("eRELATIVETIME"))
        self._t.SetRelativeTimeStart(start)
        return self

    # ------------------------------------------------------------------
    # 坐标系与单位
    # ------------------------------------------------------------------

    def set_source(
        self, central_body: str, system: str
    ) -> "BatchCoordinateTransform":
        """
        设置源坐标系。

        Parameters
        ----------
        central_body : str
            中心天体名（如 ``"Earth"``）。
        system : str
            坐标系名（如 ``"J2000"``、``"Fixed"``、``"ICRF"``，
            常用取值见 :data:`COORDINATE_SYSTEMS`）。
        """
        self._t.SetSrcCoordinate(central_body, system)
        return self

    def set_destination(
        self, central_body: str, system: str
    ) -> "BatchCoordinateTransform":
        """设置目的坐标系（参数同 :meth:`set_source`）。"""
        self._t.SetDstCoordinate(central_body, system)
        return self

    def set_units(
        self, distance_unit: str, time_unit: str
    ) -> "BatchCoordinateTransform":
        """设置输出距离/时间单位（如 ``"m"``、``"s"``）。"""
        self._t.SetDistanceUnit(distance_unit)
        self._t.SetTimeUnit(time_unit)
        return self

    # ------------------------------------------------------------------
    # 数据列序
    # ------------------------------------------------------------------

    def set_data_sequence(self, *values: int) -> "BatchCoordinateTransform":
        """
        设置输入文件的数据列序（``std::vector<EDataSequence>``）。

        EDataSequence 为整型枚举（如 0=时间、1=X、2=Y、3=Z 等），
        按输入文件各列的语义依序传入。
        """
        vec = _ATK.vector_EDataSequence()
        for v in values:
            vec.push_back(int(v))
        self._t.SetCrdnTransformParam(vec)
        return self

    def get_data_sequence(self) -> list[Any]:
        """读取当前数据列序（尽力归一化为 list）。"""
        result = self._t.GetCrdnTransformParam()
        if result is None:
            return []
        try:
            return list(result)
        except TypeError:
            return [result]

    # ------------------------------------------------------------------
    # 文件导入与导出
    # ------------------------------------------------------------------

    def set_import_file(
        self, path: str, file_type: str = "txt"
    ) -> "BatchCoordinateTransform":
        """
        设置导入数据文件。

        Parameters
        ----------
        path : str
            数据文件路径。
        file_type : str
            ``"txt"``（ASCII）或 ``"ephemeris"``（星历文件）。
        """
        self._t.SetImportFileType(_resolve_import_type(file_type))
        self._t.SetImportFilePath(path)
        return self

    def set_export_file_type(self, file_type: str) -> "BatchCoordinateTransform":
        """设置导出文件类型（取值同 :meth:`set_import_file`）。"""
        self._t.SetExportFileType(_resolve_import_type(file_type))
        return self

    def export(self, path: str) -> Any:
        """
        执行转换并导出到 ``path``。

        Returns
        -------
        底层导出调用的返回值。
        """
        return self._t.Export(path)
