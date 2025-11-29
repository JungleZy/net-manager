import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_get_state_manager_init_fail_raises():
    from src.core.state_manager import get_state_manager, StateManagerError
    import src.core.state_manager as sm

    sm._state_manager_instance = None
    with patch(
        "src.core.state_manager.StateManager.__init__", side_effect=Exception("boom")
    ):
        raised = False
        try:
            get_state_manager()
        except StateManagerError:
            raised = True
        assert raised
