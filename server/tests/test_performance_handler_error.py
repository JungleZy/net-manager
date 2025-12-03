import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
import src.network.api.handlers.performance_handler as ph
from src.network.api.handlers.performance_handler import PerformanceHandler


def bad_monitor():
    raise RuntimeError("fail")


class TestPerformanceHandlerError(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application([
            (r"/perf", PerformanceHandler),
        ])

    def test_error_branch(self):
        ph.get_server_monitor = bad_monitor
        r = self.fetch("/perf")
        assert r.code == 500
        data = json.loads(r.body.decode("utf-8"))
        assert data["code"] == 500
