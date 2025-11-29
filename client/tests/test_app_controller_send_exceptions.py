import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_send_system_info_handles_collection_error():
    from src.core.app_controller import AppController
    from src.exceptions.exceptions import SystemInfoCollectionError
    c = AppController()
    class DummyTCP:
        def is_connected(self):
            return True
        def send_system_info(self):
            raise SystemInfoCollectionError("collect")
    c.tcp_client = DummyTCP()
    ok = c._send_system_info()
    assert ok is False

def test_send_system_info_handles_network_error():
    from src.core.app_controller import AppController
    from src.exceptions.exceptions import NetworkConnectionError
    c = AppController()
    class DummyTCP:
        def is_connected(self):
            return True
        def send_system_info(self):
            raise NetworkConnectionError("net")
    c.tcp_client = DummyTCP()
    ok = c._send_system_info()
    assert ok is False
