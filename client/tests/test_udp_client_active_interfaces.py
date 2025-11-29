import os
import sys
import socket
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_get_active_interfaces_filters_loopback_and_calls_multicast_check():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    from types import SimpleNamespace

    stats = {
        "eth0": SimpleNamespace(isup=True, is_loopback=False),
        "lo": SimpleNamespace(isup=True, is_loopback=True),
    }
    addrs = {
        "eth0": [
            MagicMock(
                family=socket.AF_INET, address="192.168.0.2", netmask="255.255.255.0"
            )
        ],
        "lo": [
            MagicMock(family=socket.AF_INET, address="127.0.0.1", netmask="255.0.0.0")
        ],
    }
    fake_psutil = type("PS", (), {})()
    fake_psutil.net_if_stats = lambda: stats
    fake_psutil.net_if_addrs = lambda: addrs
    with patch("src.network.udp_client.psutil", fake_psutil), patch.object(
        UDPClient, "_check_interface_multicast_capability", return_value=True
    ) as chk:
        interfaces = u._get_active_interfaces()
        assert any(i["name"] == "eth0" for i in interfaces)
        assert all(i["ip"] != "127.0.0.1" for i in interfaces)
        chk.assert_called()
