import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_appropriate_encoding_windows():
    with patch("src.utils.platform_utils.is_windows", return_value=True):
        from src.utils.platform_utils import get_appropriate_encoding
        assert get_appropriate_encoding() == "gbk"

def test_get_appropriate_encoding_linux():
    with patch("src.utils.platform_utils.is_windows", return_value=False):
        from src.utils.platform_utils import get_appropriate_encoding
        assert get_appropriate_encoding() == "utf-8"

def test_create_platform_specific_directory():
    from pathlib import Path
    from src.utils.platform_utils import create_platform_specific_directory
    p = Path("./.tmp_platform_utils")
    try:
        ok = create_platform_specific_directory(str(p))
        assert ok
        assert p.exists()
    finally:
        if p.exists():
            for child in p.iterdir():
                child.unlink()
            p.rmdir()

def test_get_temp_directory_windows():
    with patch("src.utils.platform_utils.is_windows", return_value=True):
        with patch.dict(os.environ, {"TEMP": "C:/Temp"}):
            from src.utils.platform_utils import get_temp_directory
            assert get_temp_directory() == "C:/Temp"
