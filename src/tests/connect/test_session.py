"""
atk.connect.session 的单元测试 — ATKConnection 和 connect()。

使用 unittest.mock 模拟 SWIG 绑定。
"""

import pytest
from unittest.mock import MagicMock, patch

from atk import exceptions as atk_exc


class TestATKConnectionSend:
    """ATKConnection.send() 的测试。"""

    def test_send_calls_atkConnect_correctly(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_result = MagicMock()
            mock_result.m_vectData = "OK"
            mock_atk.atkConnect.return_value = mock_result

            from atk.connect.session import ATKConnection
            conn = ATKConnection(con_id=123, host="127.0.0.1", port=6655)
            result = conn.send("New", "*/Scenario/Sc1", "")

            mock_atk.atkConnect.assert_called_once_with(123, "New", "*/Scenario/Sc1")
            assert result is mock_result

    def test_send_passes_path_as_is(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_result = MagicMock()
            mock_result.m_vectData = "OK"
            mock_atk.atkConnect.return_value = mock_result

            from atk.connect.session import ATKConnection
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
            conn.send("New", "*/Satellite/Sat1", "")

            # send() 不再修改路径，调用者负责传入正确格式
            mock_atk.atkConnect.assert_called_once_with(1, "New", "*/Satellite/Sat1")

    def test_send_raises_when_closed(self) -> None:
        from atk.connect.session import ATKConnection
        from atk import exceptions as atk_exc

        conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
        conn._connected = False  # type: ignore[reportAttributeAccessIssue]

        with pytest.raises(atk_exc.ATKConnectionError, match="Connection is closed"):
            conn.send("New", "*", "")

    def test_send_raises_on_error_response(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_result = MagicMock()
            mock_result.m_vectData = "ERROR: Invalid command"
            mock_atk.atkConnect.return_value = mock_result

            from atk.connect.session import ATKConnection
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)

            with pytest.raises(atk_exc.ATKCommandError, match="New.*failed"):
                conn.send("New", "*", "")


class TestATKConnectionClose:
    """ATKConnection.close() 的测试。"""

    def test_close_calls_atkClose(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            from atk.connect.session import ATKConnection
            conn = ATKConnection(con_id=42, host="127.0.0.1", port=6655)
            conn.close()

            mock_atk.atkClose.assert_called_once_with(42)
            assert conn.is_connected is False

    def test_close_idempotent(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            from atk.connect.session import ATKConnection
            conn = ATKConnection(con_id=42, host="127.0.0.1", port=6655)
            conn._connected = False  # type: ignore[reportAttributeAccessIssue]

            conn.close()  # 不应再次调用 atkClose
            mock_atk.atkClose.assert_not_called()


class TestConnectionContextManager:
    """connect() 上下文管理器工厂的测试。"""

    def test_context_manager_closes_on_success(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_atk.atkOpen.return_value = 99

            from atk.connect.session import connect
            with connect() as conn:  # type: ignore[reportGeneralTypeIssues]
                assert conn.con_id == 99
                assert conn.is_connected is True

            mock_atk.atkClose.assert_called_once_with(99)

    def test_context_manager_closes_on_exception(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_atk.atkOpen.return_value = 99

            from atk.connect.session import connect
            with pytest.raises(RuntimeError):
                with connect():  # type: ignore[reportGeneralTypeIssues]
                    raise RuntimeError("test error")

            mock_atk.atkClose.assert_called_once_with(99)


class TestATKConnectionManager:
    """ATKConnectionManager 的测试。"""

    def test_retry_on_failure(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            # 失败两次，第三次成功
            mock_atk.atkOpen.side_effect = [Exception("fail1"), Exception("fail2"), 55]

            from atk.connect.session import ATKConnectionManager
            mgr = ATKConnectionManager(retries=3, backoff=0.01)
            conn = mgr.connect()

            assert mock_atk.atkOpen.call_count == 3
            assert conn.con_id == 55

    def test_exhausted_retries_raises(self) -> None:
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_atk.atkOpen.side_effect = Exception("always fails")

            from atk.connect.session import ATKConnectionManager
            from atk import exceptions as atk_exc

            mgr = ATKConnectionManager(retries=2, backoff=0.01)
            with pytest.raises(atk_exc.ATKConnectionError, match="Failed after 2 attempts"):
                mgr.connect()


class TestConnectionPatching:
    """Verify all submodules' monkey patches are correctly applied to ATKConnection."""

    def test_all_builder_methods_exist_on_connection(self):
        """Verify create_scenario, create_satellite, mcs_builder, create_facility, create_coverage all exist on ATKConnection."""
        from atk.connect import session
        expected_methods = [
            "create_scenario",
            "create_satellite",
            "mcs_builder",
            "create_facility",
            "create_coverage",
            "constellation_builder",
            "quick_report",
            "report_rm",
            # 4.2 newly added factories
            "access_builder",
            "access_multi",
            "coverage_multi",
            "vector_tool",
            "create_adv_cat",
            "constellation_creator",
            "quick_report_create",
            "quick_report_add",
            "quick_report_list",
            "quick_report_get",
            "exec_report_create",
            "exec_report_rm",
        ]
        for method_name in expected_methods:
            assert hasattr(session.ATKConnection, method_name), \
                f"ATKConnection missing method: {method_name}"


class TestSendRetryAndWaitReady:
    """send_retry / wait_ready（节流 + NACK 退避重试）的测试。"""

    def test_send_retry_returns_on_first_success(self) -> None:
        from unittest.mock import patch
        from atk.connect.session import ATKConnection
        with patch("atk.connect.session._ATK") as mock_atk:
            ok = MagicMock()
            ok.m_vectData = "ACK"
            mock_atk.atkConnect.return_value = ok
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
            result = conn.send_retry("New", "/", " Scenario S", interval=0.0)
            assert result is ok
            mock_atk.atkConnect.assert_called_once()

    def test_send_retry_retries_on_nack_then_raises(self) -> None:
        from unittest.mock import patch
        from atk.connect.session import ATKConnection
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_atk.atkConnect.return_value = "NACK"
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
            with pytest.raises(atk_exc.ATKCommandError):
                conn.send_retry(
                    "New", "/", " Scenario S", retries=2, interval=0.0
                )
            assert mock_atk.atkConnect.call_count == 3  # 1 + 2 重试

    def test_send_retry_recovers_after_transient_nack(self) -> None:
        from unittest.mock import patch
        from atk.connect.session import ATKConnection
        with patch("atk.connect.session._ATK") as mock_atk:
            ok = MagicMock()
            ok.m_vectData = "ACK"
            mock_atk.atkConnect.side_effect = ["NACK", "NACK", ok]
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
            result = conn.send_retry(
                "New", "/", " Scenario S", retries=3, interval=0.0
            )
            assert result is ok

    def test_wait_ready_returns_true_when_command_ok(self) -> None:
        from unittest.mock import patch
        from atk.connect.session import ATKConnection
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_atk.atkConnect.return_value = "Scenario1"
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
            assert conn.wait_ready(timeout=1.0, interval=0.0) is True

    def test_wait_ready_returns_false_on_timeout(self) -> None:
        from unittest.mock import patch
        from atk.connect.session import ATKConnection
        with patch("atk.connect.session._ATK") as mock_atk:
            mock_atk.atkConnect.return_value = "NACK"
            conn = ATKConnection(con_id=1, host="127.0.0.1", port=6655)
            assert conn.wait_ready(timeout=0.05, interval=0.0) is False
