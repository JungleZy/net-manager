import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_acquire_lock_windows_exception_raises():
    import src.utils.singleton_manager as sm
    with patch("src.utils.singleton_manager.platform.system", return_value="Windows"), \
         patch.object(sm.SingletonManager, "_acquire_windows_lock", side_effect=Exception("x")):
        m = sm.SingletonManager()
        raised = False
        try:
            m.acquire_lock()
        except sm.SingletonManagerError:
            raised = True
        assert raised and m.lock_acquired is False
