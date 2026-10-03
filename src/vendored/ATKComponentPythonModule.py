"""
ATKComponentPythonModule 的测试替身（stub）。

在没有 ATK 安装的环境下允许导入 component 模块：
提供最小化的 mock 枚举和 IAtkObjectRoot 类。
真实运行时请使用 ATK 安装目录中的官方模块。
"""

from __future__ import annotations

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

    def GetBatchCrdnTransform(self):
        return MagicMock()

    def GetCat(self):
        return MagicMock()

    def GetConstellDesign(self):
        return MagicMock()



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


# ---------------------------------------------------------------------------
# 4.2 新增：指针助手 / SWIG 向量替身 / 新枚举
# ---------------------------------------------------------------------------


class _Ptr:
    """int_p / double_p 的最小替身：可写可读。"""

    def __init__(self, value=0):
        self.value = value


def new_int_p():
    return _Ptr(0)


def copy_int_p(value):
    return _Ptr(value)


def int_p_assign(obj, value):
    obj.value = value


def int_p_value(obj):
    return obj.value


def new_double_p():
    return _Ptr(0.0)


def copy_double_p(value):
    return _Ptr(value)


def double_p_assign(obj, value):
    obj.value = value


def double_p_value(obj):
    return obj.value


class _SwigVector(list):
    """SWIG 向量的最小替身：支持 push_back / 迭代 / len。"""

    def push_back(self, x):
        self.append(x)


def vector_string():
    return _SwigVector()


def vector_double():
    return _SwigVector()


def vector_EDataSequence():
    return _SwigVector()


# 可见性报告类型（名称与官方模块枚举一致）
eACCESS_ERROR_REP = "eACCESS_ERROR_REP"
eACCESS_INTRVL_REP = "eACCESS_INTRVL_REP"
eACCESS_AER_REP = "eACCESS_AER_REP"
eACCESS_AER_RATE_REP = "eACCESS_AER_RATE_REP"
eNACCESS_INTRVL_REP = "eNACCESS_INTRVL_REP"
eNACCESS_AER_REP = "eNACCESS_AER_REP"
eACCESS_COMM_REP = "eACCESS_COMM_REP"
eACCESS_SUMMARY_REP = "eACCESS_SUMMARY_REP"
eACCESS_AER_SUMMARY_REP = "eACCESS_AER_SUMMARY_REP"
eNACCESS_SUMMARY_REP = "eNACCESS_SUMMARY_REP"
eACCESS_INTRVL_REP_ELAPSED = "eACCESS_INTRVL_REP_ELAPSED"
eNACCESS_INTRVL_REP_ELAPSED = "eNACCESS_INTRVL_REP_ELAPSED"
eACCESS_SUMMARY_REP_ELAPSED = "eACCESS_SUMMARY_REP_ELAPSED"
eNACCESS_SUMMARY_REP_ELAPSED = "eNACCESS_SUMMARY_REP_ELAPSED"
eACCESS_RANGE_RATE_REP = "eACCESS_RANGE_RATE_REP"
eACCESS_HLANGLE_REP = "eACCESS_HLANGLE_REP"
eACCESS_AZIMUTHANGLE_REP = "eACCESS_AZIMUTHANGLE_REP"
eACCESS_DISTANCE_REP = "eACCESS_DISTANCE_REP"
eACCESS_ANGLERATE_REP = "eACCESS_ANGLERATE_REP"
eACCESS_ANGLEPOLAR_REP = "eACCESS_ANGLEPOLAR_REP"
eACCESS_BIE_REP = "eACCESS_BIE_REP"
eACCESS_TASKBIE_REP = "eACCESS_TASKBIE_REP"
eACCESS_CUSTOM_REP = "eACCESS_CUSTOM_REP"

# VGT 组件类型（新模块引用到的值）
eCrdnVectorTypeDisplacement = "eCrdnVectorTypeDisplacement"
eCrdnVectorTypeCrossProduct = "eCrdnVectorTypeCrossProduct"
eCrdnAngleTypeBetweenVectors = "eCrdnAngleTypeBetweenVectors"

# 批量坐标转换：时间类型与文件类型
eUTCTIME = "eUTCTIME"
eRELATIVETIME = "eRELATIVETIME"
eTxt = "eTxt"
eEPHEMERIS = "eEPHEMERIS"
