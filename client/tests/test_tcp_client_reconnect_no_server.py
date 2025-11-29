import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_reconnect_no_known_server_exits_quickly():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    c.server_ip = None
    c.server_port = None
    with patch("src.network.tcp_client.time.sleep", return_value=None):
        c.stop_event.set()
        c._reconnect()
