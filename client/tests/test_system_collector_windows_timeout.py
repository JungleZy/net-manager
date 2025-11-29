import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_windows_gateway_timeout_returns_unknown():
    from src.system.system_collector import SystemCollector
    import subprocess
    sc = SystemCollector()
    def side(cmd, capture_output=True, text=True, timeout=5):
        raise subprocess.TimeoutExpired(cmd, timeout)
    with patch("src.system.system_collector.subprocess.run", side_effect=side):
        gw = sc._get_windows_gateway("1.2.3.4")
        assert gw == "unknown"
