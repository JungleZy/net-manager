import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_create_daemon_script_linux_chmod_error():
    from src.system.autostart import _create_daemon_script_linux

    with patch(
        "src.system.autostart.get_client_executable_path",
        return_value="/usr/bin/client",
    ), patch(
        "src.system.autostart.get_appropriate_encoding", return_value="utf-8"
    ), patch(
        "src.system.autostart.os.chmod", side_effect=OSError("x")
    ):
        p = _create_daemon_script_linux()
        assert p is None
