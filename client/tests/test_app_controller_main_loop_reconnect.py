import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_main_loop_reconnect_flow():
    from src.core.app_controller import AppController
    c = AppController()
    c.running = True
    class DummyTCP:
        def __init__(self):
            self.state = [False, True]
        def is_connected(self):
            return self.state.pop(0) if self.state else True
        def send_system_info(self):
            return True
        def disconnect(self):
            pass
    c.tcp_client = DummyTCP()
    with patch("src.core.app_controller.AppController._connect_to_server_with_retry", return_value=True), \
         patch("src.config_module.config.config", type("Cfg", (), {"COLLECT_INTERVAL": 0.001})), \
         patch.object(c.stop_event, "wait", side_effect=lambda t: c.stop_event.set()):
        c._run_main_loop()
