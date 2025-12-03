import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.switches_handlers import (
    SwitchCreateHandler,
    SwitchUpdateHandler,
    SwitchDeleteHandler,
    SwitchHandler,
    SwitchesHandler,
)


class FakeSwitchMgr:
    def __init__(self):
        self.items = {1: {"id": 1, "ip": "1.2.3.4"}}

    def switch_exists(self, ip, snmp_version):
        return False

    def add_switch(self, switch_info):
        return True, "ok"

    def update_switch(self, switch_info):
        return True, "ok"

    def delete_switch(self, sid):
        return True, "ok"

    def get_switch_by_id(self, sid):
        return self.items.get(sid)

    def get_all_switches(self):
        return list(self.items.values())


class FakeDBM:
    def __init__(self):
        self.switch_manager = FakeSwitchMgr()


class TestSwitchesHandlers(AsyncHTTPTestCase):
    def get_app(self):
        self.dbm = FakeDBM()
        return tornado.web.Application(
            [
                (
                    r"/api/switches/create",
                    SwitchCreateHandler,
                    dict(db_manager=self.dbm),
                ),
                (
                    r"/api/switches/update",
                    SwitchUpdateHandler,
                    dict(db_manager=self.dbm),
                ),
                (
                    r"/api/switches/delete",
                    SwitchDeleteHandler,
                    dict(db_manager=self.dbm),
                ),
                (
                    r"/api/switches/(?P<switch_id>[^/]+)",
                    SwitchHandler,
                    dict(db_manager=self.dbm),
                ),
                (r"/api/switches", SwitchesHandler, dict(db_manager=self.dbm)),
            ]
        )

    def test_list(self):
        r = self.fetch("/api/switches")
        assert r.code == 200

    def test_get_success(self):
        r = self.fetch("/api/switches/1")
        assert r.code == 200

    def test_get_404(self):
        r = self.fetch("/api/switches/999")
        assert r.code == 404

    def test_create_missing(self):
        r = self.fetch(
            "/api/switches/create", method="POST", body=json.dumps({}).encode("utf-8")
        )
        assert r.code == 400

    def test_create_success(self):
        body = json.dumps({"ip": "10.0.0.1", "snmp_version": "2c"}).encode("utf-8")
        r = self.fetch("/api/switches/create", method="POST", body=body)
        assert r.code == 200

    def test_update_missing(self):
        r = self.fetch(
            "/api/switches/update", method="POST", body=json.dumps({}).encode("utf-8")
        )
        assert r.code == 400

    def test_update_success(self):
        body = json.dumps({"id": 1, "ip": "1.2.3.4", "snmp_version": "2c"}).encode(
            "utf-8"
        )
        r = self.fetch("/api/switches/update", method="POST", body=body)
        assert r.code == 200

    def test_delete_invalid(self):
        r = self.fetch(
            "/api/switches/delete",
            method="POST",
            body=json.dumps({"id": "x"}).encode("utf-8"),
        )
        assert r.code == 400

    def test_delete_success(self):
        r = self.fetch(
            "/api/switches/delete",
            method="POST",
            body=json.dumps({"id": 1}).encode("utf-8"),
        )
        assert r.code == 200
