import os
import sys
import tempfile
import shutil
from pathlib import Path

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_or_create_unique_id_creates_file():
    from src.utils.unique_id import get_or_create_unique_id
    td = Path(tempfile.mkdtemp(prefix="nm_uid_create_"))
    try:
        uid = get_or_create_unique_id(str(td))
        p = td / "client_state.json"
        assert p.exists()
        assert isinstance(uid, str) and len(uid) > 0
    finally:
        shutil.rmtree(td)
