import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_discover_server_multicast_success():
    from src.core.app_controller import AppController
    class DummyUDP:
        def discover_server_multicast(self):
            return ("10.0.0.1", 1234)
    with patch("src.core.app_controller.get_udp_client", return_value=DummyUDP()):
        c = AppController()
        addr = c._discover_server()
        assert addr == ("10.0.0.1", 1234)

def test_discover_server_broadcast_fallback():
    from src.core.app_controller import AppController
    class DummyUDP:
        def discover_server_multicast(self):
            return None
        def discover_server_broadcast(self):
            return ("10.0.0.2", 5678)
    with patch("src.core.app_controller.get_udp_client", return_value=DummyUDP()):
        c = AppController()
        addr = c._discover_server()
        assert addr == ("10.0.0.2", 5678)

def test_connect_to_server_with_retry_success_quick():
    from src.core.app_controller import AppController
    class DummyTCP:
        def connect(self, addr):
            return True
        def is_connected(self):
            return True
        def send_system_info(self):
            return True
        def disconnect(self):
            return None
    with patch("src.core.app_controller.initialize_tcp_client", return_value=DummyTCP()), \
         patch("src.core.app_controller.AppController._get_server_address_from_config", return_value=("127.0.0.1", 1111)):
        c = AppController()
        c.running = True
        ok = c._connect_to_server_with_retry(retry_delay=0.001)
        assert ok

def test_connect_to_server_with_retry_stopped():
    from src.core.app_controller import AppController
    c = AppController()
    c.running = False
    ok = c._connect_to_server_with_retry(retry_delay=0.001)
    assert not ok
