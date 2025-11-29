import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class GoodWinreg:
    HKEY_CURRENT_USER = 0
    KEY_SET_VALUE = 0
    REG_SZ = 1
    def OpenKey(self, *a, **k):
        return object()
    def SetValueEx(self, *a, **k):
        return None
    def CloseKey(self, *a, **k):
        return None

def test_enable_autostart_windows_success_path():
    from src.system.autostart import enable_autostart
    with __import__("unittest").mock.patch.dict(sys.modules, {"winreg": GoodWinreg()}), \
         __import__("unittest").mock.patch("src.system.autostart.platform.system", return_value="Windows"), \
         __import__("unittest").mock.patch("src.system.autostart.get_client_executable_path", return_value="C:/client.exe"):
        assert enable_autostart(None) is True
