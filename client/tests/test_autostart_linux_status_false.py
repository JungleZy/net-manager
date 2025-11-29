import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_is_autostart_enabled_linux_false():
    from src.system.autostart import is_autostart_enabled
    def side_effect(cmd, capture_output=True, text=True, timeout=10):
        return MagicMock(returncode=1, stdout="")
    with patch("src.system.autostart.platform.system", return_value="Linux"), \
         patch("src.system.autostart.subprocess.run", side_effect=side_effect):
        ok = is_autostart_enabled()
        assert ok is False
