import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_start_stop_wait_flow():
    from src.core.app_controller import AppController
    c = AppController()
    with patch("src.core.app_controller.AppController._connect_to_server_with_retry", return_value=False):
        c.start()
        c.stop()
        c.wait()
    assert not c.running
