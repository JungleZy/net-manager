import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class ProcObj:
    def __init__(self, pid, name):
        self.info = {
            "pid": pid,
            "name": name,
            "username": "u",
            "cpu_percent": 1.2,
            "memory_percent": 2.3,
            "status": "running",
        }

def test_get_processes_sorted_path():
    from src.system.system_collector import SystemCollector
    procs = [ProcObj(100, "p1"), ProcObj(200, "p2")]
    conn = SimpleNamespace(status=patch("src.system.system_collector.psutil.CONN_LISTEN").start(), laddr=SimpleNamespace(ip="127.0.0.1", port=8080), type=patch("src.system.system_collector.socket.SOCK_STREAM").start())
    conn.status = __import__("psutil").CONN_LISTEN
    with patch("src.system.system_collector.psutil.process_iter", return_value=procs), \
         patch("src.system.system_collector.psutil.Process") as P:
        P.return_value.net_connections.return_value = [conn]
        sc = SystemCollector()
        out = sc.get_processes()
        assert any(p["pid"] == 100 for p in out)

def test_get_processes_fallback_path():
    from src.system.system_collector import SystemCollector
    procs = [ProcObj(300, "p3")]
    conn = SimpleNamespace(status=__import__("psutil").CONN_LISTEN, laddr=SimpleNamespace(ip="0.0.0.0", port=9090), type=patch("src.system.system_collector.socket.SOCK_STREAM").start())
    with patch("src.system.system_collector.psutil.process_iter", side_effect=Exception("boom")), \
         patch("src.system.system_collector.psutil.process_iter", return_value=procs), \
         patch("src.system.system_collector.psutil.Process") as P:
        P.return_value.net_connections.return_value = [conn]
        sc = SystemCollector()
        out = sc.get_processes()
        assert any(p["pid"] == 300 for p in out)
