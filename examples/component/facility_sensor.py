"""
ATK Component 模式 — 地面站与传感器示例

演示使用 Component 模式 API 创建地面站、设置位置、
配置圆锥视场传感器与固定欧拉角指向。

运行要求：
- 将 ATKComponentPythonModule.py 和 _ATKComponentPythonModule.pyd
  复制到 src/vendored/，或设置 ATK_ROOT 环境变量指向 ATK 安装目录。

用法：
    python examples/component/facility_sensor.py
"""

from atk.component import component_session
from atk.component.scenario import ScenarioBuilder
from atk.component.facility import FacilityBuilder


def main() -> None:
    with component_session() as session:
        print("[1] Component 会话已启动")

        # ---------------------------------------------------------------
        # 创建场景
        # ---------------------------------------------------------------
        scenario = ScenarioBuilder(session, session.new_scenario("FacilityDemo"))
        scenario.set_analysis_period(
            "1 Jan 2024 00:00:00.000",
            "2 Jan 2024 00:00:00.000",
        )
        print(f"[2] 场景已创建: {scenario.name}")

        # ---------------------------------------------------------------
        # 创建地面站并设置大地坐标位置
        # ---------------------------------------------------------------
        facility = FacilityBuilder(scenario.create_facility("Beijing"))
        facility.set_position_geodetic(lat=39.9, lon=116.4, alt=50)
        print(f"[3] 地面站已创建: {facility.path}")

        lat, lon, alt = facility.get_position_geodetic()
        print(f"    位置: lat={lat:.4f}, lon={lon:.4f}, alt={alt:.1f} m")

        # ---------------------------------------------------------------
        # 在地面站下创建圆锥视场传感器
        # ---------------------------------------------------------------
        sensor = facility.create_sensor("Sensor1")
        sensor.set_pattern_simple_conic(cone_angle=40, angular_resolution=0.5)
        sensor.point_fixed_euler(sequence=123, a=180, b=0, c=0)
        print(f"[4] 传感器已创建: {sensor.path}")
        print("    视场: 圆锥，半锥角 40 度")
        print("    指向: 固定欧拉角 (123 序列, 180, 0, 0)")

        # ---------------------------------------------------------------
        # 保存场景
        # ---------------------------------------------------------------
        scenario.save()
        print("\nComponent 模式地面站与传感器示例已完成！")


if __name__ == "__main__":
    main()
