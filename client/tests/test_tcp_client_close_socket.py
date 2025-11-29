import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class S:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True

def test_close_socket_closes_and_nulls():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    s = S()
    c.socket = s
    c._close_socket()
    assert s.closed and c.socket is None
