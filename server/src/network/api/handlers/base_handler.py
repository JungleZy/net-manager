#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础处理器类
"""

import json
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    """基础处理器类，提供通用功能如CORS支持"""

    def set_default_headers(self):
        """设置默认响应头，支持CORS"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.set_header(
            "Access-Control-Allow-Headers", "x-requested-with, Content-Type"
        )
        self.set_header("Access-Control-Max-Age", "86400")  # 24小时
        # 设置Content-Type为UTF-8编码的JSON
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def options(self, *args):
        """处理OPTIONS预检请求"""
        self.set_status(204)
        self.finish()

    def write(self, chunk):
        """重写write方法，确保中文以UTF-8编码而非Unicode转义序列输出"""
        if isinstance(chunk, dict):
            # 将字典序列化为JSON，使用ensure_ascii=False确保中文正常显示
            chunk = json.dumps(chunk, ensure_ascii=False, separators=(",", ":"))
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        super(BaseHandler, self).write(chunk)
