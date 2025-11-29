import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_get_network_interfaces_exception_returns_empty():
    from src.system.system_collector import SystemCollector

    with patch(
        "src.system.system_collector.psutil.net_io_counters", side_effect=Exception("x")
    ):
        sc = SystemCollector()
        interfaces = sc.get_network_interfaces()
        assert interfaces == []


def test_get_gateway_and_netmask_no_match_returns_empty():
    from src.system.system_collector import SystemCollector
    import socket
    from types import SimpleNamespace

    sc = SystemCollector()
    addrs = {
        "eth0": [
            SimpleNamespace(
                family=socket.AF_INET, address="10.0.0.2", netmask="255.255.255.0"
            )
        ]
    }
    with patch(
        "src.system.system_collector.psutil.net_if_addrs", return_value=addrs
    ), patch.object(
        SystemCollector, "get_ip_address", return_value="192.168.0.99"
    ), patch(
        "src.system.system_collector.platform.system", return_value="Linux"
    ):
        gw, nm = sc.get_gateway_and_netmask()
        assert gw in ("", "unknown") and nm in ("", "unknown")
