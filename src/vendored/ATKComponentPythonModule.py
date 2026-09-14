"""
ATKComponentPythonModule 的测试替身（stub）。

在没有 ATK 安装的环境下允许导入 component 模块：
提供最小化的 mock 枚举和 IAtkObjectRoot 类。
真实运行时请使用 ATK 安装目录中的官方模块。
"""

from unittest.mock import MagicMock


class IAtkObjectRoot:
    """IAtkObjectRoot 的测试替身。"""

    def __init__(self):
        self._scenario = None

    def NewScenario(self, name: str):
        pass

    def GetCurrentScenario(self):
        return self._scenario

    def SetCurrentScenario(self, scenario):
        self._scenario = scenario

    def LoadScenario(self, path: str):
        pass

    def CloseScenario(self):
        self._scenario = None

    def SaveScenario(self, path: str | None = None):
        pass

    def GetObjectFromPath(self, path: str):
        return None

    def ObjectExists(self, path: str) -> bool:
        return False

    def GetAnimation(self):
        return MagicMock()

    def OutputDataReport(self, obj, report_type: str, start: str, stop: str, output_path: str | None = None):
        return output_path or "default_report.txt"


# Propagator enumerations
ePropagatorTwoBody = "ePropagatorTwoBody"
ePropagatorJ2Perturbation = "ePropagatorJ2Perturbation"
ePropagatorHPOP = "ePropagatorHPOP"
ePropagatorSGP4 = "ePropagatorSGP4"
ePropagatorStkExternal = "ePropagatorStkExternal"
ePropagatorAstromaster = "ePropagatorAstromaster"
ePropagatorGreatArc = "ePropagatorGreatArc"
ePropagatorSimpleAscent = "ePropagatorSimpleAscent"
ePropagatorJ4Perturbation = "ePropagatorJ4Perturbation"
ePropagatorVinti = "ePropagatorVinti"
ePropagatorBallistic = "ePropagatorBallistic"
ePropagatorLOP = "ePropagatorLOP"

# Object type enumerations
eSatellite = "eSatellite"
eScenario = "eScenario"
eFacility = "eFacility"
eSensor = "eSensor"
eCoverage = "eCoverage"

# 地面站坐标类型 EPositionType
eCartesian = "eCartesian"
eGeodetic = "eGeodetic"

# 欧拉旋转序列 EEulerOrientationSequence
e121 = "e121"
e123 = "e123"
e131 = "e131"
e132 = "e132"
e212 = "e212"
e213 = "e213"
e231 = "e231"
e232 = "e232"
e312 = "e312"
e313 = "e313"
e321 = "e321"
e323 = "e323"
