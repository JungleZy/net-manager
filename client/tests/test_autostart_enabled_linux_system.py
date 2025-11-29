import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_enable_autostart_linux_system_service():
    from src.system.autostart import enable_autostart

    def side_effect(cmd, capture_output=True, text=True, timeout=30):
        if cmd[:2] == ["sudo", "cp"]:
            return MagicMock(returncode=0, stdout="")
        if cmd[:2] == ["sudo", "chmod"]:
            return MagicMock(returncode=0, stdout="")
        if cmd[:3] == ["sudo", "systemctl", "daemon-reload"]:
            return MagicMock(returncode=0, stdout="")
        if cmd[:3] == ["sudo", "systemctl", "enable"]:
            return MagicMock(returncode=0, stdout="")
        if cmd[:3] == ["systemctl", "is-enabled", "netmanager-client.service"]:
            return MagicMock(returncode=0, stdout="enabled")
        return MagicMock(returncode=0, stdout="")

    with patch("src.system.autostart.platform.system", return_value="Linux"), patch(
        "src.system.autostart.os.geteuid", return_value=0, create=True
    ), patch(
        "src.system.autostart.get_client_executable_path",
        return_value="/usr/bin/netmanager",
    ), patch(
        "src.system.autostart.subprocess.run", side_effect=side_effect
    ):
        ok = enable_autostart(None)
        assert ok
