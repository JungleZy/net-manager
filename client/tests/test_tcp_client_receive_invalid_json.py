import os
import sys
import struct

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class BadSocket:
    def __init__(self, frames):
        self.frames = frames
        self.i = 0
    def settimeout(self, t):
        pass
    def recv(self, n):
        if self.i < len(self.frames):
            d = self.frames[self.i]
            self.i += 1
            return d
        return b""

def test_receive_invalid_json():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    bad = b"\xff\xfe\xfd"
    frame = struct.pack("!I", len(bad)) + bad
    c.socket = BadSocket([frame, b""])
    c.connected = True
    c._receive_data()
