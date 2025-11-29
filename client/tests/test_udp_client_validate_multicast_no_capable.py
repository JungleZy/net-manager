import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_validate_multicast_no_multicast_capable_still_true():
    from src.network.udp_client import UDPClient
    u = UDPClient()
    # inject interfaces with capability False
    u._interfaces_cache = [{"name":"eth0","ip":"1.1.1.1","netmask":"255.255.255.0","is_multicast_capable":False}]
    ok, msg = u._validate_multicast_setup("239.255.1.1", 37020)
    assert ok is True
