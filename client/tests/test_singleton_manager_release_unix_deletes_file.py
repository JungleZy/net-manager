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


class Fcntl:
    LOCK_UN = 3

    def flock(self, handle, flags):
        return None


def test_release_lock_unix_deletes_file():
    import src.utils.singleton_manager as sm

    td = Path(tempfile.mkdtemp(prefix="nm_sm_rel_"))
    try:
        lf = td / "x.lock"
        lf.write_text(str(os.getpid()), encoding="utf-8")
        m = sm.SingletonManager()
        m.lock_file = str(lf)
        m.lock_handle = 1
        m.lock_acquired = True
        with patch(
            "src.utils.singleton_manager.platform.system", return_value="Linux"
        ), patch.dict(sys.modules, {"fcntl": Fcntl()}):
            m.release_lock()
            assert not lf.exists() and not m.lock_acquired
    finally:
        shutil.rmtree(td)
