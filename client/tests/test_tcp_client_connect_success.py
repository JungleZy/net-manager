import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


class DummySocket:
    def __init__(self, *a, **k):
        self.closed = False

    def settimeout(self, t):
        pass

    def setsockopt(self, *a, **k):
        pass

    def connect(self, addr):
        pass

    def sendall(self, data):
        pass

    def close(self):
        self.closed = True


class DummyThread:
    def __init__(self, target=None, daemon=None):
        self.target = target

    def start(self):
        pass

    def join(self, timeout=None):
        pass

    def is_alive(self):
        return False


def test_connect_success_with_handshake():
    from src.network.tcp_client import TCPClient

    with patch(
        "src.network.tcp_client.socket.socket", return_value=DummySocket()
    ), patch(
        "src.network.tcp_client.threading.Thread", return_value=DummyThread()
    ), patch.object(
        TCPClient, "_perform_handshake", return_value=True
    ):
        c = TCPClient()
        ok = c.connect(("127.0.0.1", 1234))
        assert ok
        assert c.connected
        c.disconnect()

def test_connect_no_address_returns_false():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    assert c.connect(None) is False

class DummySocket2:
    def __init__(self):
        pass
    def settimeout(self, t):
        pass
    def setsockopt(self, *a, **k):
        pass
    def connect(self, addr):
        pass
    def close(self):
        pass

def test_connect_handshake_fail():
    from src.network.tcp_client import TCPClient
    with __import__("unittest").mock.patch("src.network.tcp_client.socket.socket", return_value=DummySocket2()), \
         __import__("unittest").mock.patch.object(TCPClient, "_perform_handshake", return_value=False):
        c = TCPClient()
        ok = c.connect(("127.0.0.1", 1234))
        assert ok is False and c.socket is None
