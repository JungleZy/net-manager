import os
import tempfile
from src.database.managers.switch_manager import SwitchManager
from src.models.switch_info import SwitchInfo
from src.database.db_exceptions import DatabaseQueryError, DeviceNotFoundError


def test_switch_crud_and_queries():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        mgr = SwitchManager(db_path=tmp.name)
        s1 = SwitchInfo(
            ip="192.0.2.10",
            snmp_version="2c",
            community="public",
            description="d1",
            device_name="sw1",
            device_type="switch",
        )
        ok, msg = mgr.add_switch(s1)
        assert ok is True

        assert mgr.get_switch_count() == 1
        row = mgr.get_switch_by_ip("192.0.2.10")
        assert row is not None
        sid = row["id"]
        assert sid > 0

        exists = mgr.switch_exists("192.0.2.10", "2c")
        assert exists is True

        s1upd = SwitchInfo(
            ip="192.0.2.10",
            snmp_version="2c",
            community="public",
            description="d2",
            device_name="sw1",
            device_type="switch",
            alias="A",
            id=sid,
        )
        ok, msg = mgr.update_switch(s1upd)
        assert ok is True
        got = mgr.get_switch_by_id(sid)
        assert got is not None
        assert got["alias"] == "A"
        assert got["description"] == "d2"

        dup_err = None
        try:
            mgr.add_switch(SwitchInfo(ip="192.0.2.10", snmp_version="2c"))
        except Exception as e:
            dup_err = e
        assert isinstance(dup_err, DatabaseQueryError)

        ok, msg = mgr.delete_switch(sid)
        assert ok is True
        del_err = None
        try:
            mgr.delete_switch(sid)
        except Exception as e:
            del_err = e
        assert isinstance(del_err, DatabaseQueryError)
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
