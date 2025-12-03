import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.devices_handlers import (
    DeviceCreateHandler,
    DeviceUpdateHandler,
    DeviceDeleteHandler,
    DeviceHandler,
    DevicesHandler,
    DeviceTypeHandler,
)


class BadDM:
    def __init__(self):
        class Dev:
            def create_device(self, d):
                raise RuntimeError("boom")

            def update_device(self, d):
                raise RuntimeError("boom")

            def delete_device(self, i):
                raise RuntimeError("boom")

            def get_all_device_info(self):
                return []

            def get_device_info_by_id(self, x):
                return None

        self.device_manager = Dev()


class GoodDM:
    def __init__(self, devices):
        class Dev:
            def __init__(self, ds):
                self.ds = {d["id"]: d for d in ds}

            def get_all_device_info(self):
                return list(self.ds.values())

            def get_device_info_by_id(self, x):
                return self.ds.get(x)

        self.device_manager = Dev(devices)


class TestDevicesHandlersMore(AsyncHTTPTestCase):
    def get_app(self):
        self.bad = BadDM()
        self.good = GoodDM(
            [
                {
                    "id": "d1",
                    "client_id": None,
                    "hostname": "h",
                    "alias": "",
                    "services": [],
                    "processes": [],
                    "networks": None,
                    "cpu_info": {},
                    "memory_info": {},
                    "disk_info": {},
                    "os_name": "o",
                    "os_version": "v",
                    "os_architecture": "a",
                    "machine_type": "m",
                    "type": "t",
                    "timestamp": "",
                    "created_at": "",
                }
            ]
        )
        return tornado.web.Application(
            [
                (r"/create", DeviceCreateHandler, dict(db_manager=self.bad)),
                (r"/update", DeviceUpdateHandler, dict(db_manager=self.bad)),
                (r"/delete", DeviceDeleteHandler, dict(db_manager=self.bad)),
                (
                    r"/one/(?P<device_id>[^/]+)",
                    DeviceHandler,
                    dict(
                        db_manager=self.good,
                        get_tcp_server_func=lambda: type(
                            "T",
                            (),
                            {
                                "clients_lock": __import__("threading").Lock(),
                                "client_id_map": {"cid": 1},
                            },
                        )(),
                    ),
                ),
                (
                    r"/list",
                    DevicesHandler,
                    dict(db_manager=self.good, get_tcp_server_func=None),
                ),
                (
                    r"/li",
                    DevicesHandler,
                    dict(
                        db_manager=type(
                            "BL",
                            (),
                            {
                                "device_manager": type(
                                    "DM",
                                    (),
                                    {
                                        "get_all_device_info": lambda self2: (
                                            _ for _ in ()
                                        ).throw(RuntimeError("boom"))
                                    },
                                )()
                            },
                        )(),
                        get_tcp_server_func=None,
                    ),
                ),
                (
                    r"/type/(?P<device_id>[^/]+)",
                    DeviceTypeHandler,
                    dict(
                        db_manager=type(
                            "DB",
                            (),
                            {
                                "device_manager": type(
                                    "DM",
                                    (),
                                    {"update_device_type": lambda self2, i, t: True},
                                )()
                            },
                        )()
                    ),
                ),
                (
                    r"/type_badjson/(?P<device_id>[^/]+)",
                    DeviceTypeHandler,
                    dict(db_manager=self.good),
                ),
                (
                    r"/type_err/(?P<device_id>[^/]+)",
                    DeviceTypeHandler,
                    dict(
                        db_manager=type(
                            "DB",
                            (),
                            {
                                "device_manager": type(
                                    "DM",
                                    (),
                                    {"update_device_type": lambda self2, i, t: False},
                                )()
                            },
                        )()
                    ),
                ),
                (
                    r"/type_exc/(?P<device_id>[^/]+)",
                    DeviceTypeHandler,
                    dict(
                        db_manager=type(
                            "DB",
                            (),
                            {
                                "device_manager": type(
                                    "DM",
                                    (),
                                    {
                                        "update_device_type": lambda self2, i, t: (
                                            _ for _ in ()
                                        ).throw(RuntimeError("x"))
                                    },
                                )()
                            },
                        )()
                    ),
                ),
                (
                    r"/oneerr/(?P<device_id>[^/]+)",
                    DeviceHandler,
                    dict(
                        db_manager=type(
                            "BDM",
                            (),
                            {
                                "device_manager": type(
                                    "DM",
                                    (),
                                    {
                                        "get_device_info_by_id": lambda self2, x: (
                                            _ for _ in ()
                                        ).throw(RuntimeError("x"))
                                    },
                                )()
                            },
                        )(),
                        get_tcp_server_func=None,
                    ),
                ),
            ]
        )

    def test_json_decode_error(self):
        r = self.fetch("/create", method="POST", body=b"{")
        assert r.code == 400
        r = self.fetch("/update", method="POST", body=b"{")
        assert r.code == 400
        r = self.fetch("/delete", method="POST", body=b"{")
        assert r.code == 400

    def test_internal_server_error(self):
        body = json.dumps({"id": "d1", "hostname": "h"}).encode("utf-8")
        r = self.fetch("/create", method="POST", body=body)
        assert r.code == 500
        body = json.dumps({"id": "d1"}).encode("utf-8")
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 500
        body = json.dumps({"id": "d1"}).encode("utf-8")
        r = self.fetch("/delete", method="POST", body=body)
        assert r.code == 500

    def test_device_handler_404(self):
        r = self.fetch("/one/unknown")
        assert r.code == 404

    def test_device_handler_success(self):
        r = self.fetch("/one/d1")
        assert r.code == 200

    def test_devices_list_networks_none(self):
        r = self.fetch("/list")
        assert r.code == 200

    def test_devices_list_internal_error(self):
        class BadList:
            def __init__(self):
                class Dev:
                    def get_all_device_info(self2):
                        raise RuntimeError("boom")

                self.device_manager = Dev()

        r = self.fetch("/li")
        assert r.code == 500

    def test_device_type_missing_field(self):
        r = self.fetch("/type/d1", method="PUT", body=b"{}")
        assert r.code == 400

    def test_device_type_success(self):
        r = self.fetch(
            "/type/d1", method="PUT", body=json.dumps({"type": "pc"}).encode("utf-8")
        )
        assert r.code == 200

    def test_device_type_not_found(self):
        r = self.fetch(
            "/type_err/d1",
            method="PUT",
            body=json.dumps({"type": "pc"}).encode("utf-8"),
        )
        assert r.code == 404

    def test_device_type_exception(self):
        r = self.fetch(
            "/type_exc/d1",
            method="PUT",
            body=json.dumps({"type": "pc"}).encode("utf-8"),
        )
        assert r.code == 500

    def test_device_type_json_decode_error(self):
        r = self.fetch("/type_badjson/d1", method="PUT", body=b"{")
        assert r.code == 400
