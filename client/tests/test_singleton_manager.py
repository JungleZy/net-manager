import os
import sys
import tempfile
import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


class FakeFcntl:
    LOCK_EX = 1
    LOCK_NB = 2
    LOCK_UN = 3

    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def flock(self, handle, flags):
        if self.should_fail:
            raise OSError("lock busy")


def test_singleton_unix_lock_acquire_release():
    temp_dir = Path(tempfile.mkdtemp(prefix="nm_singleton_"))
    try:
        with patch.dict(sys.modules, {"fcntl": FakeFcntl(should_fail=False)}), patch(
            "src.utils.singleton_manager.platform.system", return_value="Linux"
        ), patch(
            "src.utils.singleton_manager.os.path.exists",
            side_effect=lambda p: False if p == "/tmp" else os.path.exists(p),
        ), patch(
            "src.utils.singleton_manager.os.path.expanduser", return_value=str(temp_dir)
        ):
            from src.utils.singleton_manager import SingletonManager

            m = SingletonManager()
            ok = m.acquire_lock()
            assert ok
            assert m.lock_acquired
            assert m.lock_file is not None
            assert Path(m.lock_file).exists()
            content = Path(m.lock_file).read_text().strip()
            assert content == str(os.getpid())
            m.release_lock()
            assert not m.lock_acquired
    finally:
        shutil.rmtree(temp_dir)


def test_singleton_unix_lock_busy():
    temp_dir = Path(tempfile.mkdtemp(prefix="nm_singleton_"))
    try:
        with patch.dict(sys.modules, {"fcntl": FakeFcntl(should_fail=True)}), patch(
            "src.utils.singleton_manager.platform.system", return_value="Linux"
        ), patch(
            "src.utils.singleton_manager.os.path.exists",
            side_effect=lambda p: False if p == "/tmp" else os.path.exists(p),
        ), patch(
            "src.utils.singleton_manager.os.path.expanduser", return_value=str(temp_dir)
        ):
            from src.utils.singleton_manager import SingletonManager

            m = SingletonManager()
            ok = m.acquire_lock()
            assert not ok
            assert not m.lock_acquired
    finally:
        shutil.rmtree(temp_dir)
