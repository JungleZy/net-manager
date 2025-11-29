import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_disable_autostart_linux_systemctl_fail_returns_false():
    from src.system.autostart import _disable_autostart_linux

    def side(cmd, capture_output=True, text=True, timeout=30):
        return MagicMock(returncode=1, stdout="", stderr="")

    with patch("src.system.autostart.Path.exists", return_value=True), patch(
        "src.system.autostart.subprocess.run", side_effect=side
    ):
        assert _disable_autostart_linux() is True
