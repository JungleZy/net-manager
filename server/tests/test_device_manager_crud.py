import os
import tempfile
from src.database.managers.device_manager import DeviceManager
from src.models.device_info import DeviceInfo
from src.database.db_exceptions import DatabaseQueryError


def test_device_manager_crud_and_queries():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        mgr = DeviceManager(db_path=tmp.name)

        ok, msg = mgr.create_device(
            {
                "id": "dev-001",
                "client_id": "cid-001",
                "hostname": "host-A",
                "os_name": "Windows",
                "os_version": "11",
                "os_architecture": "x64",
                "machine_type": "Desktop",
                "services": [{"n": 1}],
                "processes": [{"p": 1}],
                "networks": [{"name": "eth0", "ip_address": "10.0.0.3"}],
                "cpu_info": {"c": 1},
                "memory_info": {"m": 1},
                "disk_info": {"d": 1},
                "type": "",
            }
        )
        assert ok is True
        assert mgr.get_device_count() == 1

        item = mgr.get_device_info_by_id("dev-001")
        assert item is not None
        assert item["alias"] == ""
        assert item["hostname"] == "host-A"
        assert isinstance(item["services"], list)
        assert isinstance(item["cpu_info"], dict)

        # update type
        assert mgr.update_device_type("dev-001", "pc") is True
        item2 = mgr.get_device_info_by_id("dev-001")
        assert item2["type"] == "pc"

        # update alias via update_device
        ok, msg = mgr.update_device({"id": "dev-001", "alias": "AliasA", "type": "pc"})
        assert ok is True
        item3 = mgr.get_device_info_by_id("dev-001")
        assert item3["alias"] == "AliasA"

        # save_device_info should not overwrite alias
        di = DeviceInfo(
            id="dev-001",
            client_id="cid-001",
            hostname="host-B",
            os_name="Windows",
            os_version="11",
            os_architecture="x64",
            machine_type="Desktop",
        )
        mgr.save_device_info(di)
        item4 = mgr.get_device_info_by_id("dev-001")
        assert item4["hostname"] == "host-B"
        assert item4["alias"] == "AliasA"

        # duplicate create causes DatabaseQueryError
        dup_err = None
        try:
            mgr.create_device({"id": "dev-001", "hostname": "x"})
        except Exception as e:
            dup_err = e
        assert isinstance(dup_err, DatabaseQueryError)

        # get by client id
        bycid = mgr.get_device_info_by_client_id("cid-001")
        assert bycid is not None
        assert bycid["id"] == "dev-001"

        # delete
        ok, msg = mgr.delete_device("dev-001")
        assert ok is True
        del_err = None
        try:
            mgr.delete_device("dev-001")
        except Exception as e:
            del_err = e
        assert isinstance(del_err, DatabaseQueryError)
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
