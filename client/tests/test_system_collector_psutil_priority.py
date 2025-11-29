import os
import sys
import socket
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_ip_via_psutil_priority_eth_over_wlan():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    addrs = {
        "eth0": [SimpleNamespace(family=socket.AF_INET, address="192.168.1.10")],
        "wlan0": [SimpleNamespace(family=socket.AF_INET, address="192.168.1.20")],
    }
    with patch("src.system.system_collector.psutil.net_if_addrs", return_value=addrs):
        ip = sc._get_ip_via_psutil()
        assert ip == "192.168.1.10"

def test_get_ip_via_gateway_linux_success():
    from src.system.system_collector import SystemCollector
    import subprocess
    sc = SystemCollector()
    def side(cmd, capture_output=True, text=True, timeout=5):
        if cmd[:3] == ["ip","route","show"]:
            return SimpleNamespace(returncode=0, stdout="default via 192.168.1.1 dev eth0\n")
        raise subprocess.TimeoutExpired(cmd, timeout)
    with patch("src.system.system_collector.platform.system", return_value="Linux"), \
         patch("src.system.system_collector.subprocess.run", side_effect=side), \
         patch("src.system.system_collector.socket.socket") as S:
        s = S.return_value.__enter__.return_value
        s.getsockname.return_value = ("192.168.1.100", 0)
        ip = sc._get_ip_via_gateway()
        assert ip == "192.168.1.100"
