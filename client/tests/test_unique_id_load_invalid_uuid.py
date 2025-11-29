import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_load_unique_id_invalid_uuid_returns_none():
    from src.utils.unique_id import load_unique_id
    tmp = Path(tempfile.mkdtemp(prefix="nm_uuid_invalid_"))
    try:
        (tmp / "client_state.json").write_text(json.dumps({"client_id": "not-a-uuid"}), encoding="utf-8")
        assert load_unique_id(str(tmp)) is None
    finally:
        shutil.rmtree(tmp)
