import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_generate_and_save_unique_id():
    from src.utils.unique_id import generate_unique_id, save_unique_id
    tmp = Path(tempfile.mkdtemp(prefix="nm_uid_"))
    try:
        uid = generate_unique_id()
        ok = save_unique_id(uid, str(tmp))
        assert ok
        data = json.loads((tmp / "client_state.json").read_text(encoding="utf-8"))
        assert data.get("client_id") == uid
    finally:
        shutil.rmtree(tmp)
