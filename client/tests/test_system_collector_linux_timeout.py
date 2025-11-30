import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_linux_gateway_timeout_returns_unknown():
    from src.system.system_collector import SystemCollector
    import subprocess

    sc = SystemCollector()

    def side(cmd, capture_output=True, text=True, timeout=5):
        raise subprocess.TimeoutExpired(cmd, timeout)

    from contextlib import ExitStack

    with ExitStack() as stack:
        stack.enter_context(
            patch("src.system.system_collector.platform.system", return_value="Linux")
        )
        stack.enter_context(
            patch("src.system.system_collector.subprocess.run", side_effect=side)
        )
        import io, builtins

        class DummyOpen:
            def __call__(self, *args, **kwargs):
                return self

            def __enter__(self):
                return io.StringIO(
                    "Iface\tDestination\tGateway\neth0\t00000001\t00000000\n"
                )

            def __exit__(self, *args):
                return False

        stack.enter_context(patch("builtins.open", DummyOpen()))
        gw = sc._get_linux_gateway()
        assert gw == "unknown"
