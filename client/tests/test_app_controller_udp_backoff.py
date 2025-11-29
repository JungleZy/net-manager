import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_connect_retry_udp_backoff_none_discovery_then_stop():
    from src.core.app_controller import AppController
    c = AppController()
    c.running = True
    with patch("src.core.app_controller.AppController._get_server_address_from_config", return_value=None), \
         patch("src.core.app_controller.AppController._discover_server", return_value=None), \
         patch("src.core.app_controller.time.sleep", side_effect=lambda d: setattr(c, "running", False)):
        ok = c._connect_to_server_with_retry(retry_delay=0.001)
    assert ok is False
