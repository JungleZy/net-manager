import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.topology_handlers import (
    TopologyCreateHandler,
    TopologyUpdateHandler,
    TopologyDeleteHandler,
    TopologyLatestHandler,
    TopologyHandler,
    TopologiesHandler,
)


class FakeTM:
    def __init__(self):
        self.latest = {"id": 1, "content": '{"nodes": []}', "created_at": ""}
        self.byid = None

    def save_topology(self, topo):
        return 1

    def update_topology(self, tid, content):
        return False

    def delete_topology(self, tid):
        return False

    def get_latest_topology(self):
        return self.latest

    def get_topology_by_id(self, tid):
        return self.byid


class TestTopologyHandlersMore(AsyncHTTPTestCase):
    def get_app(self):
        self.tm = FakeTM()

        class CreateExc:
            def save_topology(self, topo):
                raise RuntimeError("e")

        class UpdateExc:
            def update_topology(self, tid, content):
                raise RuntimeError("e")

        class DeleteExc:
            def delete_topology(self, tid):
                raise RuntimeError("e")

        class ListExc:
            def get_all_topologies(self):
                raise RuntimeError("e")

        return tornado.web.Application(
            [
                (r"/create", TopologyCreateHandler, dict(topology_manager=self.tm)),
                (
                    r"/create_exc",
                    TopologyCreateHandler,
                    dict(topology_manager=CreateExc()),
                ),
                (r"/update", TopologyUpdateHandler, dict(topology_manager=self.tm)),
                (
                    r"/update_exc",
                    TopologyUpdateHandler,
                    dict(topology_manager=UpdateExc()),
                ),
                (r"/delete", TopologyDeleteHandler, dict(topology_manager=self.tm)),
                (
                    r"/delete_exc",
                    TopologyDeleteHandler,
                    dict(topology_manager=DeleteExc()),
                ),
                (r"/latest", TopologyLatestHandler, dict(topology_manager=self.tm)),
                (
                    r"/one/(?P<topology_id>[^/]+)",
                    TopologyHandler,
                    dict(topology_manager=self.tm),
                ),
                (r"/list", TopologiesHandler, dict(topology_manager=self.tm)),
                (r"/list_exc", TopologiesHandler, dict(topology_manager=ListExc())),
            ]
        )

    def test_create_jsondecodeerror(self):
        r = self.fetch("/create", method="POST", body=b"{")
        assert r.code == 400

    def test_create_missing_content(self):
        body = json.dumps({}).encode("utf-8")
        r = self.fetch("/create", method="POST", body=body)
        assert r.code == 400

    def test_create_invalid_string(self):
        body = json.dumps({"content": "not-json"}).encode("utf-8")
        r = self.fetch("/create", method="POST", body=body)
        assert r.code == 400

    def test_create_exception(self):
        body = json.dumps({"content": {"nodes": []}}).encode("utf-8")
        r = self.fetch("/create_exc", method="POST", body=body)
        assert r.code == 500

    def test_update_not_found(self):
        body = json.dumps({"id": 9, "content": {"nodes": []}}).encode("utf-8")
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 404

    def test_update_invalid_string(self):
        body = json.dumps({"id": 1, "content": "not-json"}).encode("utf-8")
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 400

    def test_update_json_error(self):
        r = self.fetch("/update", method="POST", body=b"{")
        assert r.code == 400

    def test_update_missing_id(self):
        body = json.dumps({"content": {"nodes": []}}).encode("utf-8")
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 400

    def test_update_missing_content(self):
        body = json.dumps({"id": 1}).encode("utf-8")
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 400

    def test_update_invalid_id_type(self):
        body = json.dumps({"id": "abc", "content": {"nodes": []}}).encode("utf-8")
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 400

    def test_update_exception(self):
        body = json.dumps({"id": 1, "content": {"nodes": []}}).encode("utf-8")
        r = self.fetch("/update_exc", method="POST", body=body)
        assert r.code == 500

    def test_delete_not_found(self):
        body = json.dumps({"id": 9}).encode("utf-8")
        r = self.fetch("/delete", method="POST", body=body)
        assert r.code == 404

    def test_delete_missing_id(self):
        r = self.fetch("/delete", method="POST", body=json.dumps({}).encode("utf-8"))
        assert r.code == 400

    def test_delete_invalid_id_type(self):
        r = self.fetch(
            "/delete", method="POST", body=json.dumps({"id": "abc"}).encode("utf-8")
        )
        assert r.code == 400

    def test_delete_json_error(self):
        r = self.fetch("/delete", method="POST", body=b"{")
        assert r.code == 400

    def test_delete_exception(self):
        body = json.dumps({"id": 1}).encode("utf-8")
        r = self.fetch("/delete_exc", method="POST", body=body)
        assert r.code == 500

    def test_latest_success(self):
        r = self.fetch("/latest")
        assert r.code == 200

    def test_latest_parse_error(self):
        self.tm.latest = {"id": 1, "content": "bad-json", "created_at": ""}
        r = self.fetch("/latest")
        assert r.code == 200

    def test_latest_none(self):
        self.tm.latest = None
        r = self.fetch("/latest")
        assert r.code == 200

    def test_latest_error(self):
        class Bad(FakeTM.__class__):
            pass

        self.tm.get_latest_topology = lambda: (_ for _ in ()).throw(RuntimeError("e"))
        r = self.fetch("/latest")
        assert r.code == 500

    def test_handler_invalid_id(self):
        r = self.fetch("/one/abc")
        assert r.code == 400

    def test_handler_empty(self):
        self.tm.byid = None
        r = self.fetch("/one/1")
        assert r.code == 200

    def test_handler_parse_error(self):
        self.tm.byid = {"id": 2, "content": "bad-json", "created_at": ""}
        r = self.fetch("/one/2")
        assert r.code == 200

    def test_handler_parse_success(self):
        self.tm.byid = {"id": 3, "content": json.dumps({"nodes": []}), "created_at": ""}
        r = self.fetch("/one/3")
        assert r.code == 200

    def test_handler_exception(self):
        self.tm.get_topology_by_id = lambda tid: (_ for _ in ()).throw(
            RuntimeError("e")
        )
        r = self.fetch("/one/1")
        assert r.code == 500

    def test_update_type_error_on_dump(self):
        import src.network.api.handlers.topology_handlers as th
        import src.network.api.handlers.base_handler as bh

        orig_json = th.json

        def bad_dumps(*a, **k):
            raise TypeError("bad")

        th.json = type("J", (), {"dumps": bad_dumps, "loads": json.loads})()
        orig_bh = bh.json.dumps
        bh.json.dumps = lambda *a, **k: '{"status":"error"}'
        try:
            body = b'{"id": 1, "content": {"nodes": []}}'
            r = self.fetch("/update", method="POST", body=body)
            assert r.code == 400
        finally:
            th.json = orig_json
            bh.json.dumps = orig_bh

    def test_create_type_error_on_dump(self):
        import src.network.api.handlers.topology_handlers as th
        import src.network.api.handlers.base_handler as bh

        orig_json = th.json

        def bad_dumps(*a, **k):
            raise TypeError("bad")

        th.json = type("J", (), {"dumps": bad_dumps, "loads": json.loads})()
        orig_bh = bh.json.dumps
        bh.json.dumps = lambda *a, **k: '{"status":"error"}'
        try:
            body = b'{"content": {"nodes": []}}'
            r = self.fetch("/create", method="POST", body=body)
            assert r.code == 400
        finally:
            th.json = orig_json
            bh.json.dumps = orig_bh

    def test_delete_error(self):
        self.tm.delete_topology = lambda tid: (_ for _ in ()).throw(RuntimeError("e"))
        body = json.dumps({"id": 1}).encode("utf-8")
        r = self.fetch("/delete", method="POST", body=body)
        assert r.code == 500

    def test_list_parse_error_and_exception(self):
        def bad_list():
            return [{"id": 1, "content": "bad-json", "created_at": ""}]

        self.tm.get_all_topologies = bad_list
        r = self.fetch("/list")
        assert r.code == 200
        self.tm.get_all_topologies = lambda: (_ for _ in ()).throw(RuntimeError("e"))
        r = self.fetch("/list")
        assert r.code == 500
