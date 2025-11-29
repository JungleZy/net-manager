import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_enable_autostart_linux_user_service():
    from src.system.autostart import enable_autostart
    td = Path(tempfile.mkdtemp(prefix="nm_autostart_user_"))
    try:
        def side(cmd, capture_output=True, text=True, timeout=30):
            # systemctl --user commands succeed
            return MagicMock(returncode=0, stdout="ok", stderr="")
        with patch("src.system.autostart.platform.system", return_value="Linux"), \
             patch("src.system.autostart.get_client_executable_path", return_value="/usr/bin/netmanager"), \
             patch("src.system.autostart.os.geteuid", return_value=1, create=True), \
             patch("src.system.autostart._can_write_to_system_dir", return_value=False), \
             patch("src.system.autostart.Path.home", return_value=td), \
             patch("src.system.autostart.subprocess.run", side_effect=side):
            ok = enable_autostart(None)
            assert ok
            p = td / ".config" / "systemd" / "user" / "netmanager-client.service"
            assert p.exists()
    finally:
        shutil.rmtree(td)
