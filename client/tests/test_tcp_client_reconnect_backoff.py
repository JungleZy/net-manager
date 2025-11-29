import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_reconnect_backoff_delays():
    from src.network.tcp_client import TCPClient
    delays = []
    def sleep_rec(d):
        delays.append(d)
        if len(delays) >= 2:
            c.stop_event.set()
    c = TCPClient()
    c.server_ip = "127.0.0.1"
    c.server_port = 1234
    with __import__("unittest").mock.patch("src.network.tcp_client.time.sleep", side_effect=sleep_rec), \
         __import__("unittest").mock.patch.object(TCPClient, "connect", return_value=False):
        c._reconnect()
    assert delays[:2] == [5, 10]
