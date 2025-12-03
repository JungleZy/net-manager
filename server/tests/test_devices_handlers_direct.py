import tornado.web
import tornado.httputil
from src.network.api.handlers.devices_handlers import DevicesHandler, DeviceHandler


def make_req(method="GET"):
    req = tornado.httputil.HTTPServerRequest(method=method)
    req.connection = type("C", (), {"set_close_callback": lambda self, cb: None})()
    return req


def test_devices_handler_get_online_status_false_paths():
    app = tornado.web.Application([])
    h = DevicesHandler(app, make_req(), db_manager=None, get_tcp_server_func=None)
    assert h.get_online_status("cid") is False

    h2 = DevicesHandler(
        app, make_req(), db_manager=None, get_tcp_server_func=lambda: None
    )
    assert h2.get_online_status("cid") is False


def test_device_handler_get_online_status_all_paths():
    class DM:
        def __init__(self, ret):
            self.ret = ret

        def get_device_info_by_id(self, x):
            return self.ret

    app = tornado.web.Application([])

    # not found
    h1 = DeviceHandler(
        app,
        make_req(),
        db_manager=type("DB", (), {"device_manager": DM(None)})(),
        get_tcp_server_func=None,
    )
    assert h1.get_online_status("d") is False

    # client_id missing
    h2 = DeviceHandler(
        app,
        make_req(),
        db_manager=type("DB", (), {"device_manager": DM({"id": "d"})})(),
        get_tcp_server_func=None,
    )
    assert h2.get_online_status("d") is False

    # tcp func missing
    h3 = DeviceHandler(
        app,
        make_req(),
        db_manager=type(
            "DB", (), {"device_manager": DM({"id": "d", "client_id": "c"})}
        )(),
        get_tcp_server_func=None,
    )
    assert h3.get_online_status("d") is False

    # tcp server None
    h4 = DeviceHandler(
        app,
        make_req(),
        db_manager=type(
            "DB", (), {"device_manager": DM({"id": "d", "client_id": "c"})}
        )(),
        get_tcp_server_func=lambda: None,
    )
    assert h4.get_online_status("d") is False

    # in map
    h5 = DeviceHandler(
        app,
        make_req(),
        db_manager=type(
            "DB", (), {"device_manager": DM({"id": "d", "client_id": "c"})}
        )(),
        get_tcp_server_func=lambda: tcp,
    )
    tcp = type(
        "T",
        (),
        {"clients_lock": __import__("threading").Lock(), "client_id_map": {"c": 1}},
    )()
    assert h5.get_online_status("d") is True


def test_device_handler_get_online_status_exception():
    class DM:
        def get_device_info_by_id(self, x):
            raise RuntimeError("e")

    app = tornado.web.Application([])
    h = DeviceHandler(
        app,
        make_req(),
        db_manager=type("DB", (), {"device_manager": DM()})(),
        get_tcp_server_func=None,
    )
    assert h.get_online_status("d") is False
