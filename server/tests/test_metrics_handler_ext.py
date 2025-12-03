import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
import src.network.api.handlers.metrics_handler as mh
from src.network.api.handlers.metrics_handler import MetricsHandler


class FakeDB:
    def health_check(self):
        return True


class FakeTCP:
    def __init__(self):
        import threading

        self.clients_lock = threading.Lock()
        self.client_id_map = {"cid": ("127.0.0.1", 1)}
        self.clients = {("127.0.0.1", 1)}


class TestMetricsHandlerExt(AsyncHTTPTestCase):
    def get_app(self):
        self.db = FakeDB()
        self.tcp = FakeTCP()

        class BadDB:
            def health_check(self):
                raise RuntimeError("db")

        def bad_get_tcp():
            raise RuntimeError("tcp")

        return tornado.web.Application(
            [
                (
                    r"/metrics",
                    MetricsHandler,
                    dict(db_manager=self.db, get_tcp_server_func=lambda: self.tcp),
                ),
                (
                    r"/m1",
                    MetricsHandler,
                    dict(db_manager=BadDB(), get_tcp_server_func=bad_get_tcp),
                ),
            ]
        )

    def test_enabled(self):
        mh.METRICS_ENABLED = True
        r = self.fetch("/metrics")
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["status"] == "success"

    def test_disabled(self):
        mh.METRICS_ENABLED = False
        r = self.fetch("/metrics")
        assert r.code == 404

    def test_error_branches(self):
        mh.METRICS_ENABLED = True

        r = self.fetch("/m1")
        assert r.code == 200
        import sys, types

        mod = types.SimpleNamespace()
        mod.get_device_poller = lambda: type(
            "P", (), {"get_statistics": lambda self: {"a": 1}}
        )()
        mod.get_interface_poller = lambda: type(
            "P", (), {"get_statistics": lambda self: {"b": 2}}
        )()
        sys.modules["src.snmp.unified_poller"] = mod
        r = self.fetch("/metrics")
        assert r.code == 200

    def test_snmp_and_state_errors(self):
        mh.METRICS_ENABLED = True
        import sys, types

        mod = types.SimpleNamespace()
        mod.get_device_poller = lambda: type(
            "P", (), {"get_statistics": lambda self: {"a": 1}}
        )()
        mod.get_interface_poller = lambda: type(
            "P",
            (),
            {"get_statistics": lambda self: (_ for _ in ()).throw(RuntimeError("x"))},
        )()
        sys.modules["src.snmp.unified_poller"] = mod
        import sys
        import types

        orig = sys.modules.get("src.core.state_manager")

        class BadMod(types.SimpleNamespace):
            def __getattr__(self, name):
                raise RuntimeError("bad")

        sys.modules["src.core.state_manager"] = BadMod()
        try:
            r = self.fetch("/metrics")
            assert r.code == 200
        finally:
            if orig is not None:
                sys.modules["src.core.state_manager"] = orig
