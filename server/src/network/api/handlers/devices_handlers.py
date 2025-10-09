#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备管理处理器
"""

import json
import tornado.escape
import sqlite3
from src.network.api.handlers.base_handler import BaseHandler

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

class DeviceHandler(BaseHandler):
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
                SELECT client_id FROM devices_info WHERE mac_address = ? ORDER BY timestamp DESC LIMIT 1
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

class DeviceTypeHandler(BaseHandler):
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

class DevicesHandler(BaseHandler):
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
                SELECT client_id FROM devices_info WHERE mac_address = ? ORDER BY timestamp DESC LIMIT 1
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
