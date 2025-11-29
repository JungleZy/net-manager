import os
import sys
import tempfile
import shutil
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_save_unique_id_with_invalid_existing_state():
    from src.utils.unique_id import save_unique_id
    tmp = Path(tempfile.mkdtemp(prefix="nm_uid_invalid_"))
    try:
        (tmp / "client_state.json").write_text("{invalid", encoding="utf-8")
        ok = save_unique_id("abc", str(tmp))
        assert ok
        text = (tmp / "client_state.json").read_text(encoding="utf-8")
        assert "client_id" in text
    finally:
        shutil.rmtree(tmp)
