import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_setup_signal_handlers_error_path():
    from src.core.app_controller import AppController
    with patch("src.core.app_controller.signal.signal", side_effect=Exception("boom")):
        c = AppController()
        # no exception propagated
        assert isinstance(c, AppController)
