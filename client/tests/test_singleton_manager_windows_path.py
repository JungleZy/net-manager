import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_windows_lock_unavailable():
    import src.utils.singleton_manager as sm

    with patch.object(sm, "WIN32_AVAILABLE", False), patch(
        "src.utils.singleton_manager.platform.system", return_value="Windows"
    ):
        m = sm.SingletonManager()
        ok = m._acquire_windows_lock()
        assert ok is False
        m.lock_handle = 1
        m.lock_acquired = True
        m.release_lock()
        assert m.lock_handle is None
