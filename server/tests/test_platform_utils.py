from src.utils.platform_utils import get_platform, is_windows, setup_signal_handlers


def test_platform_utils_basic():
    plat = get_platform()
    assert plat in {"windows", "linux"}
    win = is_windows()
    assert isinstance(win, bool)


def test_setup_signal_handlers():
    called = {"v": 0}
    def handler(signum, frame):
        called["v"] += 1
    setup_signal_handlers(handler)
    assert called["v"] == 0
