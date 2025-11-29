import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class P:
    def __init__(self, pid, cpu):
        self.info = {
            "pid": pid,
            "name": f"p{pid}",
            "username": "u",
            "cpu_percent": cpu,
            "memory_percent": 0.1,
            "status": "running",
        }

def test_get_processes_limits_top_100_and_includes_ports():
    from src.system.system_collector import SystemCollector
    procs = [P(i, i % 50) for i in range(1, 121)]
    conn = SimpleNamespace(status=__import__("psutil").CONN_LISTEN, laddr=SimpleNamespace(ip="0.0.0.0", port=8080), type=__import__("socket").SOCK_STREAM)
    with patch("src.system.system_collector.psutil.process_iter", return_value=procs), \
         patch("src.system.system_collector.psutil.Process") as Pcls:
        Pcls.return_value.net_connections.return_value = [conn]
        sc = SystemCollector()
        out = sc.get_processes()
        assert len(out) <= 100
        assert any(p.get("listening_ports") for p in out)
