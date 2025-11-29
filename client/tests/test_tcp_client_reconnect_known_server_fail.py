import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_reconnect_known_server_connect_fail():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.server_ip = "127.0.0.1"
    c.server_port = 1234
    with patch("src.network.tcp_client.time.sleep", return_value=None), patch.object(
        TCPClient, "connect", return_value=False
    ):
        c.stop_event.set()
        c._reconnect()


class DummyDgram:
    def __init__(self, *a, **k):
        pass

    def settimeout(self, t):
        pass

    def bind(self, addr):
        pass

    def setsockopt(self, *a, **k):
        pass

    def sendto(self, data, addr):
        pass

    def recvfrom(self, n):
        import json

        msg = json.dumps(
            {
                "type": "discovery_response",
                "server_ip": "127.0.0.1",
                "server_port": 1234,
            }
        ).encode("utf-8")
        return (msg, ("127.0.0.1", 1234))

    def close(self):
        pass


def test_reconnect_via_last_interface_success():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.server_ip = "0.0.0.0"
    c.server_port = 1111
    c.last_successful_interface = {"name": "eth0", "ip": "127.0.0.1"}
    with patch("src.network.tcp_client.time.sleep", return_value=None), patch(
        "src.network.tcp_client.socket.socket", return_value=DummyDgram()
    ), patch.object(TCPClient, "connect", return_value=True):
        c._reconnect()
    assert c.server_ip == "127.0.0.1" and c.server_port == 1234
