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

from src.core.config import TCP_PORT, API_PORT
from src.core.logger import logger
from src.database.database_manager import DatabaseManager


class BaseHandler(RequestHandler):
    """基础处理器类，提供通用功能如CORS支持"""
    def set_default_headers(self):
        """设置默认响应头，支持CORS"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type")
        self.set_header("Access-Control-Max-Age", "86400")  # 24小时
    
    def options(self, *args):
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
        """根据client_id判断客户端是否在线"""
        # 首先通过MAC地址获取client_id
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT client_id FROM system_info WHERE mac_address = ? ORDER BY timestamp DESC LIMIT 1
            ''', (mac_address,))
            row = cursor.fetchone()
            conn.close()
            
            if not row or not row[0]:
                return False
                
            client_id = row[0]
        except Exception:
            return False
        
        # 然后通过TCP服务器检查client_id是否在线
        if not self.get_tcp_server_func:
            return False
            
        tcp_server = self.get_tcp_server_func()
        if not tcp_server:
            return False
        
        # 检查client_id是否在在线客户端映射中
        with tcp_server.clients_lock:
            return client_id in tcp_server.client_id_map
    
    def get(self):
        try:
            systems = self.db_manager.get_all_system_info()
            
            # 处理返回数据：只返回services和processes的数量，并添加在线状态和操作系统信息
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
                    'os_name': system['os_name'],
                    'os_version': system['os_version'],
                    'os_architecture': system['os_architecture'],
                    'machine_type': system['machine_type'],
                    'type': system['type'],
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
        """根据client_id判断客户端是否在线"""
        # 首先通过MAC地址获取client_id
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT client_id FROM system_info WHERE mac_address = ? ORDER BY timestamp DESC LIMIT 1
            ''', (mac_address,))
            row = cursor.fetchone()
            conn.close()
            
            if not row or not row[0]:
                return False
                
            client_id = row[0]
        except Exception:
            return False
        
        # 然后通过TCP服务器检查client_id是否在线
        if not self.get_tcp_server_func:
            return False
            
        tcp_server = self.get_tcp_server_func()
        if not tcp_server:
            return False
        
        # 检查client_id是否在在线客户端映射中
        with tcp_server.clients_lock:
            return client_id in tcp_server.client_id_map
    
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

class SystemTypeHandler(BaseHandler):
    """系统类型处理器 - 设置设备类型"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def put(self, mac_address):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            device_type = data.get('type')
            
            # 检查type字段是否存在
            if device_type is None:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": "缺少必需的字段: type"
                })
                return
            
            # 更新数据库中的设备类型
            success = self.db_manager.update_system_type(mac_address, device_type)
            
            if success:
                self.write({
                    "status": "success",
                    "message": "设备类型更新成功"
                })
            else:
                self.set_status(404)
                self.write({
                    "status": "error",
                    "message": f"未找到MAC地址为 {mac_address} 的系统信息"
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })

class DeviceCreateHandler(BaseHandler):
    """设备创建处理器 - 新增设备"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            required_fields = ['mac_address', 'hostname', 'ip_address']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write({
                        "status": "error",
                        "message": f"缺少必需的字段: {field}"
                    })
                    return
            
            # 创建设备
            success, message = self.db_manager.create_device(data)
            
            if success:
                self.write({
                    "status": "success",
                    "message": message
                })
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": message
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })

class DeviceUpdateHandler(BaseHandler):
    """设备更新处理器 - 修改设备"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            required_fields = ['mac_address', 'hostname', 'ip_address']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write({
                        "status": "error",
                        "message": f"缺少必需的字段: {field}"
                    })
                    return
            
            # 更新设备
            success, message = self.db_manager.update_device(data)
            
            if success:
                self.write({
                    "status": "success",
                    "message": message
                })
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": message
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })

class DeviceDeleteHandler(BaseHandler):
    """设备删除处理器 - 删除设备"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            mac_address = data.get('mac_address')
            if not mac_address:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": "缺少必需的字段: mac_address"
                })
                return
            
            # 删除设备
            success, message = self.db_manager.delete_device(mac_address)
            
            if success:
                self.write({
                    "status": "success",
                    "message": message
                })
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": message
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
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