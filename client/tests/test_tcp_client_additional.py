import os
import sys
from types import SimpleNamespace

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


class FakeSocket:
    def __init__(self):
        self.sent = []
        self.connected = True
        self._client = None

    def settimeout(self, t):
        return None

    def setsockopt(self, *args, **kwargs):
        return None

    def connect(self, addr):
        return None

    def sendall(self, data):
        self.sent.append(data)
        # trigger stop to exit loop after first send
        if self._client:
            self._client.stop_event.set()

    def recv(self, n):
        return b""

    def close(self):
        self.connected = False


def test_handshake_with_none_socket():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.socket = None
    assert not c._perform_handshake()


def test_disconnect_sends_message():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    s = FakeSocket()
    c.socket = s
    c.connected = True
    c.disconnect()
    assert len(s.sent) >= 1


def test_send_data_socket_none_breaks():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.connected = True
    c.socket = None
    c.send_buffer.append("hello")
    c._send_data()


def test_send_data_success_once():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    s = FakeSocket()
    s._client = c
    c.socket = s
    c.connected = True
    c.send_buffer.append("h")
    c._send_data()
    assert len(s.sent) >= 1
