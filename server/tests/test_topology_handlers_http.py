import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.topology_handlers import (
    TopologyCreateHandler,
    TopologyUpdateHandler,
    TopologyDeleteHandler,
    TopologiesHandler,
)


class FakeTopoMgr:
    def __init__(self):
        self.items = {1: {"id": 1, "content": json.dumps({"nodes": []}), "created_at": ""}}

    def save_topology(self, topo):
        return 2

    def update_topology(self, tid, content):
        return True

    def delete_topology(self, tid):
        return True

    def get_all_topologies(self):
        return list(self.items.values())


class TestTopologyHandlers(AsyncHTTPTestCase):
    def get_app(self):
        self.tm = FakeTopoMgr()
        return tornado.web.Application([
            (r"/api/topologies/create", TopologyCreateHandler, dict(topology_manager=self.tm)),
            (r"/api/topologies/update", TopologyUpdateHandler, dict(topology_manager=self.tm)),
            (r"/api/topologies/delete", TopologyDeleteHandler, dict(topology_manager=self.tm)),
            (r"/api/topologies", TopologiesHandler, dict(topology_manager=self.tm)),
        ])

    def test_list(self):
        r = self.fetch("/api/topologies")
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["status"] == "success"
        assert data["count"] >= 1

    def test_create_with_string_content(self):
        body = json.dumps({"content": json.dumps({"nodes": [1]})}).encode("utf-8")
        r = self.fetch("/api/topologies/create", method="POST", body=body)
        assert r.code == 200

    def test_create_with_object_content(self):
        body = json.dumps({"content": {"nodes": [1]}}).encode("utf-8")
        r = self.fetch("/api/topologies/create", method="POST", body=body)
        assert r.code == 200

    def test_update_success(self):
        body = json.dumps({"id": 1, "content": {"nodes": [2]}}).encode("utf-8")
        r = self.fetch("/api/topologies/update", method="POST", body=body)
        assert r.code == 200

    def test_delete_success(self):
        body = json.dumps({"id": 1}).encode("utf-8")
        r = self.fetch("/api/topologies/delete", method="POST", body=body)
        assert r.code == 200
