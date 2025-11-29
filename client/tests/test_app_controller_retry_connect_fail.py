import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class FailTCP:
    def connect(self, addr):
        return False
    def is_connected(self):
        return False
    def send_system_info(self):
        return False
    def disconnect(self):
        pass

def test_connect_retry_connect_fail_then_stop():
    from src.core.app_controller import AppController
    c = AppController()
    c.running = True
    def stop_on_sleep(*args, **kwargs):
        c.running = False
    with patch("src.core.app_controller.AppController._get_server_address_from_config", return_value=("127.0.0.1", 1111)), \
         patch("src.core.app_controller.initialize_tcp_client", return_value=FailTCP()), \
         patch("src.core.app_controller.time.sleep", side_effect=stop_on_sleep):
        ok = c._connect_to_server_with_retry(retry_delay=0.001)
    assert ok is False
