"""Connect 集成测试的就绪探测（scripts/run_integration.sh 调用）。

只覆盖稳定的核心命令（场景/时间窗/卫星/传感器）；QuickReportCreate、
InsertSegment、AccessMulti 等 4.2 命令在 alpha 版存在非确定性 NACK
相位，由集成测试自身配合 runner 的重试机制覆盖。
"""

import socket
import sys

sys.path.insert(0, __file__.rsplit("/", 3)[0] + "/src")

# TCP 预检：atkOpen 对死端口也会成功，不能只依赖 SDK 连接
with socket.create_connection(("127.0.0.1", 6655), timeout=2):
    pass

from atk.connect import connect  # noqa: E402

with connect(retries=1) as atk:
    pong = atk.send_str("AllInstanceNames", "/")
    assert "Socket Error" not in pong, pong
    if pong.strip():
        atk.send("Unload", "/", "*")
    atk.send("New", "/", " Scenario ProbeReady")
    atk.send(
        "SetAnalysisTimePeriod", "*",
        ' "1 Jul 2035 00:00:00.000" "2 Jul 2035 00:00:00.000"',
    )
    atk.send("New", "/", " Satellite SatReady")
    atk.send("New", "/", " */Satellite/SatReady/Sensor SenReady")
    atk.send("Unload", "/", "*")
print("canary OK")
