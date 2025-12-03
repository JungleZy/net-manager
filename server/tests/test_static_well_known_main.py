import os
import json
import tempfile
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.static_handler import StaticFileHandler
from src.network.api.handlers.well_known_handler import WellKnownHandler
from src.network.api.handlers.main_handler import MainHandler


class TestStaticWellKnownMain(AsyncHTTPTestCase):
    def get_app(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        index_path = os.path.join(self.tmpdir.name, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("<html>ok</html>")
        return tornado.web.Application(
            [
                (r"/", MainHandler),
                (r"/.well-known/(.*)", WellKnownHandler),
                (
                    r"/(.*)",
                    StaticFileHandler,
                    {"path": self.tmpdir.name, "default_filename": "index.html"},
                ),
            ]
        )

    def test_main(self):
        r = self.fetch("/")
        assert r.code == 200
        data = json.loads(r.body.decode("utf-8"))
        assert data["message"]

    def test_wellknown(self):
        r = self.fetch("/.well-known/abc")
        assert r.code == 404

    def test_static_fallback(self):
        r = self.fetch("/non-existent-route")
        assert r.code == 200

    def test_static_options(self):
        import tornado.httputil

        app = tornado.web.Application([])
        req = tornado.httputil.HTTPServerRequest(method="OPTIONS")
        req.connection = type("C", (), {"set_close_callback": lambda self, cb: None})()
        h = StaticFileHandler(
            app, req, path=self.tmpdir.name, default_filename="index.html"
        )
        h._transforms = []
        h.finish = lambda: None
        h.options()

    def test_static_rethrow(self):
        r = self.fetch("/file.js")
        assert r.code == 404
