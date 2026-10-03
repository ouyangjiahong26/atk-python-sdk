"""问题 1 复现：IMnvPODDataBaseDetection.Compute 的 std::string& 出参
导致 Python 无法调用。

用法（wine，在 ATK 安装目录下运行）：
    wine Python/_internal/python.exe Z:\\<路径>\\repro1_pod_compute.py
"""

import sys

sys.path.insert(0, r"Z:\home\ouyangjiahong\codes\ATK\ATK-v4.2.0-alpha.1-windows-x64\ATK-4.2.0-alpha.1")

import ATKComponentPythonModule as ATK  # noqa: E402

root = ATK.IAtkObjectRoot()
root.NewScenario("ReproPOD")
sat = root.GetCurrentScenario().GetChildren().New(ATK.eSatellite, "Sat1")

pod = sat.GetManeuverDetection().GetPODDataBaseDetection()
pod.SetOrbitPropagator(ATK.ePropagatorTwoBody)
pod.SetObjectATime("1 Jul 2035 00:00:00.000")
pod.SetObjectAJ2000Frame(6678137.0, 0.0, 0.0, 0.0, 7545.8, 0.0)
pod.SetObjectBTime("1 Jul 2035 00:00:00.000")
pod.SetObjectBJ2000Frame(6678237.0, 0.0, 0.0, 0.0, 7545.3, 0.0)

n = ATK.new_int_p()
d = [ATK.new_double_p() for _ in range(7)]
vs = ATK.vector_string()
vd = ATK.vector_double()

# 依次尝试 Python 侧所有可能的字符串实参形态
for label, value in [
    ("str(\"\")", ""),
    ("None", None),
    ("bytes", b""),
    ("bytearray", bytearray()),
]:
    try:
        pod.Compute(n, value, *d, vs, vd)
        print(f"{label:12s} -> OK")
        break
    except TypeError as e:
        print(f"{label:12s} -> TypeError: {e}")

# 对照：同为机动检测的 TLE 变体 Compute 出参全为 vector，可正常调用
print("\n对照：IMnvTLEDataBaseDetection.Compute（出参 vector，正常）")
tle = sat.GetManeuverDetection().GetTLEDataBaseDetection()
times = ATK.vector_string()
times.push_back("1 Jul 2035 00:00:00.000")
outs = [ATK.vector_double() for _ in range(5)]
try:
    tle.Compute(times, *outs)
    print("TLE Compute -> OK（返回值正常读出）")
except TypeError as e:
    print(f"TLE Compute -> TypeError: {e}")

root.CloseScenario()
