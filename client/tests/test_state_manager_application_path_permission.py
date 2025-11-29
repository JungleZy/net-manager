import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_state_manager_application_path_permission_error():
    from src.core.state_manager import StateManager, StateManagerError
    with patch("src.core.state_manager.Path.mkdir", side_effect=PermissionError("no")):
        raised = False
        try:
            StateManager._instance = None
            StateManager()
        except StateManagerError:
            raised = True
        assert raised
