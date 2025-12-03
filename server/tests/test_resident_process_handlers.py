import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.resident_process_handlers import (
    ResidentProcessListHandler,
    ResidentProcessCreateHandler,
    ResidentProcessGetHandler,
    ResidentProcessDeleteHandler,
    ResidentProcessClearHandler,
)


class FakeRPM:
    def __init__(self):
        self.store = {1: {"id": 1, "name": "procA", "created_at": ""}}

    def get_all_resident_processes(self):
        return list(self.store.values())

    def add_resident_process(self, process_info):
        new_id = max(self.store.keys()) + 1 if self.store else 1
        self.store[new_id] = {"id": new_id, "name": process_info.name, "created_at": ""}
        return new_id

    def batch_add_resident_processes(self, names):
        return {"success_count": 1, "skipped_count": 0, "failed_count": 0, "deleted_count": 0, "details": []}

    def delete_resident_process(self, pid):
        return bool(self.store.pop(pid, None))

    def delete_resident_process_by_name(self, name):
        for k, v in list(self.store.items()):
            if v.get("name") == name:
                self.store.pop(k)
                return True
        return False

    def clear_all_resident_processes(self):
        c = len(self.store)
        self.store.clear()
        return c

    def get_resident_process_by_id(self, pid):
        return self.store.get(pid)

    def get_resident_process_by_name(self, name):
        for v in self.store.values():
            if v.get("name") == name:
                return v
        return None


class TestResidentProcessHandlers(AsyncHTTPTestCase):
    def get_app(self):
        self.rpm = FakeRPM()
        return tornado.web.Application([
            (r"/api/resident-processes", ResidentProcessListHandler, dict(resident_process_manager=self.rpm)),
            (r"/api/resident-processes/create", ResidentProcessCreateHandler, dict(resident_process_manager=self.rpm)),
            (r"/api/resident-processes/get", ResidentProcessGetHandler, dict(resident_process_manager=self.rpm)),
            (r"/api/resident-processes/delete", ResidentProcessDeleteHandler, dict(resident_process_manager=self.rpm)),
            (r"/api/resident-processes/clear", ResidentProcessClearHandler, dict(resident_process_manager=self.rpm)),
        ])

    def test_list(self):
        r = self.fetch("/api/resident-processes")
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["status"] == "success"
        assert isinstance(data["data"], list)

    def test_create(self):
        r = self.fetch("/api/resident-processes/create", method="POST", body=json.dumps({"name": "procB"}).encode("utf-8"))
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["status"] == "success"
        assert data["data"]["name"] == "procB"

    def test_get_by_id(self):
        r = self.fetch("/api/resident-processes/get?id=1")
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["data"]["id"] == 1

    def test_delete_by_id(self):
        r = self.fetch("/api/resident-processes/delete", method="POST", body=json.dumps({"id": 1}).encode("utf-8"))
        assert r.code == 200

    def test_clear(self):
        r = self.fetch("/api/resident-processes/clear", method="POST", body=b"{}")
        assert r.code == 200
