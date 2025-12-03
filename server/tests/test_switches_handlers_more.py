import json
import tornado.web
from tornado.testing import AsyncHTTPTestCase
from src.network.api.handlers.switches_handlers import (
    SwitchCreateHandler,
    SwitchUpdateHandler,
    SwitchDeleteHandler,
    SwitchHandler,
    SwitchesHandler,
)


class ExistsMgr:
    def switch_exists(self, ip, ver):
        return True

    def add_switch(self, si):
        return False, "exists"

    def update_switch(self, si):
        return True, "ok"

    def delete_switch(self, sid):
        return True, "ok"

    def get_switch_by_id(self, sid):
        return None


class TestSwitchesHandlersMore(AsyncHTTPTestCase):
    def get_app(self):
        class DB:
            def __init__(self):
                self.switch_manager = ExistsMgr()

        self.db = DB()

        class BadUpdate:
            def __init__(self):
                class SM:
                    def update_switch(self2, si):
                        raise RuntimeError("err")

                self.switch_manager = SM()

        class BadDelete:
            def __init__(self):
                class SM:
                    def delete_switch(self2, sid):
                        raise RuntimeError("err")

                self.switch_manager = SM()

        class BadCreate:
            def __init__(self):
                class SM:
                    def switch_exists(self2, ip, ver):
                        return False

                    def add_switch(self2, si):
                        return False, "bad"

                self.switch_manager = SM()

        class BadUpdateFalse:
            def __init__(self):
                class SM:
                    def update_switch(self2, si):
                        return False, "bad"

                self.switch_manager = SM()

        class BadDeleteFalse:
            def __init__(self):
                class SM:
                    def delete_switch(self2, sid):
                        return False, "bad"

                self.switch_manager = SM()

        class OneExc:
            def __init__(self):
                class SM:
                    def get_switch_by_id(self2, sid):
                        raise RuntimeError("err")

                self.switch_manager = SM()

        class ListExc:
            def __init__(self):
                class SM:
                    def get_all_switches(self2):
                        raise RuntimeError("err")

                self.switch_manager = SM()

        return tornado.web.Application(
            [
                (r"/create", SwitchCreateHandler, dict(db_manager=self.db)),
                (r"/update", SwitchUpdateHandler, dict(db_manager=self.db)),
                (r"/delete", SwitchDeleteHandler, dict(db_manager=self.db)),
                (r"/one/(?P<switch_id>[^/]+)", SwitchHandler, dict(db_manager=self.db)),
                (r"/u", SwitchUpdateHandler, dict(db_manager=BadUpdate())),
                (r"/d", SwitchDeleteHandler, dict(db_manager=BadDelete())),
                (r"/create_exc", SwitchCreateHandler, dict(db_manager=BadCreate())),
                (r"/create_bad", SwitchCreateHandler, dict(db_manager=BadCreate())),
                (
                    r"/update_bad",
                    SwitchUpdateHandler,
                    dict(db_manager=BadUpdateFalse()),
                ),
                (
                    r"/delete_bad",
                    SwitchDeleteHandler,
                    dict(db_manager=BadDeleteFalse()),
                ),
                (
                    r"/one_exc/(?P<switch_id>[^/]+)",
                    SwitchHandler,
                    dict(db_manager=OneExc()),
                ),
                (r"/list_exc", SwitchesHandler, dict(db_manager=ListExc())),
            ]
        )

    def test_create_exists(self):
        body = json.dumps({"ip": "1.2.3.4", "snmp_version": "2c"}).encode("utf-8")
        r = self.fetch("/create", method="POST", body=body)
        assert r.code == 400

    def test_json_decode_error(self):
        r = self.fetch("/create", method="POST", body=b"{")
        assert r.code == 400
        r = self.fetch("/update", method="POST", body=b"{")
        assert r.code == 400
        r = self.fetch("/delete", method="POST", body=b"{")
        assert r.code == 400

        # general exception path
        class BadCreate:
            def __init__(self):
                class SM:
                    def switch_exists(self2, ip, ver):
                        return False

                    def add_switch(self2, si):
                        raise RuntimeError("x")

                self.switch_manager = SM()

        app = tornado.web.Application(
            [
                (r"/create_exc", SwitchCreateHandler, dict(db_manager=BadCreate())),
            ]
        )
        body = json.dumps({"ip": "1.2.3.4", "snmp_version": "2c"}).encode("utf-8")
        r = self.fetch("/create_exc", method="POST", body=body)
        assert r.code in (400, 500)

    def test_create_general_exception(self):
        import src.network.api.handlers.switches_handlers as sh

        orig = sh.tornado.escape.json_decode
        try:
            sh.tornado.escape.json_decode = lambda body: (_ for _ in ()).throw(
                RuntimeError("x")
            )
            r = self.fetch(
                "/create",
                method="POST",
                body=json.dumps({"ip": "1.2.3.4", "snmp_version": "2c"}).encode(
                    "utf-8"
                ),
            )
            assert r.code == 500
        finally:
            sh.tornado.escape.json_decode = orig

    def test_switch_handler_value_error(self):
        r = self.fetch("/one/abc")
        assert r.code == 400

    def test_create_false(self):
        body = json.dumps({"ip": "1.2.3.4", "snmp_version": "2c"}).encode("utf-8")
        r = self.fetch("/create_bad", method="POST", body=body)
        assert r.code == 400

    def test_switch_handler_exception(self):
        r = self.fetch("/one_exc/1")
        assert r.code == 500

    def test_list_exception(self):
        r = self.fetch("/list_exc")
        assert r.code == 500

    def test_update_false(self):
        body = json.dumps({"id": 1, "ip": "1.2.3.4", "snmp_version": "2c"}).encode(
            "utf-8"
        )
        r = self.fetch("/update_bad", method="POST", body=body)
        assert r.code == 400

    def test_delete_missing_field(self):
        r = self.fetch("/delete", method="POST", body=json.dumps({}).encode("utf-8"))
        assert r.code == 400

    def test_delete_false(self):
        body = json.dumps({"id": 1}).encode("utf-8")
        r = self.fetch("/delete_bad", method="POST", body=body)
        assert r.code == 400

    def test_update_invalid_id_type(self):
        body = json.dumps({"id": "abc", "ip": "1.2.3.4", "snmp_version": "2c"}).encode(
            "utf-8"
        )
        r = self.fetch("/update", method="POST", body=body)
        assert r.code == 400

    def test_update_internal_error(self):
        class BadMgr:
            def __init__(self):
                class SM:
                    def update_switch(self2, si):
                        raise RuntimeError("err")

                self.switch_manager = SM()

        body = json.dumps({"id": 1, "ip": "1.2.3.4", "snmp_version": "2c"}).encode(
            "utf-8"
        )
        r = self.fetch("/u", method="POST", body=body)
        assert r.code == 500

    def test_delete_internal_error(self):
        class BadMgr:
            def __init__(self):
                class SM:
                    def delete_switch(self2, sid):
                        raise RuntimeError("err")

                self.switch_manager = SM()

        body = json.dumps({"id": 1}).encode("utf-8")
        r = self.fetch("/d", method="POST", body=body)
        assert r.code == 500
