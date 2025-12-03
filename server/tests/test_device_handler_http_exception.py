import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.devices_handlers import DeviceHandler


class TestDeviceHandlerHttpException(AsyncHTTPTestCase):
    def get_app(self):
        class BadDM:
            def __init__(self):
                class Dev:
                    def get_device_info_by_id(self2, x):
                        raise RuntimeError("e")
                self.device_manager = Dev()
        return tornado.web.Application([
            (r"/onebad/(?P<device_id>[^/]+)", DeviceHandler, dict(db_manager=BadDM(), get_tcp_server_func=None)),
        ])

    def test_http_exception(self):
        r = self.fetch("/onebad/d")
        assert r.code == 500
