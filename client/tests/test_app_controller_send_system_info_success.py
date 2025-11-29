import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_send_system_info_success():
    from src.core.app_controller import AppController
    c = AppController()
    class T:
        def is_connected(self):
            return True
        def send_system_info(self):
            return True
    c.tcp_client = T()
    assert c._send_system_info() is True
