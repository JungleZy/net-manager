import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_send_system_info_not_connected():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    c.connected = False
    assert c.send_system_info() is False
