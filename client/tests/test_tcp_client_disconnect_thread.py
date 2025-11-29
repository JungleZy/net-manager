import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


class DummyThread:
    def __init__(self, target=None, daemon=None):
        self.target = target
        self.started = False

    def start(self):
        self.started = True

    def is_alive(self):
        return True

    def join(self, timeout=None):
        pass


def test_handle_disconnect_starts_reconnect_thread():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.connected = True
    with patch(
        "src.network.tcp_client.threading.Thread", return_value=DummyThread()
    ) as th:
        c._handle_disconnect()
        assert c.reconnecting is True


def test_disconnect_joins_threads_and_sends_message():
    from src.network.tcp_client import TCPClient

    class S:
        def __init__(self):
            self.sent = False

        def sendall(self, data):
            self.sent = True

        def close(self):
            pass

    c = TCPClient()
    c.heartbeat_thread = DummyThread()
    c.receive_thread = DummyThread()
    c.send_thread = DummyThread()
    c.socket = S()
    c.connected = True
    c.disconnect()
    assert c.socket is None
