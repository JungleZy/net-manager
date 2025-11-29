import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_handle_autostart_enables_when_disabled():
    from src.core.app_controller import AppController
    c = AppController()
    with patch("src.core.app_controller.is_autostart_enabled", return_value=False), \
         patch("src.core.app_controller.enable_autostart", return_value=True):
        c._handle_autostart()

def test_handle_autostart_noop_when_enabled():
    from src.core.app_controller import AppController
    c = AppController()
    with patch("src.core.app_controller.is_autostart_enabled", return_value=True):
        c._handle_autostart()
