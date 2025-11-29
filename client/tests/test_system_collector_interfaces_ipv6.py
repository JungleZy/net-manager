import os
import sys
import socket
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_network_interfaces_with_ipv6_and_mac():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    initial = {"eth0": SimpleNamespace(bytes_sent=0, bytes_recv=0)}
    final = {"eth0": SimpleNamespace(bytes_sent=100, bytes_recv=200)}
    addrs = {
        "eth0": [
            SimpleNamespace(family=socket.AF_INET6, address="fe80::1"),
            SimpleNamespace(family=socket.AF_INET, address="192.168.0.2", netmask="255.255.255.0"),
            SimpleNamespace(family=__import__("psutil").AF_LINK, address="aa:bb:cc:dd:ee:ff"),
        ]
    }
    with patch("src.system.system_collector.psutil.net_io_counters", side_effect=[initial, final]), \
         patch("src.system.system_collector.psutil.net_if_addrs", return_value=addrs), \
         patch.object(SystemCollector, "_is_virtual_or_loopback_interface", return_value=False), \
         patch.object(SystemCollector, "get_ip_address", return_value="192.168.0.2"), \
         patch.object(SystemCollector, "get_gateway_and_netmask", return_value=("192.168.0.1", "255.255.255.0")):
        interfaces = sc.get_network_interfaces()
        i = interfaces[0]
        assert i["mac_address"] == "aa:bb:cc:dd:ee:ff" and i["upload_rate"] == 100 and i["download_rate"] == 200
