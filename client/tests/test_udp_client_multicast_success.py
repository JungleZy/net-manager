import os
import sys
import json
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class FakeSendSock:
    def setsockopt(self, *a, **k):
        pass
    def sendto(self, data, addr):
        pass
    def close(self):
        pass

class FakeListenSock:
    def __init__(self):
        self.bound = None
    def setsockopt(self, *a, **k):
        pass
    def bind(self, addr):
        self.bound = addr
    def settimeout(self, t):
        pass
    def recvfrom(self, n):
        msg = json.dumps({"type":"discovery_response","tcp_port":4321}).encode("utf-8")
        return (msg, ("10.1.2.3", 37020))
    def close(self):
        pass

def test_discover_server_multicast_success_path():
    from src.network.udp_client import UDPClient
    u = UDPClient()
    with patch.object(UDPClient, "_validate_multicast_setup", return_value=(True, "")), \
         patch.object(UDPClient, "refresh_network_interfaces", return_value=[{"name":"eth0","ip":"192.168.0.2","netmask":"255.255.255.0","is_multicast_capable":True}]), \
         patch("src.network.udp_client.socket.socket", side_effect=[FakeSendSock(), FakeListenSock()]):
        out = u.discover_server_multicast()
        assert out == ("10.1.2.3", 4321)
