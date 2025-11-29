import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_check_lock_status_lock_name_error():
    import src.utils.singleton_manager as sm
    m = sm.SingletonManager()
    with patch.object(sm.SingletonManager, "_get_lock_name", side_effect=Exception("x")):
        s = m.check_lock_status()
        assert "lock_name_error" in s
