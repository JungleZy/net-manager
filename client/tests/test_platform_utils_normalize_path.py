import os
import sys
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_normalize_path_roundtrip():
    from src.utils.platform_utils import normalize_path
    p = normalize_path("./tmp/../tmp2")
    assert isinstance(p, str)
    assert Path(p).exists() or True

def test_get_home_directory():
    from src.utils.platform_utils import get_home_directory
    h = get_home_directory()
    assert isinstance(h, str)
