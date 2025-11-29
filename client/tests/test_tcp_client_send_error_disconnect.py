import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class BadSock:
    def sendall(self, data):
        raise OSError("send fail")

def test_send_data_error_triggers_disconnect():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    c.socket = BadSock()
    c.connected = True
    c.send_buffer.append("hi")
    called = {"n":0}
    def hd():
        called["n"] += 1
        c.stop_event.set()
    c._handle_disconnect = hd
    c._send_data()
    assert called["n"] >= 1
