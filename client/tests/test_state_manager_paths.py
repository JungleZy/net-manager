import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_application_path_packaged_windows():
    from src.core.state_manager import StateManager

    tmp_exec = Path(tempfile.mkdtemp(prefix="nm_pack_")) / "netmanager.exe"
    tmp_exec.parent.mkdir(parents=True, exist_ok=True)
    tmp_exec.write_text("", encoding="utf-8")
    try:
        with patch("src.core.state_manager.sys.frozen", True, create=True), patch(
            "src.core.state_manager.sys.executable", str(tmp_exec), create=True
        ):
            StateManager._instance = None
            sm = StateManager()
            assert sm.state_file.parent == tmp_exec.parent
    finally:
        shutil.rmtree(tmp_exec.parent)


def test_load_state_json_error_and_save_permission_error():
    from src.core.state_manager import StateManager

    td = Path(tempfile.mkdtemp(prefix="nm_state_"))
    try:
        (td / "client_state.json").write_text("{invalid", encoding="utf-8")
        with patch.object(StateManager, "_get_application_path", return_value=td):
            StateManager._instance = None
            sm = StateManager()
            assert isinstance(sm.state, dict)

        # simulate permission error during save
        def bad_open(*args, **kwargs):
            raise PermissionError("no")

        with patch.object(StateManager, "_get_application_path", return_value=td):
            StateManager._instance = None
            sm = StateManager()
            with patch("src.core.state_manager.open", side_effect=bad_open):
                ok = sm.set_state("x", 1)
                assert ok is False
    finally:
        shutil.rmtree(td)
