import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class BadWinreg:
    HKEY_CURRENT_USER = 0
    KEY_READ = 0
    def OpenKey(self, *a, **k):
        return object()
    def QueryValueEx(self, *a, **k):
        raise FileNotFoundError()
    def CloseKey(self, *a, **k):
        return None

def test_is_autostart_enabled_windows_false():
    from src.system.autostart import is_autostart_enabled
    with patch.dict(sys.modules, {"winreg": BadWinreg()}), \
         patch("src.system.autostart.platform.system", return_value="Windows"):
        ok = is_autostart_enabled()
        assert ok is False
