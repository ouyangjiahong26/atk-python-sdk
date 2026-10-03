"""Connect 集成测试共享 fixture。

- ``atk``：每用例独立短连接，建立后做命令就绪重试。
- 命令节流 + NACK 自动重试：Connect 服务端对命令速率敏感（连发
  NACK），且启动加载完成前部分命令暂不可用（NACK）。沿用项目既有
  方案（应用层 sleep 控制发送频率 + 启动等待），对每条命令间隔
  200ms，NACK 时按 1s 退避自动重试，规避启动加载窗口。
"""

import time

import pytest

from atk import exceptions as _ex
from atk.connect import connect

HOST = "127.0.0.1"
PORT = 6655

# 命令间隔（秒）与 NACK 重试参数
SEND_INTERVAL = 0.2
SEND_RETRIES = 10
SEND_BACKOFF = 1.0


@pytest.fixture
def atk():
    """每用例独立短连接（长连接遇重计算命令可能挂起）。"""
    from atk.connect.session import ATKConnection

    # 就绪重试：TCP 可连早于命令就绪，且偶发 "Socket Error" 相位
    conn = None
    cm = None
    last_pong = ""
    deadline = time.time() + 90
    while time.time() < deadline:
        try:
            cm = connect(HOST, PORT, retries=1)
            candidate = cm.__enter__()
            pong = candidate.send_str("AllInstanceNames", "/")
            if "Socket Error" not in pong:
                conn = candidate
                break
            last_pong = pong
        except Exception:
            cm = None
        if conn is None and cm is not None:
            try:
                cm.__exit__(None, None, None)
            except Exception:
                pass
            cm = None
        if conn is not None:
            break
        time.sleep(2)
    if conn is None:
        pytest.fail(
            f"ATK 90 秒内未就绪（最后响应：{last_pong!r}）："
            "请确认 ATK 已启动且完成初始化"
        )

    # 命令节流 + NACK 自动重试：类级包装 send（ATKConnection 有
    # __slots__，不能打实例补丁；类级可覆盖 builder 内部的 conn.send）
    original_send = ATKConnection.send

    def throttled_send(self, command, obj_path="*", param=""):
        last_exc = None
        for _ in range(SEND_RETRIES + 1):
            time.sleep(SEND_INTERVAL)
            try:
                return original_send(self, command, obj_path, param)
            except _ex.ATKCommandError as exc:
                last_exc = exc
                # 启动加载窗口的暂不可用：退避后重试
                time.sleep(SEND_BACKOFF)
        raise last_exc

    ATKConnection.send = throttled_send
    try:
        yield conn
    finally:
        ATKConnection.send = original_send
        conn.close()


@pytest.fixture(autouse=True)
def _clean_scene(atk):
    """每个用例前后卸载当前场景（ATK 同时只允许加载一个场景）。"""
    if atk.send_str("AllInstanceNames", "/").strip():
        atk.send("Unload", "/", "*")
    yield
    if atk.send_str("AllInstanceNames", "/").strip():
        atk.send("Unload", "/", "*")
