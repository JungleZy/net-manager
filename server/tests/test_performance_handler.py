import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.performance_handler import PerformanceHandler


class TestPerformanceHandler(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application([
            (r"/api/performance", PerformanceHandler),
        ])

    def test_performance_endpoint(self):
        resp = self.fetch("/api/performance")
        assert resp.code == 200
        data = json.loads(resp.body.decode("utf-8"))
        assert data["code"] == 0
        assert data["message"] == "success"
        assert isinstance(data["data"], dict)
