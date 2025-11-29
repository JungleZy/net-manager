import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


class DummyUDPNone:
    def discover_server_multicast(self):
        return None

    def discover_server_broadcast(self):
        return None


def test_discover_server_none():
    from src.network.tcp_client import TCPClient

    with patch("src.network.udp_client.get_udp_client", return_value=DummyUDPNone()):
        c = TCPClient()
        assert c.discover_server() is None


def test_handle_disconnect_command():
    from src.network.tcp_client import TCPClient

    c = TCPClient()
    c.connected = True
    with patch.object(c, "_handle_disconnect") as hd:
        c._handle_message({"type": "command", "command": "disconnect"})
        hd.assert_called()
