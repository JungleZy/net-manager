import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_state_manager_save_chmod_warning_on_posix():
    from src.core.state_manager import StateManager
    td = Path(tempfile.mkdtemp(prefix="nm_state_chmod_"))
    try:
        with patch.object(StateManager, "_get_application_path", return_value=td), \
             patch("src.core.state_manager.os.name", "posix", create=True), \
             patch("src.core.state_manager.os.chmod", side_effect=OSError("x")):
            StateManager._instance = None
            sm = StateManager()
            ok = sm.set_state("k", "v")
            assert ok
    finally:
        shutil.rmtree(td)
