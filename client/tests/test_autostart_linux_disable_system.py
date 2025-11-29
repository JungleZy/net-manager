import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_disable_autostart_linux_system_exists():
    from src.system.autostart import _disable_autostart_linux
    def side_effect(cmd, capture_output=True, text=False, timeout=30):
        return MagicMock(returncode=0, stdout="")
    with patch("src.system.autostart.Path.exists", return_value=True), \
         patch("src.system.autostart.subprocess.run", side_effect=side_effect):
        ok = _disable_autostart_linux()
        assert ok
