import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_main_loop_sends_heartbeat_and_exits():
    from src.core.app_controller import AppController
    from threading import Event
    c = AppController()
    c.running = True
    c.stop_event = Event()
    sent = {"count": 0}
    def fake_send():
        sent["count"] += 1
        c.stop_event.set()
        return True
    with patch("src.core.app_controller.initialize_tcp_client") as init_tcp, \
         patch("src.core.app_controller.AppController._connect_to_server_with_retry", return_value=True), \
         patch("src.core.app_controller.AppController._send_system_info", side_effect=fake_send), \
         patch("src.config_module.config.config", SimpleNamespace(COLLECT_INTERVAL=0.001)):
        ok = c._run_main_loop()
        assert sent["count"] >= 1
