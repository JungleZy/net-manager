#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康检查处理器
"""

from .base_handler import BaseHandler


class HealthHandler(BaseHandler):
    """健康检查处理器"""
    
    def get(self):
        self.write({
            "status": "healthy",
            "service": "Net Manager API Server"
        })