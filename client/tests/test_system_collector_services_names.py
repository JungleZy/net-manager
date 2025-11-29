import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class Conn:
    def __init__(self, status, ip, port, pid):
        self.status = status
        self.laddr = SimpleNamespace(ip=ip, port=port)
        self.pid = pid

def test_get_services_tcp_udp_with_process_names():
    from src.system.system_collector import SystemCollector
    import psutil
    tcp = [Conn(psutil.CONN_LISTEN, "0.0.0.0", 8080, 123)]
    udp = [Conn("", "127.0.0.1", 5353, 123)]
    with patch("src.system.system_collector.psutil.net_connections", side_effect=[tcp, udp]), \
         patch("src.system.system_collector.psutil.Process") as P:
        P.return_value.name.return_value = "proc123"
        sc = SystemCollector()
        services = sc.get_services()
        assert any(s.get("process_name") == "proc123" for s in services)
