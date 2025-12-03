import sys
import threading
import tornado.ioloop
import tornado.netutil
from src.network.api.api_server import APIServer
import runpy


def test_api_server_make_app_branches():
    orig = getattr(sys, "frozen", False)
    try:
        sys.frozen = False
        s = APIServer(port=0, host="127.0.0.1")
        app1 = s.make_app()
        assert app1 is not None

        sys.frozen = True
        app2 = s.make_app()
        assert app2 is not None
    finally:
        if orig:
            sys.frozen = True
        else:
            if hasattr(sys, "frozen"):
                delattr(sys, "frozen")


def test_api_server_tcp_server_refs():
    s = APIServer(port=0, host="127.0.0.1")
    o = object()
    s.set_tcp_server(o)
    assert s.get_tcp_server() is o


def test_api_server_start_error_branch_and_stop():
    s = APIServer(port=0, host="127.0.0.1")
    orig = tornado.netutil.bind_sockets
    try:

        def boom(*args, **kwargs):
            raise OSError("bind fail")

        tornado.netutil.bind_sockets = boom
        ok, msg = s.start()
        assert ok is False
        fake = type("_", (), {"stop": lambda self: None})()
        s.server = fake
        s.stop()
    finally:
        tornado.netutil.bind_sockets = orig


def test_api_server_start_success_branch():
    s = APIServer(port=0, host="127.0.0.1")
    orig_bind = tornado.netutil.bind_sockets
    orig_start = tornado.ioloop.IOLoop.start
    try:

        class FakeSock:
            def fileno(self):
                return 1

        tornado.netutil.bind_sockets = lambda *a, **k: [FakeSock()]
        tornado.ioloop.IOLoop.start = lambda self: None
        s.start()
        s.server = type("_", (), {"stop": lambda self: None})()
        s.stop()
    finally:
        tornado.netutil.bind_sockets = orig_bind
        tornado.ioloop.IOLoop.start = orig_start


def test_api_server_main_guard():
    orig_bind = tornado.netutil.bind_sockets
    orig_start = tornado.ioloop.IOLoop.start
    try:
        tornado.netutil.bind_sockets = lambda *a, **k: []
        tornado.ioloop.IOLoop.start = lambda self: None
        runpy.run_module("src.network.api.api_server", run_name="__main__")
    finally:
        tornado.netutil.bind_sockets = orig_bind
        tornado.ioloop.IOLoop.start = orig_start
