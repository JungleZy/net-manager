import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_can_write_to_system_dir_true_and_false():
    from src.system.autostart import _can_write_to_system_dir
    with patch("src.system.autostart.subprocess.run", return_value=MagicMock(returncode=0)):
        assert _can_write_to_system_dir() is True
    with patch("src.system.autostart.subprocess.run", side_effect=Exception("x")):
        assert _can_write_to_system_dir() is False
