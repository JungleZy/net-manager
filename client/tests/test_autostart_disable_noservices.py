import os
import sys
from unittest.mock import patch
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_disable_autostart_no_services_returns_true():
    from src.system.autostart import _disable_autostart_linux
    with patch("src.system.autostart.Path.exists", return_value=False):
        ok = _disable_autostart_linux()
        assert ok
