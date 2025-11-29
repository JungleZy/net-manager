import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_check_lock_status_with_existing_file_and_process():
    temp_dir = Path(tempfile.mkdtemp(prefix="nm_sm_status_"))
    try:
        lock_path = temp_dir / "net_manager_client_test.lock"
        lock_path.write_text(str(os.getpid()), encoding="utf-8")
        with patch("src.utils.singleton_manager.sys.platform", "linux"):
            from src.utils.singleton_manager import SingletonManager

            m = SingletonManager()
            m.lock_file = str(lock_path)
            m.lock_handle = 1
            with patch("src.utils.singleton_manager.os.kill", return_value=None):
                s = m.check_lock_status()
                assert s["file_exists"]
                assert s["file_content"] == str(os.getpid())
                assert s["process_exists"]
    finally:
        shutil.rmtree(temp_dir)


def test_check_lock_status_with_nonexisting_process():
    temp_dir = Path(tempfile.mkdtemp(prefix="nm_sm_status_"))
    try:
        lock_path = temp_dir / "net_manager_client_test.lock"
        lock_path.write_text("999999", encoding="utf-8")
        with patch("src.utils.singleton_manager.sys.platform", "linux"):
            from src.utils.singleton_manager import SingletonManager

            m = SingletonManager()
            m.lock_file = str(lock_path)
            m.lock_handle = 1
            with patch("src.utils.singleton_manager.os.kill", side_effect=OSError()):
                s = m.check_lock_status()
                assert s["file_exists"]
                assert s.get("process_exists") is False
    finally:
        shutil.rmtree(temp_dir)
