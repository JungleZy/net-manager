import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class Bad:
    pass

def test_calculate_system_info_hash_error_returns_empty():
    from src.core.app_controller import AppController
    c = AppController()
    h = c._calculate_system_info_hash(Bad())
    assert h == ""
