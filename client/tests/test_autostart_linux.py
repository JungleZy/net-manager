import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_enable_autostart_linux_user_service_success():
    temp_dir = Path(tempfile.mkdtemp(prefix="netmanager_autostart_"))
    service_path = (
        temp_dir / ".config" / "systemd" / "user" / "netmanager-client.service"
    )
    try:
        from contextlib import ExitStack

        with ExitStack() as stack:
            mock_run = stack.enter_context(patch("src.system.autostart.subprocess.run"))
            stack.enter_context(
                patch("src.system.autostart.platform.system", return_value="Linux")
            )
            stack.enter_context(patch("pathlib.Path.home", return_value=temp_dir))
            stack.enter_context(
                patch(
                    "src.system.autostart.get_client_executable_path",
                    return_value="/usr/bin/netmanager",
                )
            )
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            from src.system.autostart import enable_autostart

            ok = enable_autostart(None)
            assert ok
            assert service_path.exists()
    finally:
        shutil.rmtree(temp_dir)


def test_disable_autostart_linux_success():
    temp_dir = Path(tempfile.mkdtemp(prefix="netmanager_autostart_"))
    service_path = (
        temp_dir / ".config" / "systemd" / "user" / "netmanager-client.service"
    )
    try:
        service_path.parent.mkdir(parents=True, exist_ok=True)
        service_path.write_text("x", encoding="utf-8")
        from contextlib import ExitStack

        with ExitStack() as stack:
            mock_run = stack.enter_context(patch("src.system.autostart.subprocess.run"))
            stack.enter_context(
                patch("src.system.autostart.platform.system", return_value="Linux")
            )
            stack.enter_context(patch("pathlib.Path.home", return_value=temp_dir))
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            from src.system.autostart import disable_autostart

            ok = disable_autostart(None)
            assert ok
            assert not service_path.exists()
    finally:
        shutil.rmtree(temp_dir)


def test_is_autostart_enabled_linux_true():
    temp_dir = Path(tempfile.mkdtemp(prefix="netmanager_autostart_"))
    try:

        def side_effect(cmd, capture_output=True, text=True, timeout=10):
            if cmd[:2] == ["systemctl", "is-enabled"]:
                return MagicMock(returncode=1, stdout="", stderr="")
            if cmd[:3] == ["systemctl", "--user", "is-enabled"]:
                return MagicMock(returncode=0, stdout="enabled", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        from contextlib import ExitStack

        with ExitStack() as stack:
            stack.enter_context(
                patch("src.system.autostart.platform.system", return_value="Linux")
            )
            stack.enter_context(patch("pathlib.Path.home", return_value=temp_dir))
            stack.enter_context(
                patch("src.system.autostart.subprocess.run", side_effect=side_effect)
            )
            from src.system.autostart import is_autostart_enabled

            ok = is_autostart_enabled()
            assert ok
    finally:
        shutil.rmtree(temp_dir)
