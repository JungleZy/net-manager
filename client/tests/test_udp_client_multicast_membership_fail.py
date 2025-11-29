import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class ListenSockFail:
    def setsockopt(self, level, optname, value):
        if level == __import__("socket").IPPROTO_IP and optname == __import__("socket").IP_ADD_MEMBERSHIP:
            raise OSError("fail membership")
    def bind(self, addr):
        pass
    def settimeout(self, t):
        pass
    def close(self):
        pass

class SendSockOk:
    def setsockopt(self, *a, **k):
        pass
    def sendto(self, *a, **k):
        pass
    def close(self):
        pass

def test_multicast_membership_fail_returns_none():
    from src.network.udp_client import UDPClient
    u = UDPClient()
    with patch.object(UDPClient, "_validate_multicast_setup", return_value=(True, "")), \
         patch.object(UDPClient, "refresh_network_interfaces", return_value=[]), \
         patch("src.network.udp_client.socket.socket", side_effect=[SendSockOk(), ListenSockFail()]):
        out = u.discover_server_multicast()
        assert out is None
