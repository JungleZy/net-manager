#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tornado


class WellKnownHandler(tornado.web.RequestHandler):
    def get(self, path):
        self.set_status(404)
        self.finish()
