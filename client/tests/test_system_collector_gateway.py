import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_windows_gateway_powershell_success():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    with patch("src.system.system_collector.subprocess.run", return_value=MagicMock(returncode=0, stdout="192.168.0.1\n")):
        gw = sc._get_windows_gateway("192.168.0.2")
        assert gw == "192.168.0.1"

def test_windows_gateway_netstat_fallback():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    def side_effect(cmd, capture_output=True, text=True, timeout=5):
        if cmd[:2] == ["powershell", "-Command"]:
            return MagicMock(returncode=1, stdout="")
        if cmd[0] == "netstat":
            return MagicMock(returncode=0, stdout="\n0.0.0.0         0.0.0.0         192.168.0.1    0  0  0\n")
        return MagicMock(returncode=1, stdout="")
    with patch("src.system.system_collector.subprocess.run", side_effect=side_effect):
        gw = sc._get_windows_gateway("192.168.0.2")
        assert gw == "192.168.0.1"

def test_linux_gateway_ip_route_success():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    with patch("src.system.system_collector.subprocess.run", return_value=MagicMock(returncode=0, stdout="default via 192.168.0.1 dev eth0\n")):
        gw = sc._get_linux_gateway()
        assert gw == "192.168.0.1"

def test_linux_gateway_route_n_fallback():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    def side_effect(cmd, capture_output=True, text=True, timeout=5):
        if cmd[0] == "ip":
            return MagicMock(returncode=0, stdout="\n")
        if cmd[0] == "route" and cmd[1] == "-n":
            return MagicMock(returncode=0, stdout="0.0.0.0 192.168.0.1 0.0.0.0  UG  0  0  0 eth0\n")
        return MagicMock(returncode=1, stdout="")
    with patch("src.system.system_collector.subprocess.run", side_effect=side_effect):
        gw = sc._get_linux_gateway()
        assert gw == "192.168.0.1"

def test_linux_gateway_proc_net_route_parsing():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    fake_file = "Iface\tDestination\tGateway\neth0\t00000000\t0102A8C0\n"
    def side_effect(cmd, capture_output=True, text=True, timeout=5):
        return MagicMock(returncode=1, stdout="")
    with patch("src.system.system_collector.subprocess.run", side_effect=side_effect), \
         patch("builtins.open", new_callable=lambda: patch("builtins.open").start()) as _:
        # Use a simple context manager to return our fake content
        class DummyOpen:
            def __init__(self, *args, **kwargs): pass
            def __call__(self, *args, **kwargs): return self
            def __enter__(self):
                import io
                return io.StringIO(fake_file)
            def __exit__(self, *args): return False
        # Patch builtins.open to DummyOpen
        import builtins
        orig_open = builtins.open
        builtins.open = DummyOpen()
        try:
            gw = sc._get_linux_gateway()
            assert gw == "192.168.2.1"
        finally:
            builtins.open = orig_open
