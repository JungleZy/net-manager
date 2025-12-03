#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import tornado.web

from src.network.api.handlers.base_handler import BaseHandler


class SNMPHistoryQueryHandler(BaseHandler):
    def initialize(self, db_manager):
        self.db_manager = db_manager

    def get(self, switch_id):
        try:
            limit = int(self.get_argument("limit", 100))
            offset = int(self.get_argument("offset", 0))
            poll_type = self.get_argument("poll_type", None)
            data = self.db_manager.snmp_history_manager.query_history(
                int(switch_id), limit=limit, offset=offset, poll_type=poll_type
            )
            self.set_header("Content-Type", "application/json")
            self.finish(
                json.dumps({"status": "success", "data": data}, ensure_ascii=False)
            )
        except Exception as e:
            self.set_status(500)
            self.finish(
                json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
            )


class SNMPHistoryClearHandler(BaseHandler):
    def initialize(self, db_manager):
        self.db_manager = db_manager

    def post(self):
        try:
            switch_id_arg = self.get_argument("switch_id", None)
            if switch_id_arg is None:
                try:
                    raw = (
                        self.request.body.decode("utf-8") if self.request.body else "{}"
                    )
                    data = json.loads(raw) if raw else {}
                    switch_id_arg = data.get("switch_id")
                except Exception:
                    switch_id_arg = None
            switch_id = int(switch_id_arg) if switch_id_arg is not None else None
            ok, msg = self.db_manager.snmp_history_manager.clear_history(switch_id)
            self.set_header("Content-Type", "application/json")
            self.finish(
                json.dumps({"status": "success", "message": msg}, ensure_ascii=False)
            )
        except Exception as e:
            self.set_status(500)
            self.finish(
                json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
            )
