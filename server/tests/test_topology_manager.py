import os
import tempfile
import json
from src.database.managers.topology_manager import TopologyManager
from src.models.topology_info import TopologyInfo


def test_topology_crud():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        mgr = TopologyManager(db_path=tmp.name)
        content1 = json.dumps({"nodes": [{"id": "n1"}], "edges": []}, ensure_ascii=False)
        t1 = TopologyInfo(content=content1)
        new_id = mgr.save_topology(t1)
        assert isinstance(new_id, int) and new_id > 0

        got = mgr.get_topology_by_id(new_id)
        assert got is not None
        assert got["content"] == content1

        content2 = json.dumps({"nodes": [{"id": "n2"}], "edges": [{"source": "n2", "target": "n1"}]}, ensure_ascii=False)
        ok = mgr.update_topology(new_id, content2)
        assert ok is True

        latest = mgr.get_latest_topology()
        assert latest is not None
        assert latest["id"] == new_id
        assert latest["content"] == content2

        all_items = mgr.get_all_topologies()
        assert isinstance(all_items, list)
        assert len(all_items) >= 1

        cnt = mgr.get_topology_count()
        assert cnt >= 1

        del_ok = mgr.delete_topology(new_id)
        assert del_ok is True
        assert mgr.get_topology_by_id(new_id) is None
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
