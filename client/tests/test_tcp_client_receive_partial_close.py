import os
import sys
import struct
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class PartialSocket:
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

def test_receive_partial_and_close():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    msg = b"{}"
    frame = struct.pack("!I", 4) + msg  # length greater than payload
    c.socket = PartialSocket([frame, b""])
    c.connected = True
    with patch.object(c, "_handle_disconnect", side_effect=lambda: setattr(c, "connected", False)):
        c._receive_data()
