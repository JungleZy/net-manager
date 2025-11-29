import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_check_lock_status_windows_fields():
    import src.utils.singleton_manager as sm
    m = sm.SingletonManager()
    m.lock_handle = 1
    m.lock_file = "C:/tmp/x.lock"
    with patch("src.utils.singleton_manager.sys.platform", "win32"):
        s = m.check_lock_status()
        assert s.get("has_lock") is True and s.get("platform") == "win32" and isinstance(s.get("lock_name"), str)
