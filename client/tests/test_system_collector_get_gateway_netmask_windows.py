import os
import sys
import socket
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_gateway_and_netmask_windows():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    addrs = {"Ethernet": [SimpleNamespace(family=socket.AF_INET, address="1.2.3.4", netmask="255.255.255.0")]}
    with patch("src.system.system_collector.psutil.net_if_addrs", return_value=addrs), \
         patch.object(SystemCollector, "get_ip_address", return_value="1.2.3.4"), \
         patch("src.system.system_collector.platform.system", return_value="Windows"), \
         patch.object(SystemCollector, "_get_windows_gateway", return_value="1.2.3.1"):
        gw, nm = sc.get_gateway_and_netmask()
        assert gw == "1.2.3.1" and nm == "255.255.255.0"
