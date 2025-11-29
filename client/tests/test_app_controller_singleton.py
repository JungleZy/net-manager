import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_app_controller_singleton():
    from src.core.app_controller import get_app_controller
    a = get_app_controller()
    b = get_app_controller()
    assert a is b
