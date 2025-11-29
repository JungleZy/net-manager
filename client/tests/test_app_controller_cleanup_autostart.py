import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_start_calls_autostart_when_compiled_and_cleanup_stops():
    from src.core.app_controller import AppController
    c = AppController()
    called = {"auto": 0}
    with patch("src.core.app_controller.sys.frozen", True, create=True), \
         patch.object(AppController, "_handle_autostart", side_effect=lambda: called.__setitem__("auto", 1)), \
         patch.object(AppController, "_connect_to_server_with_retry", return_value=False):
        c.start()
        c.cleanup()
    assert called["auto"] == 1
    assert not c.running
