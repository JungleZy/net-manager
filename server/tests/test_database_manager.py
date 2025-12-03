import os
import tempfile
from src.database import DatabaseManager


class TestDatabaseManager:
    pass


def test_database_health_check():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        dbm = DatabaseManager(db_path=tmp.name)
        assert dbm.health_check() is True
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
