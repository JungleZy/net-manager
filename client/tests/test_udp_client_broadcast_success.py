import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class DummySock:
    def __init__(self):
        self.bound = None
    def bind(self, addr):
        self.bound = addr
    def setsockopt(self, *a, **k):
        pass
    def settimeout(self, t):
        pass
    def sendto(self, data, addr):
        pass
    def recvfrom(self, n):
        return (b'{"type":"discovery_response","tcp_port":1234}', ("10.0.0.5", 9999))
    def close(self):
        pass

def test_broadcast_success_returns_server():
    from src.network.udp_client import UDPClient
    u = UDPClient()
    with patch.object(UDPClient, "refresh_network_interfaces", return_value=[{"name":"eth0","ip":"192.168.0.2","netmask":"255.255.255.0"}]), \
         patch("src.network.udp_client.socket.socket", return_value=DummySock()):
        out = u.discover_server_broadcast()
        assert out == ("10.0.0.5", 1234)
