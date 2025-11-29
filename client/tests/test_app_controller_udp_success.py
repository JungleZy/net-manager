import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

class DummyUDP:
    def discover_server_multicast(self):
        return ("10.0.0.9", 1234)
    def discover_server_broadcast(self):
        return None

class DummyTCP:
    def connect(self, addr):
        return True
    def is_connected(self):
        return True
    def send_system_info(self):
        return True
    def disconnect(self):
        pass

def test_udp_success_connect_flow():
    from src.core.app_controller import AppController
    c = AppController()
    c.running = True
    with patch("src.core.app_controller.get_udp_client", return_value=DummyUDP()), \
         patch("src.core.app_controller.initialize_tcp_client", return_value=DummyTCP()):
        ok = c._connect_to_server_with_retry(retry_delay=0.001)
    assert ok
