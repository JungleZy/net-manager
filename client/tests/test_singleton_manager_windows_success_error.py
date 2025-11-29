import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_windows_lock_success_and_release():
    import src.utils.singleton_manager as sm
    with patch.object(sm, "WIN32_AVAILABLE", True), \
         patch("src.utils.singleton_manager.platform.system", return_value="Windows"), \
         patch("src.utils.singleton_manager.win32event.CreateMutex", return_value=123), \
         patch("src.utils.singleton_manager.win32api.GetLastError", return_value=0), \
         patch("src.utils.singleton_manager.win32api.CloseHandle") as ch:
        m = sm.SingletonManager()
        ok = m.acquire_lock()
        assert ok and m.lock_acquired and m.lock_handle == 123
        m.release_lock()
        ch.assert_called_with(123)
        assert not m.lock_acquired and m.lock_handle is None

def test_windows_lock_already_exists():
    import src.utils.singleton_manager as sm
    with patch.object(sm, "WIN32_AVAILABLE", True), \
         patch("src.utils.singleton_manager.platform.system", return_value="Windows"), \
         patch("src.utils.singleton_manager.win32event.CreateMutex", return_value=123), \
         patch("src.utils.singleton_manager.win32api.GetLastError", return_value=sm.winerror.ERROR_ALREADY_EXISTS), \
         patch("src.utils.singleton_manager.win32api.CloseHandle"):
        m = sm.SingletonManager()
        ok = m.acquire_lock()
        assert ok is False
        assert m.lock_handle is None

def test_unix_lock_open_failure():
    import src.utils.singleton_manager as sm
    with patch("src.utils.singleton_manager.platform.system", return_value="Linux"), \
         patch("src.utils.singleton_manager.os.open", side_effect=OSError("oops")):
        m = sm.SingletonManager()
        ok = m.acquire_lock()
        assert ok is False
