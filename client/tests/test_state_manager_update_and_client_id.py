import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_state_manager_update_and_client_id_generation():
    from src.core.state_manager import StateManager, get_state_manager
    td = Path(tempfile.mkdtemp(prefix="nm_state_mgr_"))
    try:
        with patch.object(StateManager, "_get_application_path", return_value=td):
            StateManager._instance = None
            # initialize
            sm = get_state_manager()
            assert isinstance(sm.get_state("client_id"), (str, type(None)))
            # update states
            ok = sm.update_states({"k1": "v1", "k2": 2})
            assert ok and sm.get_state("k1") == "v1"
            # client id generation
            StateManager._instance = None
            sm2 = StateManager()
            uid = sm2.get_client_id()
            assert isinstance(uid, str) and len(uid) > 0
    finally:
        shutil.rmtree(td)

def test_state_manager_set_state_failure_returns_false():
    from src.core.state_manager import StateManager
    td = Path(tempfile.mkdtemp(prefix="nm_state_mgr_fail_"))
    try:
        with patch.object(StateManager, "_get_application_path", return_value=td):
            StateManager._instance = None
            sm = StateManager()
            with patch.object(StateManager, "_save_state", side_effect=Exception("x")):
                ok = sm.set_state("x", 1)
                assert ok is False
    finally:
        shutil.rmtree(td)
