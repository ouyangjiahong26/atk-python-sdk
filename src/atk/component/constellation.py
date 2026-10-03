"""
ATK Component 模式 — 星座设计

封装 ``IConstellDesign``：WalkerDelta / WalkerCustom / Rosette / Flower /
AsymmetricFlower（非对称 Flower）星座的批量创建。

单位约定（与 SWIG 签名一致）：半长轴 sMajAx 为米，角度为度。
"""

from __future__ import annotations

from typing import Any


class ConstellationDesigner:
    """
    ``IConstellDesign`` 的 Python 风格封装。

    通过 :meth:`ComponentSession.constellation_designer()
    <atk.component.session.ComponentSession.constellation_designer>` 创建，
    内部持有 ``session.root.GetConstellDesign()``。

    示例::

        designer = session.constellation_designer()
        designer.walker_delta(
            sma=6678137, ecc=0, inc=28.5, raan=0, argp=180, ta=180,
            num_planes=2, sats_per_plane=8,
            inter_plane_spacing=1, raan_spread=360)
    """

    def __init__(self, session: Any):
        self._session = session
        self._design = session.root.GetConstellDesign()

    @property
    def raw(self) -> Any:
        """底层 ``IConstellDesign`` SWIG 对象。"""
        return self._design

    # ------------------------------------------------------------------
    # WalkerDelta
    # ------------------------------------------------------------------

    def walker_delta(
        self,
        sma: float,
        ecc: float,
        inc: float,
        raan: float,
        argp: float,
        ta: float,
        num_planes: int,
        sats_per_plane: int,
        inter_plane_spacing: float,
        raan_spread: float,
    ) -> "ConstellationDesigner":
        """
        按轨道六要素创建 WalkerDelta 星座。

        Parameters
        ----------
        sma : float
            半长轴（米）。
        ecc, inc, raan, argp, ta : float
            离心率、倾角/升交点赤经/近地点幅角/真近点角（度）。
        num_planes, sats_per_plane : int
            轨道面数与每面卫星数。
        inter_plane_spacing, raan_spread : float
            面间相位增量（度）与升交点赤经分布（度）。
        """
        # SWIG typemap：interPlaneSpacing 为 int 参数（raanSpread 接受浮点）
        self._design.ConstellDesignWalkerDelta(
            sma, ecc, inc, raan, argp, ta,
            int(num_planes), int(sats_per_plane), int(inter_plane_spacing),
            raan_spread,
        )
        return self

    def walker_delta_by_seed(
        self,
        seed_sat_path: str,
        num_planes: int,
        sats_per_plane: int,
        inter_plane_spacing: float,
        raan_spread: float,
    ) -> "ConstellationDesigner":
        """以已有卫星为种子创建 WalkerDelta 星座。"""
        self._design.ConstellDesignWalkerDeltaBySeed(
            seed_sat_path, int(num_planes), int(sats_per_plane),
            int(inter_plane_spacing), raan_spread,
        )
        return self

    # ------------------------------------------------------------------
    # WalkerCustom
    # ------------------------------------------------------------------

    def walker_custom(
        self,
        sma: float,
        ecc: float,
        inc: float,
        raan: float,
        argp: float,
        ta: float,
        num_planes: int,
        sats_per_plane: int,
        true_anomaly_phasing: float,
        raan_increment: float,
    ) -> "ConstellationDesigner":
        """
        按轨道六要素创建 WalkerCustom 星座。

        Parameters
        ----------
        true_anomaly_phasing, raan_increment : float
            面间真近点角增量与升交点赤经增量（度）。
        """
        self._design.ConstellDesignWalkerCustom(
            sma, ecc, inc, raan, argp, ta,
            int(num_planes), int(sats_per_plane),
            true_anomaly_phasing, raan_increment,
        )
        return self

    def walker_custom_by_seed(
        self,
        seed_sat_path: str,
        num_planes: int,
        sats_per_plane: int,
        true_anomaly_phasing: float,
        raan_increment: float,
    ) -> "ConstellationDesigner":
        """以已有卫星为种子创建 WalkerCustom 星座。"""
        self._design.ConstellDesignWalkerCustomBySeed(
            seed_sat_path, int(num_planes), int(sats_per_plane),
            true_anomaly_phasing, raan_increment,
        )
        return self

    # ------------------------------------------------------------------
    # Rosette
    # ------------------------------------------------------------------

    def rosette(
        self,
        sma: float,
        ecc: float,
        inc: float,
        raan: float,
        argp: float,
        ta: float,
        num_planes: int,
        sats_per_plane: int,
        molecule: float,
    ) -> "ConstellationDesigner":
        """按轨道六要素创建 Rosette（玫瑰）星座。"""
        self._design.ConstellDesignRosette(
            sma, ecc, inc, raan, argp, ta,
            int(num_planes), int(sats_per_plane), int(molecule),
        )
        return self

    def rosette_by_seed(
        self,
        seed_sat_path: str,
        num_planes: int,
        sats_per_plane: int,
        molecule: float,
    ) -> "ConstellationDesigner":
        """以已有卫星为种子创建 Rosette 星座。"""
        self._design.ConstellDesignRosetteBySeed(
            seed_sat_path, int(num_planes), int(sats_per_plane),
            int(molecule),
        )
        return self

    # ------------------------------------------------------------------
    # Flower
    # ------------------------------------------------------------------

    def flower(
        self,
        sma: float,
        ecc: float,
        inc: float,
        raan: float,
        argp: float,
        ta: float,
        return_circle: float,
        return_day: float,
        phase_density: float,
        inter_plane_spacing: float,
        num_sats: int,
        raan_spread: float,
    ) -> "ConstellationDesigner":
        """
        按轨道六要素创建 Flower（花瓣）星座。

        Parameters
        ----------
        return_circle, return_day : float
            回归圈数与回归天数。
        phase_density : float
            相位密度。
        inter_plane_spacing : float
            面间间距（度）。
        num_sats : int
            卫星总数。
        raan_spread : float
            升交点赤经分布（度）。
        """
        # SWIG typemap：returnCircle/returnDay/phaseDensity/interPlaneSpacing 为 int 参数
        self._design.ConstellDesignFlower(
            sma, ecc, inc, raan, argp, ta,
            int(return_circle), int(return_day), int(phase_density),
            int(inter_plane_spacing), int(num_sats), raan_spread,
        )
        return self

    def flower_by_seed(
        self,
        seed_sat_path: str,
        return_circle: float,
        return_day: float,
        phase_density: float,
        inter_plane_spacing: float,
        num_sats: int,
        raan_spread: float,
    ) -> "ConstellationDesigner":
        """以已有卫星为种子创建 Flower 星座。"""
        self._design.ConstellDesignFlowerBySeed(
            seed_sat_path, int(return_circle), int(return_day),
            int(phase_density), int(inter_plane_spacing),
            int(num_sats), raan_spread,
        )
        return self

    # ------------------------------------------------------------------
    # AsymmetricFlower（非对称 Flower）
    # ------------------------------------------------------------------

    def asymmetric_flower(
        self,
        sma: float,
        ecc: float,
        inc: float,
        raan: float,
        argp: float,
        ta: float,
        return_circle: float,
        return_day: float,
        num_sats: int,
        raan_increment: float,
    ) -> "ConstellationDesigner":
        """按轨道六要素创建非对称 Flower 星座。"""
        self._design.ConstellDesignNonSymFlower(
            sma, ecc, inc, raan, argp, ta,
            int(return_circle), int(return_day), int(num_sats),
            raan_increment,
        )
        return self

    def asymmetric_flower_by_seed(
        self,
        seed_sat_path: str,
        return_circle: float,
        return_day: float,
        num_sats: int,
        raan_increment: float,
    ) -> "ConstellationDesigner":
        """以已有卫星为种子创建非对称 Flower 星座。"""
        self._design.ConstellDesignNonSymFlowerBySeed(
            seed_sat_path, int(return_circle), int(return_day),
            int(num_sats), raan_increment,
        )
        return self
