import os
import sys
import signal
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_setup_signal_handlers_linux():
    from src.utils.platform_utils import setup_signal_handlers

    calls = []

    def fake_signal(sig, handler):
        calls.append(sig)

    from contextlib import ExitStack

    with ExitStack() as stack:
        stack.enter_context(
            patch("src.utils.platform_utils.is_windows", return_value=False)
        )
        stack.enter_context(
            patch("src.utils.platform_utils.signal.signal", side_effect=fake_signal)
        )
        stack.enter_context(
            patch("src.utils.platform_utils.signal.SIGQUIT", 3, create=True)
        )
        stack.enter_context(
            patch("src.utils.platform_utils.signal.SIGHUP", 1, create=True)
        )
        setup_signal_handlers(lambda *a, **k: None)
    assert (
        signal.SIGINT in calls and signal.SIGTERM in calls and 3 in calls and 1 in calls
    )
