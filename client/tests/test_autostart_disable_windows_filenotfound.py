import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class Winreg:
    HKEY_CURRENT_USER = 0
    KEY_SET_VALUE = 0
    def OpenKey(self, *a, **k):
        return object()
    def DeleteValue(self, *a, **k):
        raise FileNotFoundError()
    def CloseKey(self, *a, **k):
        return None

def test_disable_autostart_windows_file_not_found_returns_true():
    from src.system.autostart import _disable_autostart_windows
    with patch.dict(sys.modules, {"winreg": Winreg()}):
        assert _disable_autostart_windows() is True
