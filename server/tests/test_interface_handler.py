import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
import src.network.api.handlers.interface_handlers as ih
from src.network.api.handlers.interface_handlers import InterfaceTrafficHandler


class FakeSNMP:
    async def get_interface_statistics(self, ip, version, **kwargs):
        return [{"index": 1, "description": "eth0", "upload_bps": 1, "download_bps": 2}]


class TestInterfaceHandler(AsyncHTTPTestCase):
    def get_app(self):
        ih.SNMPManager = lambda db_manager=None: FakeSNMP()
        return tornado.web.Application(
            [
                (
                    r"/api/interfaces/traffic",
                    InterfaceTrafficHandler,
                    dict(db_manager=None),
                ),
            ]
        )

    def test_missing_ip(self):
        r = self.fetch("/api/interfaces/traffic")
        assert r.code == 400

    def test_v2c(self):
        r = self.fetch("/api/interfaces/traffic?ip=1.2.3.4&version=v2c")
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["code"] == 0

    def test_v3(self):
        r = self.fetch(
            "/api/interfaces/traffic?ip=1.2.3.4&version=v3&username=u&authKey=a&privKey=p&level=authPriv"
        )
        assert r.code == 200

    def test_error_branch(self):
        class Bad:
            async def get_interface_statistics(self, *a, **k):
                raise RuntimeError("err")

        ih.SNMPManager = lambda db_manager=None: Bad()
        r = self.fetch("/api/interfaces/traffic?ip=1.2.3.4")
        assert r.code == 500
