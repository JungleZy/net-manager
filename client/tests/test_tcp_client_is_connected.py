import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_is_connected_false():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    assert c.is_connected() is False
