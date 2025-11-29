import os
import sys
from pathlib import Path
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_create_daemon_script_windows():
    from src.system.autostart import _create_daemon_script_windows

    with patch(
        "src.system.autostart.get_client_executable_path", return_value="C:/client.exe"
    ), patch("src.system.autostart.get_appropriate_encoding", return_value="utf-8"):
        p = _create_daemon_script_windows()
        assert p and Path(p).exists()
        Path(p).unlink(missing_ok=True)


def test_create_daemon_script_linux():
    from src.system.autostart import _create_daemon_script_linux

    with patch(
        "src.system.autostart.get_client_executable_path",
        return_value="/usr/bin/client",
    ), patch(
        "src.system.autostart.get_appropriate_encoding", return_value="utf-8"
    ), patch(
        "src.system.autostart.os.chmod", return_value=None
    ):
        p = _create_daemon_script_linux()
        assert p and Path(p).exists()
        Path(p).unlink(missing_ok=True)


def test_get_client_executable_path_error():
    from src.system.autostart import get_client_executable_path
    from src.exceptions.exceptions import AutoStartError

    with patch("src.system.autostart.get_executable_path", side_effect=Exception("x")):
        raised = False
        try:
            get_client_executable_path()
        except AutoStartError:
            raised = True
        assert raised


def test_create_daemon_script_dispatch_windows():
    from src.system.autostart import create_daemon_script

    with patch("src.system.autostart.platform.system", return_value="Windows"), patch(
        "src.system.autostart._create_daemon_script_windows", return_value="bat"
    ):
        p = create_daemon_script()
        assert p == "bat"


def test_create_daemon_script_dispatch_linux():
    from src.system.autostart import create_daemon_script

    with patch("src.system.autostart.platform.system", return_value="Linux"), patch(
        "src.system.autostart._create_daemon_script_linux", return_value="sh"
    ):
        p = create_daemon_script()
        assert p == "sh"
