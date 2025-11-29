import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class FakeWinreg:
    HKEY_CURRENT_USER = 0
    KEY_SET_VALUE = 0
    KEY_READ = 0
    REG_SZ = 1
    def OpenKey(self, *args, **kwargs):
        return object()
    def SetValueEx(self, *args, **kwargs):
        return None
    def DeleteValue(self, *args, **kwargs):
        return None
    def QueryValueEx(self, *args, **kwargs):
        return ("C:/client.exe", None)
    def CloseKey(self, *args, **kwargs):
        return None

def test_enable_autostart_windows_success():
    with patch.dict(sys.modules, {"winreg": FakeWinreg()}), \
         patch("src.system.autostart.platform.system", return_value="Windows"), \
         patch("src.system.autostart.get_client_executable_path", return_value="C:/client.exe"):
        from src.system.autostart import enable_autostart
        ok = enable_autostart(None)
        assert ok

def test_disable_autostart_windows_success():
    with patch.dict(sys.modules, {"winreg": FakeWinreg()}), \
         patch("src.system.autostart.platform.system", return_value="Windows"):
        from src.system.autostart import disable_autostart
        ok = disable_autostart(None)
        assert ok

def test_is_autostart_enabled_windows_true():
    with patch.dict(sys.modules, {"winreg": FakeWinreg()}), \
         patch("src.system.autostart.platform.system", return_value="Windows"):
        from src.system.autostart import is_autostart_enabled
        ok = is_autostart_enabled()
        assert ok
