import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class BadWinreg:
    HKEY_CURRENT_USER = 0
    KEY_SET_VALUE = 0
    REG_SZ = 1
    def OpenKey(self, *a, **k):
        return object()
    def SetValueEx(self, *a, **k):
        raise OSError("fail")
    def CloseKey(self, *a, **k):
        return None

def test_enable_autostart_windows_fail():
    from src.system.autostart import enable_autostart
    with patch.dict(sys.modules, {"winreg": BadWinreg()}), \
         patch("src.system.autostart.platform.system", return_value="Windows"), \
         patch("src.system.autostart.get_client_executable_path", return_value="C:/client.exe"):
        assert enable_autostart(None) is False
