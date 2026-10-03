"""问题 2 复现：Exec_Report 族命令 ACK 但不返回数据/不生成文件。

用法（Linux，ATK 已启动并监听 6655，启动加载完成后运行）：
    python3 repro2_exec_report.py /path/to/ATK-4.2.0-alpha.1
"""
import sys
import time

ATK_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
sys.path.insert(0, ATK_DIR)

import ATKConnectPython as C  # noqa: E402

HOST, PORT = "127.0.0.1", 6655
OUT_FILE = os.path.join(ATK_DIR, "repro_exec_report.out")

con = C.atkOpen(HOST, PORT)
print(f"atkOpen -> con_id={con}")


def send(command, input_str, delay=0.3):
    time.sleep(delay)
    r = C.atkConnect(con, command, input_str)
    text = r if isinstance(r, str) else str(getattr(r, "m_vectData", r))
    return text


# 前置：场景 + 时间窗 + 带轨道的卫星
send("New", "/ Scenario ReproExec")
send("SetAnalysisTimePeriod",
     '* "1 Jul 2035 00:00:00.000" "2 Jul 2035 00:00:00.000"')
send("New", "/ Satellite Sat1")
send("SetState", '*/Satellite/Sat1 Classical TwoBody '
     '"1 Jul 2035 00:00:00.000" "1 Jul 2035 00:00:00.000" 60 J2000 '
     '"1 Jul 2035 00:00:00.000" 6678.137 0.0 28.5 0.0 0.0 0.0')

print("--- Exec_Report_RM：返回空 ---")
r = send("Exec_Report_RM", '*/Satellite/Sat1 Style "Position" '
         'TimePeriod "1 Jul 2035 00:00:00.000" '
         '"1 Jul 2035 01:00:00.000" TimeStep 60')
print(f"Exec_Report_RM 响应: {r!r}（长度 {len(r)}）")

print("--- Exec_ReportCreate + File：ACK 但文件未生成 ---")
if os.path.exists(OUT_FILE):
    os.remove(OUT_FILE)
r = send("Exec_ReportCreate", '*/Satellite/Sat1 Style "Position" '
         f'File "{OUT_FILE}" TimePeriod "1 Jul 2035 00:00:00.000" '
         '"1 Jul 2035 01:00:00.000"')
print(f"Exec_ReportCreate 响应: {r!r}")
print(f"文件 {OUT_FILE} 存在: {os.path.exists(OUT_FILE)}")

print("--- 对照 QuickReport_RM GetReport：返回完整报告文本 ---")
send("QuickReportCreate", '* "J2000 Position Velocity"')
send("QuickReportAdd", '* Name "ReproQR" Type Report '
     'Style "J2000 Position Velocity" Object Satellite/Sat1')
r = send("QuickReport_RM", '* GetReport "ReproQR"')
head = r.strip().splitlines()[:3]
print(f"QuickReport_RM 响应前 3 行: {head}")

C.atkClose(con)
