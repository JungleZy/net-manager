import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_autostart_unknown_platform():
    from src.system.autostart import enable_autostart, disable_autostart, is_autostart_enabled
    with patch("src.system.autostart.platform.system", return_value="Darwin"):
        assert enable_autostart(None) is False
        assert disable_autostart(None) is False
        assert is_autostart_enabled() is False
