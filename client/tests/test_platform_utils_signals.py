import os
import sys
import signal as _signal
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_setup_signal_handlers_windows():
    from src.utils.platform_utils import setup_signal_handlers
    calls = []
    def fake_signal(sig, handler):
        calls.append(sig)
    with patch("src.utils.platform_utils.is_windows", return_value=True), \
         patch("src.utils.platform_utils.signal.signal", side_effect=fake_signal):
        setup_signal_handlers(lambda *a, **k: None)
    assert _signal.SIGINT in calls and _signal.SIGTERM in calls
