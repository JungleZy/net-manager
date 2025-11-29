import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_check_lock_status_windows_open_process_paths():
    import src.utils.singleton_manager as sm

    m = sm.SingletonManager()
    m.lock_handle = 1
    m.lock_file = "C:/tmp/x.lock"
    with patch("src.utils.singleton_manager.sys.platform", "win32"), patch(
        "src.utils.singleton_manager.win32api.OpenProcess", side_effect=OSError()
    ):
        s = m.check_lock_status()
        assert s.get("process_exists") in (False, None)
