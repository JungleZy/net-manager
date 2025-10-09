#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单个系统信息处理器
"""

import sqlite3
from .base_handler import BaseHandler

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