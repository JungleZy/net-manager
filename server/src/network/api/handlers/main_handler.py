#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主页处理器
"""

from .base_handler import BaseHandler


class MainHandler(BaseHandler):
    """主页处理器 - 返回简单的欢迎信息"""
    def get(self):
        self.write({
            "message": "欢迎使用Net Manager API服务",
            "version": "1.0.0",
            "documentation": "/api/docs"
        })