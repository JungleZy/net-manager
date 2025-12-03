import threading
import json
from tornado.testing import AsyncHTTPTestCase
import tornado.web
from src.network.api.handlers.devices_handlers import DevicesHandler, DeviceHandler
from src.network.api.handlers.devices_handlers import DeviceTypeHandler


class FakeTCPServer:
    def __init__(self, online_ids=None):
        self.clients_lock = threading.Lock()
        self.client_id_map = {cid: ("127.0.0.1", 12345) for cid in (online_ids or [])}


class FakeDeviceManager:
    def __init__(self, devices=None):
        self._devices = {d["id"]: d for d in (devices or [])}

    def get_all_device_info(self):
        return list(self._devices.values())

    def get_device_info_by_id(self, device_id):
        return self._devices.get(device_id)

    def update_device_type(self, device_id, device_type):
        item = self._devices.get(device_id)
        if item is None:
            return False
        item["type"] = device_type
        return True


class FakeDBManager:
    def __init__(self, device_manager):
        self.device_manager = device_manager


class TestDeviceHandlers(AsyncHTTPTestCase):
    def get_app(self):
        devices = [
            {
                "id": "dev-1",
                "client_id": "cid-1",
                "hostname": "host-1",
                "alias": "",
                "services": [{"name": "svc1"}],
                "processes": [{"name": "proc1"}, {"name": "proc2"}],
                "networks": [{"name": "eth0", "ip_address": "10.0.0.2"}],
                "cpu_info": {},
                "memory_info": {},
                "disk_info": {},
                "os_name": "Windows",
                "os_version": "11",
                "os_architecture": "x64",
                "machine_type": "Desktop",
                "type": "pc",
                "timestamp": "",
                "created_at": "",
            }
        ]

        self.tcp = FakeTCPServer(["cid-1"])
        self.dbm = FakeDBManager(FakeDeviceManager(devices))
        return tornado.web.Application(
            [
                (
                    r"/api/devices",
                    DevicesHandler,
                    dict(db_manager=self.dbm, get_tcp_server_func=lambda: self.tcp),
                ),
                (
                    r"/api/devices/(?P<device_id>[^/]+)",
                    DeviceHandler,
                    dict(db_manager=self.dbm, get_tcp_server_func=lambda: self.tcp),
                ),
                (
                    r"/api/devices/(?P<device_id>[^/]+)/type",
                    DeviceTypeHandler,
                    dict(db_manager=self.dbm),
                ),
            ]
        )

    def test_devices_list_contains_ips_and_online(self):
        resp = self.fetch("/api/devices")
        assert resp.code == 200
        data = json.loads(resp.body.decode("utf-8"))
        assert data["status"] == "success"
        assert data["count"] == 1
        item = data["data"][0]
        assert item["services_count"] == 1
        assert item["processes_count"] == 2
        assert item["ips"] == ["eth0: 10.0.0.2"]
        assert item["online"] is True

    def test_device_handler_404(self):
        resp = self.fetch("/api/devices/not-exists")
        assert resp.code == 404

    def test_device_type_handler_success(self):
        body = json.dumps({"type": "pc"}).encode("utf-8")
        r = self.fetch("/api/devices/dev-1/type", method="PUT", body=body)
        assert r.code == 200
