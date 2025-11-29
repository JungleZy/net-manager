import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_validate_multicast_invalid_ip_and_port():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    ok, msg = u._validate_multicast_setup("1.2.3.4", 37020)
    assert ok is False
    ok2, msg2 = u._validate_multicast_setup("239.255.1.1", 70000)
    assert ok2 is False


def test_validate_multicast_no_interfaces():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    with patch.object(UDPClient, "_get_active_interfaces", return_value=[]):
        ok, msg = u._validate_multicast_setup("239.255.1.1", 37020)
        assert ok is False


def test_check_interface_multicast_windows_true():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    with patch("src.network.udp_client.platform.system", return_value="Windows"), patch(
        "subprocess.run", return_value=MagicMock(returncode=0, stdout="True")
    ):
        assert u._check_interface_multicast_capability("eth0") is True


def test_check_interface_multicast_linux_true():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    fake_file = "Inter-|   Receive                                                |  Transmit\neth0: 0 0 0 0 0 0 0 0 0 0\n"

    class DummyOpen:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return self

        def __enter__(self):
            import io

            return io.StringIO(fake_file)

        def __exit__(self, *args):
            return False

    import builtins

    orig_open = builtins.open
    try:
        with patch("src.network.udp_client.platform.system", return_value="Linux"):
            builtins.open = DummyOpen()
            assert u._check_interface_multicast_capability("eth0") is True
    finally:
        builtins.open = orig_open


def test_discover_multicast_fallback_to_broadcast():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    with patch.object(
        UDPClient, "_validate_multicast_setup", return_value=(False, "bad")
    ), patch.object(
        UDPClient, "discover_server_broadcast", return_value=("1.2.3.4", 1234)
    ):
        assert u.discover_server_multicast() == ("1.2.3.4", 1234)


def test_broadcast_no_interfaces_returns_none():
    from src.network.udp_client import UDPClient

    u = UDPClient()
    with patch.object(UDPClient, "refresh_network_interfaces", return_value=[]):
        assert u.discover_server_broadcast() is None
