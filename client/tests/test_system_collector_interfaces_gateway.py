import os
import sys
import socket
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_interfaces_gateway_assigned_for_current_ip_only():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    initial = {
        "eth0": SimpleNamespace(bytes_sent=100, bytes_recv=200),
        "eth1": SimpleNamespace(bytes_sent=50, bytes_recv=50),
    }
    final = {
        "eth0": SimpleNamespace(bytes_sent=150, bytes_recv=300),
        "eth1": SimpleNamespace(bytes_sent=55, bytes_recv=60),
    }
    addrs = {
        "eth0": [SimpleNamespace(family=socket.AF_INET, address="192.168.0.2"), SimpleNamespace(family=__import__("psutil").AF_LINK, address="aa")],
        "eth1": [SimpleNamespace(family=socket.AF_INET, address="10.0.0.2"), SimpleNamespace(family=__import__("psutil").AF_LINK, address="bb")],
    }
    with patch("src.system.system_collector.psutil.net_io_counters", side_effect=[initial, final]), \
         patch("src.system.system_collector.psutil.net_if_addrs", return_value=addrs), \
         patch.object(SystemCollector, "get_ip_address", return_value="192.168.0.2"), \
         patch.object(SystemCollector, "get_gateway_and_netmask", return_value=("192.168.0.1", "255.255.255.0")):
        interfaces = sc.get_network_interfaces()
        e0 = next(i for i in interfaces if i["name"] == "eth0")
        e1 = next(i for i in interfaces if i["name"] == "eth1")
        assert e0["gateway"] == "192.168.0.1" and e0["netmask"] == "255.255.255.0"
        assert e1["gateway"] == "" and e1["netmask"] == ""
