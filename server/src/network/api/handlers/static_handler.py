#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""静态文件处理器模块"""

import os
import tornado.web


class StaticFileHandler(tornado.web.StaticFileHandler):
    """提供静态文件服务，支持SPA路由回退"""

    def set_default_headers(self):
        """设置允许CORS的HTTP头"""
        # 允许CORS
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Headers", "x-requested-with, content-type"
        )
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def options(self):
        """处理OPTIONS请求"""
        self.set_status(204)
        self.finish()

    def validate_absolute_path(self, root, absolute_path):
        """验证绝对路径，如果文件不存在则返回index.html（支持SPA路由）"""
        try:
            # 尝试使用父类方法验证路径
            return super().validate_absolute_path(root, absolute_path)
        except tornado.web.HTTPError as e:
            # 如果是404错误，并且请求的不是静态资源文件（如.js, .css, .png等）
            if e.status_code == 404:
                # 获取请求的路径
                request_path = self.request.path
                # 如果是目录或者看起来像是路由路径（不包含文件扩展名），返回index.html
                if not os.path.splitext(request_path)[1] or request_path.endswith("/"):
                    # 返回index.html
                    return super().validate_absolute_path(
                        root, os.path.join(root, "index.html")
                    )
            # 其他情况抛出原异常
            raise
