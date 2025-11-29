import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_create_platform_specific_directory_fail():
    from src.utils.platform_utils import create_platform_specific_directory
    with patch("src.utils.platform_utils.Path.mkdir", side_effect=Exception("x")):
        assert create_platform_specific_directory("./x") is False
