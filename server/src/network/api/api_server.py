#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于Tornado的RESTful API服务
提供系统信息查询接口
"""
import os
import sys
from typing import Dict, Any
import tornado.web
import tornado.ioloop
import tornado.httpserver

from src.core.config import API_PORT, API_HOST
from src.core.logger import logger
from src.database import DatabaseManager
from src.database.managers.topology_manager import TopologyManager

# 导入拆分后的handlers
from src.network.api.handlers.main_handler import MainHandler
from src.network.api.handlers.devices_handlers import (
    DeviceCreateHandler,
    DeviceUpdateHandler,
    DeviceDeleteHandler,
    DeviceHandler,
    DeviceTypeHandler,
    DevicesHandler,
)
from src.network.api.handlers.switches_handlers import (
    SwitchCreateHandler,
    SwitchUpdateHandler,
    SwitchDeleteHandler,
    SwitchHandler,
    SwitchesHandler,
)
from src.network.api.handlers.snmp_scan_handler import (
    SNMPScanHandler,
    SNMPScanHandlerSimple,
)
from src.network.api.handlers.topology_handlers import (
    TopologyCreateHandler,
    TopologyUpdateHandler,
    TopologyDeleteHandler,
    TopologyHandler,
    TopologiesHandler,
    TopologyLatestHandler,
)
from src.network.api.handlers.health_handler import HealthHandler
from src.network.api.handlers.performance_handler import PerformanceHandler
from src.network.api.websocket_handler import WebSocketHandler
from src.network.api.handlers.static_handler import StaticFileHandler


class APIServer:
    """API服务器类"""

    def __init__(self, db_manager=None, port=API_PORT, host=API_HOST):
        self.port = port
        self.host = host
        # 如果传入了数据库管理器实例，则使用它；否则创建新的实例
        self.db_manager = db_manager if db_manager else DatabaseManager()
        # 初始化拓扑图管理器
        self.topology_manager = TopologyManager()
        self.tcp_server = None
        self.app = self.make_app()
        self.server = None

    def set_tcp_server(self, tcp_server):
        """设置TCP服务器引用，用于获取在线状态"""
        self.tcp_server = tcp_server

    def get_tcp_server(self):
        """获取TCP服务器引用"""
        return self.tcp_server

    def make_app(self):
        """创建Tornado应用"""
        # 获取静态文件目录（开发环境和打包后的路径不同）
        if getattr(sys, "frozen", False):
            # 如果是打包后的可执行文件
            # 使用sys.argv[0]获取实际的可执行文件路径（而不是临时解压目录）
            exe_path = os.path.abspath(sys.argv[0])
            exe_dir = os.path.dirname(exe_path)
            static_path = os.path.join(exe_dir, "static")
        else:
            # 开发环境
            static_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "static"
            )

        # 标准化路径
        static_path = os.path.abspath(static_path)

        # 检查静态文件目录是否存在
        static_exists = os.path.exists(static_path)
        if static_exists:
            logger.info(f"静态文件目录: {static_path}")
        else:
            logger.warning(f"静态文件目录不存在: {static_path}")

        routes = [
            # API路由必须在静态文件路由之前，避免被静态文件处理器拦截
            (r"/ws", WebSocketHandler),
            (r"/api/performance", PerformanceHandler),
            (r"/health", HealthHandler),
            (r"/healthz", HealthHandler),  # Kubernetes健康检查标准端点
            (
                r"/api/devices",
                DevicesHandler,
                dict(
                    db_manager=self.db_manager,
                    get_tcp_server_func=self.get_tcp_server,
                ),
            ),
            (
                r"/api/devices/(?P<device_id>[^/]+)/type",
                DeviceTypeHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/devices/create",
                DeviceCreateHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/devices/update",
                DeviceUpdateHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/devices/delete",
                DeviceDeleteHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/devices/(?P<device_id>[^/]+)",
                DeviceHandler,
                dict(
                    db_manager=self.db_manager,
                    get_tcp_server_func=self.get_tcp_server,
                ),
            ),
            (r"/api/switches", SwitchesHandler, dict(db_manager=self.db_manager)),
            (
                r"/api/switches/create",
                SwitchCreateHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/switches/update",
                SwitchUpdateHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/switches/delete",
                SwitchDeleteHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/switches/scan",
                SNMPScanHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/switches/scan/simple",
                SNMPScanHandlerSimple,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/switches/([^/]+)",
                SwitchHandler,
                dict(db_manager=self.db_manager),
            ),
            # 拓扑图相关路由（注意：具体路径必须放在通配符路由之前）
            (
                r"/api/topologies/latest",
                TopologyLatestHandler,
                dict(topology_manager=self.topology_manager),
            ),
            (
                r"/api/topologies/create",
                TopologyCreateHandler,
                dict(topology_manager=self.topology_manager),
            ),
            (
                r"/api/topologies/update",
                TopologyUpdateHandler,
                dict(topology_manager=self.topology_manager),
            ),
            (
                r"/api/topologies/delete",
                TopologyDeleteHandler,
                dict(topology_manager=self.topology_manager),
            ),
            (
                r"/api/topologies",
                TopologiesHandler,
                dict(topology_manager=self.topology_manager),
            ),
            (
                r"/api/topologies/(?P<topology_id>[^/]+)",
                TopologyHandler,
                dict(topology_manager=self.topology_manager),
            ),
            (r"/ws", WebSocketHandler),
            (r"/api/performance", PerformanceHandler),
            (r"/health", HealthHandler),
            (r"/healthz", HealthHandler),  # Kubernetes健康检查标准端点
            # 静态文件服务（必须放在最后，作为SPA应用的默认处理器）
            (
                r"/(.*)",
                StaticFileHandler,
                {"path": static_path, "default_filename": "index.html"},
            ),
        ]

        # 创建应用配置
        settings: Dict[str, Any] = {
            "debug": False,
        }

        return tornado.web.Application(routes, **settings)

    def start(self):
        """启动API服务器"""
        self.server = tornado.httpserver.HTTPServer(
            self.app,
            xheaders=True,
            max_buffer_size=10485760,  # 10MB buffer size
        )

        try:
            # 根据操作系统决定是否使用reuse_port选项
            import platform

            is_windows = platform.system() == "Windows"

            # 设置socket选项，Windows不支持reuse_port
            sockets = tornado.netutil.bind_sockets(
                self.port,
                address=self.host,
                reuse_port=not is_windows,  # Windows不支持reuse_port
            )
            self.server.add_sockets(sockets)

            # 设置StateManager的主线程IOLoop引用
            from src.core.state_manager import state_manager

            state_manager.set_main_ioloop(tornado.ioloop.IOLoop.current())
        except OSError as e:
            logger.error(f"无法绑定到端口 {self.host}: {str(e)}")
            return False, f"无法绑定到端口 {self.host}: {str(e)}"

        logger.info(f"API服务端启动，监听端口 {self.port}")
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        """停止API服务器"""
        if self.server:
            self.server.stop()
        tornado.ioloop.IOLoop.current().stop()
        logger.info("API服务端已停止")


if __name__ == "__main__":
    # 使用配置文件中的端口启动API服务器
    api_server = APIServer()
    api_server.start()
