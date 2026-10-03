"""
ATK Component 模式 SDK
======================
直接 DLL 访问，无需 ATK 软件运行。
通过 ATKComponentPythonModule 使用 ATK 的嵌入式 Python 环境。

用法::

    from atk.component import component_session

    with component_session() as session:
        scenario = session.new_scenario('MyScenario')
        sat_obj = session.create_satellite('Sat1')
        ...

注意：Component 模式需要 ATKComponentPythonModule.py 和
_ATKComponentPythonModule.pyd DLL 文件。这些文件必须与
ATKComponentPythonModule.py 位于同一目录（通常是 ATK 安装根目录）。
请将这两个文件复制到项目中或将 ATK 安装目录添加到路径。
"""

from atk.component.session import ComponentSession, component_session

# 4.2 新增分析工具（导入以触发生效，类经 ComponentSession 便捷方法使用）
from atk.component.access import AccessCalculator, AccessConstraints  # noqa: F401
from atk.component.cat import CatAdvanceConfig, CatAnalysis  # noqa: F401
from atk.component.constellation import ConstellationDesigner  # noqa: F401
from atk.component.coord import BatchCoordinateTransform  # noqa: F401
from atk.component.maneuver import (  # noqa: F401
    ManeuverDetectionAnalysis,
    TLEManeuverDetection,
)
from atk.component.vgt import VgtBuilder  # noqa: F401

__all__ = [
    "ComponentSession",
    "component_session",
    "AccessCalculator",
    "AccessConstraints",
    "CatAdvanceConfig",
    "CatAnalysis",
    "ConstellationDesigner",
    "BatchCoordinateTransform",
    "ManeuverDetectionAnalysis",
    "TLEManeuverDetection",
    "VgtBuilder",
]
