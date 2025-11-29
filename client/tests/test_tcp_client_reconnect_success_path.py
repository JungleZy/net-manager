import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


class Dgram:
    def __init__(self):
        pass

    def settimeout(self, t):
        pass

    def bind(self, addr):
        pass

    def setsockopt(self, *a, **k):
        pass

    def sendto(self, *a, **k):
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


def test_reconnect_success_updates_state_and_stops():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.server_ip = "0.0.0.0"
    c.server_port = 1111
    c.last_successful_interface = {"name": "eth0", "ip": "127.0.0.1"}
    with patch(
        "src.network.tcp_client.socket.socket", return_value=Dgram()
    ), patch.object(TCPClient, "connect", return_value=True), patch(
        "src.network.tcp_client.time.sleep", side_effect=lambda d: None
    ):
        c._reconnect()
    assert c.server_ip == "127.0.0.1" and c.server_port == 1234
