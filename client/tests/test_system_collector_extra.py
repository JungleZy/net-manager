import os
import sys
import socket
import psutil
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_hex_to_ip_conversion():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    ip = sc._hex_to_ip("0102A8C0")
    assert ip == "192.168.2.1"


def test_is_valid_ip_edges():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    assert sc._is_valid_ip("192.168.0.1")
    assert not sc._is_valid_ip("127.0.0.1")
    assert not sc._is_valid_ip("0.1.2.3")
    assert not sc._is_valid_ip("256.0.0.1")


def test_get_gateway_and_netmask_linux():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    fake_addr = SimpleNamespace(
        family=socket.AF_INET, address="192.168.0.2", netmask="255.255.255.0"
    )
    with patch(
        "src.system.system_collector.psutil.net_if_addrs",
        return_value={"eth0": [fake_addr]},
    ), patch(
        "src.system.system_collector.platform.system", return_value="Linux"
    ), patch.object(
        SystemCollector, "get_ip_address", return_value="192.168.0.2"
    ), patch.object(
        SystemCollector, "_get_linux_gateway", return_value="192.168.0.1"
    ):
        gw, nm = sc.get_gateway_and_netmask()
        assert gw == "192.168.0.1"
        assert nm == "255.255.255.0"


def test_get_services_builds_tcp_and_udp_entries():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    tcp_conn = SimpleNamespace(
        status=MagicMock(), laddr=SimpleNamespace(ip="0.0.0.0", port=8080), pid=123
    )
    tcp_conn.status = psutil.CONN_LISTEN
    udp_conn = SimpleNamespace(
        laddr=SimpleNamespace(ip="127.0.0.1", port=5353), pid=None
    )
    with patch(
        "src.system.system_collector.psutil.net_connections",
        side_effect=[[tcp_conn], [udp_conn]],
    ), patch("src.system.system_collector.psutil.Process") as mock_proc:
        mock_proc.return_value.name.return_value = "proc123"
        services = sc.get_services()
        assert any(s["protocol"] == "TCP" for s in services)
        assert any(s["protocol"] == "UDP" for s in services)


def test_get_network_interfaces_basic():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    initial = {
        "eth0": SimpleNamespace(bytes_sent=100, bytes_recv=200),
        "lo": SimpleNamespace(bytes_sent=0, bytes_recv=0),
    }
    final = {
        "eth0": SimpleNamespace(bytes_sent=150, bytes_recv=300),
        "lo": SimpleNamespace(bytes_sent=0, bytes_recv=0),
    }
    addr_eth = [
        SimpleNamespace(family=psutil.AF_LINK, address="aa:bb:cc:dd:ee:ff"),
        SimpleNamespace(family=socket.AF_INET, address="192.168.0.2"),
    ]
    addr_lo = [SimpleNamespace(family=socket.AF_INET, address="127.0.0.1")]
    with patch(
        "src.system.system_collector.psutil.net_io_counters",
        side_effect=[initial, final],
    ), patch(
        "src.system.system_collector.psutil.net_if_addrs",
        return_value={"eth0": addr_eth, "lo": addr_lo},
    ), patch.object(
        SystemCollector,
        "_is_virtual_or_loopback_interface",
        side_effect=lambda name: name == "lo",
    ), patch.object(
        SystemCollector, "get_ip_address", return_value="192.168.0.2"
    ), patch.object(
        SystemCollector,
        "get_gateway_and_netmask",
        return_value=("192.168.0.1", "255.255.255.0"),
    ):
        interfaces = sc.get_network_interfaces()
        assert any(
            i["name"] == "eth0" and i["upload_rate"] == 50 and i["download_rate"] == 100
            for i in interfaces
        )
