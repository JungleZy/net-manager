#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础处理器类
"""

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    """基础处理器类，提供通用功能如CORS支持"""
    def set_default_headers(self):
        """设置默认响应头，支持CORS"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type")
        self.set_header("Access-Control-Max-Age", "86400")  # 24小时
    
    def options(self, *args):
        """处理OPTIONS预检请求"""
        self.set_status(204)
        self.finish()