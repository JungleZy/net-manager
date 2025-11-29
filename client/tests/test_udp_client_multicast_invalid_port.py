import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_validate_multicast_invalid_low_port():
    from src.network.udp_client import UDPClient
    u = UDPClient()
    ok, msg = u._validate_multicast_setup("239.255.1.1", 0)
    assert ok is False
