import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.devices_handlers import (
    DeviceCreateHandler,
    DeviceUpdateHandler,
    DeviceDeleteHandler,
)


class FakeDeviceMgr:
    def create_device(self, data):
        return True, "ok"

    def update_device(self, data):
        return True, "ok"

    def delete_device(self, device_id):
        return True, "ok"


class FakeDBM:
    def __init__(self):
        self.device_manager = FakeDeviceMgr()


class TestDevicesCRUDHandlers(AsyncHTTPTestCase):
    def get_app(self):
        self.dbm = FakeDBM()

        class BadDB:
            def __init__(self):
                class DM:
                    def create_device(self, d):
                        return False, "bad"

                    def update_device(self, d):
                        return False, "bad"

                    def delete_device(self, i):
                        return False, "bad"

                self.device_manager = DM()

        return tornado.web.Application(
            [
                (
                    r"/api/devices/create",
                    DeviceCreateHandler,
                    dict(db_manager=self.dbm),
                ),
                (
                    r"/api/devices/update",
                    DeviceUpdateHandler,
                    dict(db_manager=self.dbm),
                ),
                (
                    r"/api/devices/delete",
                    DeviceDeleteHandler,
                    dict(db_manager=self.dbm),
                ),
                (
                    r"/api/devices/create2",
                    DeviceCreateHandler,
                    dict(db_manager=BadDB()),
                ),
                (
                    r"/api/devices/update2",
                    DeviceUpdateHandler,
                    dict(db_manager=BadDB()),
                ),
                (
                    r"/api/devices/delete2",
                    DeviceDeleteHandler,
                    dict(db_manager=BadDB()),
                ),
            ]
        )

    def test_create_success(self):
        body = json.dumps({"id": "d1", "hostname": "h"}).encode("utf-8")
        r = self.fetch("/api/devices/create", method="POST", body=body)
        assert r.code == 200

    def test_create_missing_field(self):
        body = json.dumps({"hostname": "h"}).encode("utf-8")
        r = self.fetch("/api/devices/create", method="POST", body=body)
        assert r.code == 400

    def test_update_success(self):
        body = json.dumps({"id": "d1", "alias": "A"}).encode("utf-8")
        r = self.fetch("/api/devices/update", method="POST", body=body)
        assert r.code == 200

    def test_update_missing_field(self):
        body = json.dumps({}).encode("utf-8")
        r = self.fetch("/api/devices/update", method="POST", body=body)
        assert r.code == 400

    def test_delete_success(self):
        body = json.dumps({"id": "d1"}).encode("utf-8")
        r = self.fetch("/api/devices/delete", method="POST", body=body)
        assert r.code == 200

    def test_delete_missing_field(self):
        body = json.dumps({}).encode("utf-8")
        r = self.fetch("/api/devices/delete", method="POST", body=body)
        assert r.code == 400

    def test_create_false(self):
        body = json.dumps({"id": "d1", "hostname": "h"}).encode("utf-8")
        r = self.fetch("/api/devices/create2", method="POST", body=body)
        assert r.code == 400

    def test_update_false(self):
        body = json.dumps({"id": "d1"}).encode("utf-8")
        r = self.fetch("/api/devices/update2", method="POST", body=body)
        assert r.code == 400

    def test_delete_false(self):
        body = json.dumps({"id": "d1"}).encode("utf-8")
        r = self.fetch("/api/devices/delete2", method="POST", body=body)
        assert r.code == 400
