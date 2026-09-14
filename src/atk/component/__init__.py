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

__all__ = [
    "ComponentSession",
    "component_session",
]
