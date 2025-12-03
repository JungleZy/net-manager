import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.base_handler import BaseHandler


class EchoHandler(BaseHandler):
    def get(self):
        self.write({"你好": "世界"})


class TestBaseHandler(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application([
            (r"/echo", EchoHandler),
        ])

    def test_headers_and_write(self):
        r = self.fetch("/echo")
        assert r.code == 200
        assert r.headers["Access-Control-Allow-Origin"] == "*"
        data = json.loads(r.body.decode("utf-8"))
        assert data["你好"] == "世界"

    def test_options(self):
        r = self.fetch("/echo", method="OPTIONS")
        assert r.code == 204
