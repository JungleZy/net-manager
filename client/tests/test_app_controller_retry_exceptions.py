import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_connect_retry_handles_exceptions_and_returns_false():
    from src.core.app_controller import AppController
    from src.network.tcp_client import TCPClient
    c = AppController()
    c.running = True
    attempts = {"n": 0}
    def side_effect():
        attempts["n"] += 1
        if attempts["n"] == 1:
            from src.exceptions.exceptions import NetworkDiscoveryError
            raise NetworkDiscoveryError("disc")
        if attempts["n"] == 2:
            from src.exceptions.exceptions import NetworkConnectionError
            raise NetworkConnectionError("conn")
        c.running = False
        return None
    with patch("src.core.app_controller.initialize_tcp_client", return_value=TCPClient()), \
         patch("src.core.app_controller.AppController._get_server_address_from_config", return_value=None), \
         patch("src.core.app_controller.AppController._discover_server", side_effect=side_effect), \
         patch("src.core.app_controller.time.sleep", return_value=None):
        ok = c._connect_to_server_with_retry(retry_delay=0.001)
    assert ok is False
