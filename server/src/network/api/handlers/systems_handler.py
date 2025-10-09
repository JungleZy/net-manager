#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统信息处理器
"""

import sqlite3
from .base_handler import BaseHandler


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