import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_executable_path_dev():
    from src.utils.platform_utils import get_executable_path
    old = sys.argv[0]
    try:
        sys.argv[0] = os.path.abspath(__file__)
        p = get_executable_path()
        assert isinstance(p, str)
    finally:
        sys.argv[0] = old
