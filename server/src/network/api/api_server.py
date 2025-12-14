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

from src.core.config import API_PORT, API_HOST, METRICS_ENABLED, METRICS_ROUTE, SNMP_HISTORY_RETENTION_DAYS, SNMP_HISTORY_PURGE_INTERVAL_MIN
from src.core.logger import logger
from src.database import DatabaseManager
from src.database.managers.topology_manager import TopologyManager
from src.database.managers.resident_process_manager import ResidentProcessManager

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
from src.network.api.handlers.interface_handlers import InterfaceTrafficHandler
from src.network.api.handlers.topology_handlers import (
    TopologyCreateHandler,
    TopologyUpdateHandler,
    TopologyDeleteHandler,
    TopologyHandler,
    TopologiesHandler,
    TopologyLatestHandler,
)
from src.network.api.handlers.resident_process_handlers import (
    ResidentProcessListHandler,
    ResidentProcessCreateHandler,
    ResidentProcessBatchCreateHandler,
    ResidentProcessDeleteHandler,
    ResidentProcessClearHandler,
    ResidentProcessGetHandler,
)
from src.network.api.handlers.health_handler import HealthHandler
from src.network.api.handlers.performance_handler import PerformanceHandler
from src.network.api.handlers.metrics_handler import MetricsHandler
from src.network.api.websocket_handler import WebSocketHandler
from src.network.api.handlers.static_handler import StaticFileHandler
from src.network.api.handlers.well_known_handler import WellKnownHandler
from src.network.api.handlers.snmp_history_handlers import (
    SNMPHistoryQueryHandler,
    SNMPHistoryClearHandler,
)


class APIServer:
    """基于Tornado的RESTful API服务器
    
    提供以下功能：
    - 设备管理API
    - 交换机管理API
    - 拓扑图管理API
    - 常驻进程管理API
    - SNMP扫描和历史查询API
    - WebSocket实时通信
    - 静态文件服务（用于前端应用）
    - 健康检查端点
    - 性能监控端点
    """

    def __init__(self, db_manager=None, port=API_PORT, host=API_HOST):
        """初始化API服务器
        
        Args:
            db_manager: 数据库管理器实例
            port: API服务监听端口
            host: API服务监听地址
        """
        self.port = port
        self.host = host
        
        # 复用或创建数据库管理器实例
        self.db_manager = db_manager if db_manager else DatabaseManager()
        
        # 初始化异步数据库连接池
        try:
            self.db_manager.init_async_pool()
        except Exception:
            logger.debug("无法初始化异步数据库连接池")
        
        # 初始化各种管理器
        self.topology_manager = TopologyManager()  # 拓扑图管理器
        self.resident_process_manager = ResidentProcessManager()  # 常驻进程管理器
        
        self.tcp_server = None  # TCP服务器引用，用于获取设备在线状态
        self.app = self.make_app()  # 创建Tornado应用
        self.server = None  # HTTPServer实例
        self._history_purge_callback = None  # SNMP历史数据清理定时任务

    def set_tcp_server(self, tcp_server):
        """设置TCP服务器引用
        
        Args:
            tcp_server: TCP服务器实例，用于获取设备在线状态
        """
        self.tcp_server = tcp_server

    def get_tcp_server(self):
        """获取TCP服务器引用
        
        Returns:
            TCPServer: TCP服务器实例
        """
        return self.tcp_server

    def make_app(self):
        """创建并配置Tornado应用
        
        Returns:
            tornado.web.Application: 配置好的Tornado应用实例
        """
        # 确定静态文件目录（适配开发和生产环境）
        if getattr(sys, "frozen", False):
            # 打包后的可执行文件环境
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

        # 定义API路由规则
        routes = [
            # WebSocket和基础服务端点
            (r"/ws", WebSocketHandler),  # WebSocket实时通信
            (r"/api/performance", PerformanceHandler),  # 性能监控
            (r"/health", HealthHandler),  # 健康检查
            (r"/healthz", HealthHandler),  # Kubernetes标准健康检查端点
            
            # 设备管理API
            (
                r"/api/devices",
                DevicesHandler,
                dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server),
            ),
            # 设备类型管理API
            (
                r"/api/devices/(?P<device_id>[^/]+)/type",
                DeviceTypeHandler,
                dict(db_manager=self.db_manager),
            ),
            # 设备CRUD操作
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
                dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server),
            ),
            
            # 轻量指标端点（可配置开关）
            (
                (
                    METRICS_ROUTE,
                    MetricsHandler,
                    dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server),
                )
                if METRICS_ENABLED
                else None
            ),
            
            # 交换机管理API
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
            
            # 接口流量API
            (
                r"/api/interfaces/traffic",
                InterfaceTrafficHandler,
                dict(db_manager=self.db_manager),
            ),
            
            # SNMP历史数据API
            (
                r"/api/snmp/history/clear",
                SNMPHistoryClearHandler,
                dict(db_manager=self.db_manager),
            ),
            (
                r"/api/snmp/history/(?P<switch_id>[^/]+)",
                SNMPHistoryQueryHandler,
                dict(db_manager=self.db_manager),
            ),
            
            # 拓扑图管理API
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
            
            # 常驻进程管理API
            (
                r"/api/resident-processes",
                ResidentProcessListHandler,
                dict(resident_process_manager=self.resident_process_manager),
            ),
            (
                r"/api/resident-processes/get",
                ResidentProcessGetHandler,
                dict(resident_process_manager=self.resident_process_manager),
            ),
            (
                r"/api/resident-processes/create",
                ResidentProcessCreateHandler,
                dict(resident_process_manager=self.resident_process_manager),
            ),
            (
                r"/api/resident-processes/batch-create",
                ResidentProcessBatchCreateHandler,
                dict(resident_process_manager=self.resident_process_manager),
            ),
            (
                r"/api/resident-processes/delete",
                ResidentProcessDeleteHandler,
                dict(resident_process_manager=self.resident_process_manager),
            ),
            (
                r"/api/resident-processes/clear",
                ResidentProcessClearHandler,
                dict(resident_process_manager=self.resident_process_manager),
            ),
            
            # Chrome DevTools配置请求处理
            (r"/.well-known/(.*)", WellKnownHandler),
            
            # 静态文件服务（必须放在最后，作为SPA应用的默认处理器）
            (
                r"/(.*)",
                StaticFileHandler,
                {"path": static_path, "default_filename": "index.html"},
            ),
        ]

        # 创建应用配置
        settings: Dict[str, Any] = {
            "debug": False,  # 生产环境关闭调试模式
        }

        # 过滤掉可能的None路由项（如禁用的指标端点）
        filtered_routes = [r for r in routes if r is not None]
        return tornado.web.Application(filtered_routes, **settings)

    def start(self):
        """启动API服务器
        
        Returns:
            tuple: (success, message) 启动结果和消息
        """
        # 创建HTTPServer实例
        self.server = tornado.httpserver.HTTPServer(
            self.app,
            xheaders=True,  # 启用X-Real-IP等代理头
            max_buffer_size=10485760,  # 10MB缓冲区大小
        )

        try:
            # 根据操作系统决定socket选项
            import platform
            is_windows = platform.system() == "Windows"

            # 绑定套接字，Windows不支持reuse_port选项
            sockets = tornado.netutil.bind_sockets(
                self.port,
                address=self.host,
                reuse_port=not is_windows,  # Windows不支持reuse_port
            )
            self.server.add_sockets(sockets)

            # 设置StateManager的IOLoop引用，用于WebSocket广播
            from src.core.state_manager import state_manager
            state_manager.set_main_ioloop(tornado.ioloop.IOLoop.current())
            
            # 初始化SNMP历史数据清理
            try:
                # 立即执行一次清理
                self.db_manager.snmp_history_manager.purge_older_than_days(
                    SNMP_HISTORY_RETENTION_DAYS
                )
            except Exception:
                logger.debug("无法执行SNMP历史数据清理")
            
            # 设置定时清理任务
            try:
                interval_ms = int(SNMP_HISTORY_PURGE_INTERVAL_MIN) * 60 * 1000
                def _purge():
                    try:
                        self.db_manager.snmp_history_manager.purge_older_than_days(
                            SNMP_HISTORY_RETENTION_DAYS
                        )
                    except Exception:
                        pass
                
                import tornado.ioloop as _ioloop
                self._history_purge_callback = _ioloop.PeriodicCallback(_purge, interval_ms)
                self._history_purge_callback.start()
            except Exception:
                logger.debug("无法设置SNMP历史数据定时清理任务")
        except OSError as e:
            logger.error(f"无法绑定到端口 {self.host}: {str(e)}")
            return False, f"无法绑定到端口 {self.host}: {str(e)}"

        logger.info(f"API服务端启动，监听端口 {self.port}")
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        """停止API服务器"""
        # 停止HTTP服务器
        if self.server:
            self.server.stop()
        
        # 停止IOLoop
        tornado.ioloop.IOLoop.current().stop()
        
        logger.info("API服务端已停止")


if __name__ == "__main__":
    # 使用配置文件中的端口启动API服务器
    api_server = APIServer()
    api_server.start()
