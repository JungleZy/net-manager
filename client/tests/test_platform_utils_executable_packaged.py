import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_executable_path_packaged():
    from src.utils.platform_utils import get_executable_path
    old_exec = sys.executable
    try:
        sys.executable = os.path.abspath(__file__)
        sys.frozen = True
        p = get_executable_path()
        assert isinstance(p, str)
    finally:
        sys.executable = old_exec
        if hasattr(sys, "frozen"):
            del sys.frozen
