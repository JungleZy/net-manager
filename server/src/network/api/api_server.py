#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于Tornado的RESTful API服务
提供系统信息查询接口
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver

from src.core.config import API_PORT, API_HOST
from src.core.logger import logger
from src.database import DatabaseManager

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
from src.network.api.handlers.health_handler import HealthHandler

class APIServer:
    """API服务器类"""
    def __init__(self, db_manager=None, port=API_PORT, host=API_HOST):
        self.port = port
        self.host = host
        # 如果传入了数据库管理器实例，则使用它；否则创建新的实例
        self.db_manager = db_manager if db_manager else DatabaseManager()
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
        return tornado.web.Application([
            (r"/", MainHandler),
            (r"/api/devices", DevicesHandler, dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server)),
            (r"/api/devices/([^/]+)/type", DeviceTypeHandler, dict(db_manager=self.db_manager)),
            (r"/api/devices/create", DeviceCreateHandler, dict(db_manager=self.db_manager)),
            (r"/api/devices/update", DeviceUpdateHandler, dict(db_manager=self.db_manager)),
            (r"/api/devices/delete", DeviceDeleteHandler, dict(db_manager=self.db_manager)),
            (r"/api/devices/([^/]+)", DeviceHandler, dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server)),
            (r"/api/switches", SwitchesHandler, dict(db_manager=self.db_manager)),
            (r"/api/switches/create", SwitchCreateHandler, dict(db_manager=self.db_manager)),
            (r"/api/switches/update", SwitchUpdateHandler, dict(db_manager=self.db_manager)),
            (r"/api/switches/delete", SwitchDeleteHandler, dict(db_manager=self.db_manager)),
            (r"/api/switches/scan", SNMPScanHandler, dict(db_manager=self.db_manager)),
            (r"/api/switches/scan/simple", SNMPScanHandlerSimple, dict(db_manager=self.db_manager)),
            (r"/api/switches/([^/]+)", SwitchHandler, dict(db_manager=self.db_manager)),
            (r"/health", HealthHandler),
            (r"/healthz", HealthHandler),  # Kubernetes健康检查标准端点
        ], debug=False)
    
    def start(self):
        """启动API服务器"""
        self.server = tornado.httpserver.HTTPServer(
            self.app,
            xheaders= True,
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