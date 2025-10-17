#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器性能监控处理器
提供当前性能数据的HTTP接口
"""

from .base_handler import BaseHandler
from src.monitor.server_monitor import get_server_monitor


class PerformanceHandler(BaseHandler):
    """服务器性能数据处理器"""

    def get(self):
        """
        获取当前服务器性能数据

        返回格式与WebSocket推送的数据一致
        """
        try:
            # 获取监控器实例
            monitor = get_server_monitor()

            # 收集当前性能数据
            performance_data = monitor._collect_performance_data()

            self.write({"code": 0, "message": "success", "data": performance_data})
        except Exception as e:
            self.set_status(500)
            self.write(
                {"code": 500, "message": f"获取性能数据失败: {str(e)}", "data": None}
            )
