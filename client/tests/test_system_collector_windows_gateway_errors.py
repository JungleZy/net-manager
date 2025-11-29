import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_windows_gateway_powershell_error_netstat_parse():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    def side(cmd, capture_output=True, text=True, timeout=5):
        if cmd[:2] == ["powershell", "-Command"]:
            return MagicMock(returncode=1, stdout="")
        if cmd[0] == "netstat":
            return MagicMock(returncode=0, stdout="\n0.0.0.0         0.0.0.0         10.0.0.1    0  0  0\n")
        return MagicMock(returncode=1, stdout="")
    with patch("src.system.system_collector.subprocess.run", side_effect=side):
        gw = sc._get_windows_gateway("10.0.0.2")
        assert gw == "10.0.0.1"
