#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于Tornado的RESTful API服务
提供系统信息查询接口
"""

import json
import sqlite3
from pathlib import Path
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.web import RequestHandler
from tornado.escape import json_decode, json_encode

from src.config import TCP_PORT, API_PORT
from src.logger import logger


class DatabaseManager:
    """数据库管理器 - 用于API查询"""
    def __init__(self, db_path="net_manager_server.db"):
        self.db_path = Path(db_path)
    
    def get_all_system_info(self):
        """获取所有系统信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mac_address, hostname, ip_address, services, processes, timestamp
                FROM system_info
                ORDER BY timestamp DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append({
                    'mac_address': row[0],
                    'hostname': row[1],
                    'ip_address': row[2],
                    'services': json.loads(row[3]) if row[3] else [],
                    'processes': json.loads(row[4]) if row[4] else [],
                    'timestamp': row[5]
                })
            
            return result
        except Exception as e:
            logger.error(f"查询所有系统信息失败: {e}")
            raise
    
    def get_system_info_by_mac(self, mac_address):
        """根据MAC地址获取系统信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mac_address, hostname, ip_address, services, processes, timestamp
                FROM system_info
                WHERE mac_address = ?
            ''', (mac_address,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'mac_address': row[0],
                    'hostname': row[1],
                    'ip_address': row[2],
                    'services': json.loads(row[3]) if row[3] else [],
                    'processes': json.loads(row[4]) if row[4] else [],
                    'timestamp': row[5]
                }
            return None
        except Exception as e:
            logger.error(f"根据MAC地址查询系统信息失败: {e}")
            raise


class MainHandler(RequestHandler):
    """主页处理器"""
    def get(self):
        self.write({
            "message": "Net Manager API Server",
            "version": "1.0.0",
            "endpoints": {
                "GET /api/systems": "获取所有系统信息",
                "GET /api/systems/{mac_address}": "根据MAC地址获取特定系统信息",
                "GET /health": "健康检查"
            }
        })


class SystemsHandler(RequestHandler):
    """系统信息处理器 - 获取所有系统信息"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def get(self):
        try:
            systems = self.db_manager.get_all_system_info()
            self.write({
                "status": "success",
                "data": systems,
                "count": len(systems)
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })


class SystemHandler(RequestHandler):
    """单个系统信息处理器 - 根据MAC地址获取系统信息"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def get(self, mac_address):
        try:
            system = self.db_manager.get_system_info_by_mac(mac_address)
            if system:
                self.write({
                    "status": "success",
                    "data": system
                })
            else:
                self.set_status(404)
                self.write({
                    "status": "error",
                    "message": f"未找到MAC地址为 {mac_address} 的系统信息"
                })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })


class HealthHandler(RequestHandler):
    """健康检查处理器"""
    def get(self):
        self.write({
            "status": "healthy",
            "service": "Net Manager API Server"
        })


class APIServer:
    """API服务器类"""
    def __init__(self, port=None, db_path="net_manager_server.db"):
        self.port = port if port is not None else API_PORT
        self.db_manager = DatabaseManager(db_path)
        self.app = self.make_app()
        
    def make_app(self):
        """创建Tornado应用"""
        return tornado.web.Application([
            (r"/", MainHandler),
            (r"/api/systems", SystemsHandler, dict(db_manager=self.db_manager)),
            (r"/api/systems/([^/]+)", SystemHandler, dict(db_manager=self.db_manager)),
            (r"/health", HealthHandler),
            (r"/healthz", HealthHandler),  # Kubernetes健康检查标准端点
        ], debug=False)
    
    def start(self):
        """启动API服务器"""
        server = tornado.httpserver.HTTPServer(self.app)
        server.listen(self.port)
        logger.info(f"API服务端启动，监听端口 {self.port}")
        tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    # 使用配置文件中的端口启动API服务器
    api_server = APIServer()
    api_server.start()