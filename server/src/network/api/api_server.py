#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于Tornado的RESTful API服务
提供系统信息查询接口
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver

from src.core.config import API_PORT
from src.core.logger import logger
from src.database.database_manager import DatabaseManager

# 导入拆分后的handlers
from src.network.api.handlers.main_handler import MainHandler
from src.network.api.handlers.systems_handler import SystemsHandler
from src.network.api.handlers.system_handler import SystemHandler
from src.network.api.handlers.system_type_handler import SystemTypeHandler
from src.network.api.handlers.device_handlers import (DeviceCreateHandler, DeviceUpdateHandler, DeviceDeleteHandler)
from src.network.api.handlers.health_handler import HealthHandler

class APIServer:
    """API服务器类"""
    def __init__(self, db_manager=None, port=API_PORT):
        self.port = port
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
            (r"/api/systems", SystemsHandler, dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server)),
            (r"/api/systems/([^/]+)/type", SystemTypeHandler, dict(db_manager=self.db_manager)),
            (r"/api/systems/([^/]+)", SystemHandler, dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server)),
            (r"/api/devices/create", DeviceCreateHandler, dict(db_manager=self.db_manager)),
            (r"/api/devices/update", DeviceUpdateHandler, dict(db_manager=self.db_manager)),
            (r"/api/devices/delete", DeviceDeleteHandler, dict(db_manager=self.db_manager)),
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
        self.server.listen(self.port)
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