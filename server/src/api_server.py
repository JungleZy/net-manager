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
                SELECT mac_address, hostname, ip_address, gateway, netmask, services, processes, timestamp
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
                    'gateway': row[3],
                    'netmask': row[4],
                    'services': json.loads(row[5]) if row[5] else [],
                    'processes': json.loads(row[6]) if row[6] else [],
                    'timestamp': row[7]
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
                SELECT mac_address, hostname, ip_address, gateway, netmask, services, processes, timestamp
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
                    'gateway': row[3],
                    'netmask': row[4],
                    'services': json.loads(row[5]) if row[5] else [],
                    'processes': json.loads(row[6]) if row[6] else [],
                    'timestamp': row[7]
                }
            return None
        except Exception as e:
            logger.error(f"根据MAC地址查询系统信息失败: {e}")
            raise


class BaseHandler(RequestHandler):
    """基础处理器类，提供通用功能如CORS支持"""
    def set_default_headers(self):
        """设置默认响应头，支持CORS"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type")
        self.set_header("Access-Control-Max-Age", "86400")  # 24小时
    
    def options(self):
        """处理OPTIONS预检请求"""
        self.set_status(204)
        self.finish()

class MainHandler(BaseHandler):
    """主页处理器 - 返回简单的欢迎信息"""
    def get(self):
        self.write({
            "message": "欢迎使用Net Manager API服务",
            "version": "1.0.0",
            "documentation": "/api/docs"
        })


class SystemsHandler(BaseHandler):
    """系统信息处理器 - 获取所有系统信息"""
    def initialize(self, db_manager, get_tcp_server_func=None):
        self.db_manager = db_manager
        self.get_tcp_server_func = get_tcp_server_func
    
    def get_online_status(self, mac_address):
        """根据MAC地址判断客户端是否在线"""
        if not self.get_tcp_server_func:
            return False
            
        tcp_server = self.get_tcp_server_func()
        if not tcp_server:
            return False
        
        # 遍历所有连接的客户端，检查是否有匹配的MAC地址
        with tcp_server.clients_lock:
            for client_socket, address in tcp_server.clients:
                # 这里需要从数据库或客户端信息中获取MAC地址
                # 简化实现：假设address包含IP信息，需要从数据库查找对应MAC
                try:
                    conn = sqlite3.connect(self.db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT mac_address FROM system_info WHERE ip_address = ?
                    ''', (address[0],))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row and row[0] == mac_address:
                        return True
                except Exception:
                    pass
        return False
    
    def get(self):
        try:
            systems = self.db_manager.get_all_system_info()
            
            # 处理返回数据：只返回services和processes的数量，并添加在线状态
            processed_systems = []
            for system in systems:
                processed_system = {
                    'mac_address': system['mac_address'],
                    'hostname': system['hostname'],
                    'ip_address': system['ip_address'],
                    'gateway': system['gateway'],
                    'netmask': system['netmask'],
                    'services_count': len(system['services']),
                    'processes_count': len(system['processes']),
                    'online': self.get_online_status(system['mac_address']),
                    'timestamp': system['timestamp']
                }
                processed_systems.append(processed_system)
            
            self.write({
                "status": "success",
                "data": processed_systems,
                "count": len(processed_systems)
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })


class SystemHandler(BaseHandler):
    """单个系统信息处理器 - 根据MAC地址获取系统信息"""
    def initialize(self, db_manager, get_tcp_server_func=None):
        self.db_manager = db_manager
        self.get_tcp_server_func = get_tcp_server_func
    
    def get_online_status(self, mac_address):
        """根据MAC地址判断客户端是否在线"""
        if not self.get_tcp_server_func:
            return False
            
        tcp_server = self.get_tcp_server_func()
        if not tcp_server:
            return False
        
        # 遍历所有连接的客户端，检查是否有匹配的MAC地址
        with tcp_server.clients_lock:
            for client_socket, address in tcp_server.clients:
                # 这里需要从数据库或客户端信息中获取MAC地址
                # 简化实现：假设address包含IP信息，需要从数据库查找对应MAC
                try:
                    conn = sqlite3.connect(self.db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT mac_address FROM system_info WHERE ip_address = ?
                    ''', (address[0],))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row and row[0] == mac_address:
                        return True
                except Exception:
                    pass
        return False
    
    def get(self, mac_address):
        try:
            system = self.db_manager.get_system_info_by_mac(mac_address)
            if system:
                # 添加在线状态字段
                system['online'] = self.get_online_status(mac_address)
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


class HealthHandler(BaseHandler):
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
            (r"/api/systems/([^/]+)", SystemHandler, dict(db_manager=self.db_manager, get_tcp_server_func=self.get_tcp_server)),
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