import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_server_address_from_config_found():
    from src.core.app_controller import AppController
    class DummyState:
        def get_state(self, key, default=None):
            if key == "tcp_ip":
                return "192.168.0.10"
            if key == "tcp_port":
                return 5555
            return None
    with patch("src.core.state_manager.get_state_manager", return_value=DummyState()):
        c = AppController()
        addr = c._get_server_address_from_config()
        assert addr == ("192.168.0.10", 5555)

def test_get_server_address_from_config_not_found():
    from src.core.app_controller import AppController
    class DummyState:
        def get_state(self, key, default=None):
            return None
    with patch("src.core.state_manager.get_state_manager", return_value=DummyState()):
        c = AppController()
        addr = c._get_server_address_from_config()
        assert addr is None
