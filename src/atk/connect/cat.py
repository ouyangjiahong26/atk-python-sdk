"""
ATK Connect 模式 — 高级接近分析（AdvCat / ACAT）

封装 4.2 的 ACAT 命令族：设置主/次目标、阈值、时间窗并计算接近事件。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from atk import exceptions as _ex
from atk import utils

if TYPE_CHECKING:
    from atk.connect.session import ATKConnection


class AdvCatBuilder:
    """
    Connect 模式下高级接近分析对象（AdvCat）的流式构建器。

    通过 ``atk.create_adv_cat(name)`` 创建（同时发送 New 命令）。

    示例::

        cat = atk.create_adv_cat('AdvCat1')
        cat.set_threshold(50000)
        cat.add_primary('Satellite/Satellite1', 21000.0, 11000.0, 6000.0)
        cat.set_time_period('14 Nov 2030 08:00:00.000', '15 Nov 2030 08:00:00.000')
        cat.compute()
    """

    def __init__(self, conn: "ATKConnection", name: str):
        self._conn = conn
        self._name = utils.validate_name(name)
        self._path = f"*/AdvCat/{self._name}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    def create(self) -> "AdvCatBuilder":
        """
        在场景中创建 AdvCat 对象。

        对应命令 ``New / AdvCat {name}``。
        """
        self._conn.send("New", "/", f" AdvCat {self._name}")
        return self

    # ------------------------------------------------------------------
    # 阈值与全局参数
    # ------------------------------------------------------------------

    def set_threshold(self, meters: float) -> "AdvCatBuilder":
        """
        设置接近阈值（米）。

        对应命令 ``ACAT <path> Threshold <DistanceValue>``。
        """
        self._conn.send("ACAT", self._path, f" Threshold {meters}")
        return self

    def set_ssc_file(self, value: str) -> "AdvCatBuilder":
        """
        使用 SSC 文件设置目标半径。

        对应命令 ``ACAT <path> SSCFile {On | Off | "<FilePath>"}``。

        Parameters
        ----------
        value : str
            ``"On"``、``"Off"`` 或 SSC 文件路径。
        """
        if value in ("On", "Off"):
            self._conn.send("ACAT", self._path, f" SSCFile {value}")
        else:
            self._conn.send("ACAT", self._path, f' SSCFile "{value}"')
        return self

    def set_time_period(self, start: str, stop: str) -> "AdvCatBuilder":
        """
        设置接近分析时间窗。

        对应命令 ``ACAT <path> TimePeriod "<Start>" "<Stop>"``。
        """
        self._conn.send(
            "ACAT", self._path, f' TimePeriod "{start}" "{stop}"'
        )
        return self

    # ------------------------------------------------------------------
    # 主/次目标
    # ------------------------------------------------------------------

    def _add_target(
        self,
        list_keyword: str,
        target: str,
        tangential: float,
        cross_track: float,
        normal: float,
        hard_body_radius: float | None,
        multi: bool,
    ) -> None:
        keyword = f"{list_keyword}Multi" if multi else list_keyword
        # 目标可以是场景内截断路径或 TLE 文件路径，均带引号；
        # Multi 形态将多个路径以空格连接放在同一引号内
        param = f' {keyword} Add "{target}" Fixed {tangential} {cross_track} {normal}'
        if hard_body_radius is not None:
            param += f" HardBodyRadius {hard_body_radius}"
        self._conn.send("ACAT", self._path, param)

    def add_primary(
        self,
        target: str,
        tangential: float = 0.0,
        cross_track: float = 0.0,
        normal: float = 0.0,
        hard_body_radius: float | None = None,
    ) -> "AdvCatBuilder":
        """
        添加主目标。

        对应命令 ``ACAT <path> Primary Add "<Target>" Fixed <T> <C> <N>
        [HardBodyRadius <R>]``。

        Parameters
        ----------
        target : str
            场景内对象路径（如 ``"Satellite/Satellite1"``）或
            TLE 文件绝对路径。
        tangential, cross_track, normal : float
            目标切向/径向/法向协方差（米）。
        hard_body_radius : float, optional
            目标包络球半径（米）。

        Returns
        -------
        self
        """
        self._add_target(
            "Primary", target, tangential, cross_track, normal,
            hard_body_radius, multi=False,
        )
        return self

    def add_primary_multi(
        self,
        targets: list[str] | tuple[str, ...],
        tangential: float = 0.0,
        cross_track: float = 0.0,
        normal: float = 0.0,
        hard_body_radius: float | None = None,
    ) -> "AdvCatBuilder":
        """
        批量添加多个主目标（一个命令、空格分隔放同一引号内）。

        对应命令 ``ACAT <path> PrimaryMulti Add "<T1 T2 ...>" Fixed ...``。
        """
        if not targets:
            raise _ex.ATKValueError("add_primary_multi requires at least one target")
        joined = " ".join(str(t) for t in targets)
        self._add_target(
            "Primary", joined, tangential, cross_track, normal,
            hard_body_radius, multi=True,
        )
        return self

    def add_secondary(
        self,
        target: str,
        tangential: float = 0.0,
        cross_track: float = 0.0,
        normal: float = 0.0,
        hard_body_radius: float | None = None,
    ) -> "AdvCatBuilder":
        """
        添加次目标（场景对象或 TLE 文件路径）。

        对应命令 ``ACAT <path> Secondary Add "<Target>" Fixed ...``。
        """
        self._add_target(
            "Secondary", target, tangential, cross_track, normal,
            hard_body_radius, multi=False,
        )
        return self

    def add_secondary_multi(
        self,
        targets: list[str] | tuple[str, ...],
        tangential: float = 0.0,
        cross_track: float = 0.0,
        normal: float = 0.0,
        hard_body_radius: float | None = None,
    ) -> "AdvCatBuilder":
        """
        批量添加多个次目标。

        对应命令 ``ACAT <path> SecondaryMulti Add "<T1 T2 ...>" Fixed ...``。
        """
        if not targets:
            raise _ex.ATKValueError(
                "add_secondary_multi requires at least one target"
            )
        joined = " ".join(str(t) for t in targets)
        self._add_target(
            "Secondary", joined, tangential, cross_track, normal,
            hard_body_radius, multi=True,
        )
        return self

    def remove_primary(self, target: str) -> "AdvCatBuilder":
        """
        从主目标列表移除目标。

        对应命令 ``ACAT <path> Primary Remove "<Target>"``。
        """
        self._conn.send("ACAT", self._path, f' Primary Remove "{target}"')
        return self

    def remove_secondary(self, target: str) -> "AdvCatBuilder":
        """
        从次目标列表移除目标。

        对应命令 ``ACAT <path> Secondary Remove "<Target>"``。
        """
        self._conn.send("ACAT", self._path, f' Secondary Remove "{target}"')
        return self

    def remove_all(self) -> "AdvCatBuilder":
        """
        移除主、次目标列表中的所有目标。

        对应命令 ``ACAT <path> Primary RemoveAll`` 与
        ``ACAT <path> Secondary RemoveAll``。
        """
        self._conn.send("ACAT", self._path, " Primary RemoveAll")
        self._conn.send("ACAT", self._path, " Secondary RemoveAll")
        return self

    # ------------------------------------------------------------------
    # 计算
    # ------------------------------------------------------------------

    def compute(self) -> "AdvCatBuilder":
        """
        计算接近事件。

        对应命令 ``ACAT <path> Compute On``。
        """
        self._conn.send("ACAT", self._path, " Compute On")
        return self

    def __repr__(self) -> str:
        return f"<AdvCatBuilder name={self._name!r}>"


# ---------------------------------------------------------------------------
# ATKConnection 扩展 — 添加工厂
# ---------------------------------------------------------------------------

def _patch_connection():
    from atk.connect import session as _s

    def create_adv_cat(self, name: str) -> AdvCatBuilder:
        """创建 AdvCat 对象并返回 AdvCatBuilder。"""
        builder = AdvCatBuilder(self, name)
        builder.create()
        return builder

    _s.ATKConnection.create_adv_cat = create_adv_cat


_patch_connection()
del _patch_connection
