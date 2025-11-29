import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class BadWinreg2:
    HKEY_CURRENT_USER = 0
    KEY_SET_VALUE = 0
    def OpenKey(self, *a, **k):
        return object()
    def DeleteValue(self, *a, **k):
        raise OSError("fail")
    def CloseKey(self, *a, **k):
        return None

def test_disable_autostart_windows_fail():
    from src.system.autostart import _disable_autostart_windows
    with patch.dict(sys.modules, {"winreg": BadWinreg2()}):
        assert _disable_autostart_windows() is False
