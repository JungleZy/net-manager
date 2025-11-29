import os
import sys
import json
import struct
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class FakeRecvSocket:
    def __init__(self, frames):
        self.frames = frames
        self.idx = 0
        self.sent = []
    def settimeout(self, t):
        pass
    def recv(self, n):
        if self.idx < len(self.frames):
            data = self.frames[self.idx]
            self.idx += 1
            return data
        return b""
    def sendall(self, data):
        self.sent.append(data)

def test_receive_data_with_valid_frame_and_disconnect():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    msg = json.dumps({"type": "command", "command": "noop"}).encode("utf-8")
    frame = struct.pack("!I", len(msg)) + msg
    c.socket = FakeRecvSocket([frame, b""])
    c.connected = True
    called = {"count": 0}
    def handler(message):
        called["count"] += 1
    c.register_command_handler("noop", handler)
    with patch.object(c, "_handle_disconnect", side_effect=lambda: setattr(c, "connected", False)):
        c._receive_data()
    assert called["count"] == 1

def test_handle_message_unknown_and_known():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    called = {"hit": 0}
    c.register_command_handler("x", lambda m: called.__setitem__("hit", called["hit"] + 1))
    c._handle_message({"type": "command", "command": "x"})
    c._handle_message({"type": "unknown"})
    assert called["hit"] == 1

def test_send_system_info_appends_buffer():
    from src.network.tcp_client import TCPClient
    c = TCPClient()
    c.connected = True
    info = SimpleNamespace(
        client_id="cid",
        hostname="h",
        os_name="os",
        os_version="v",
        os_architecture="x64",
        machine_type="pc",
        services=[],
        processes=[],
        network_interfaces=[],
        cpu_info={},
        memory_info={},
        disk_info={},
        timestamp="t",
    )
    with patch.object(c.system_collector, "collect_system_info", return_value=info):
        ok = c.send_system_info()
    assert ok
    assert len(c.send_buffer) == 1
