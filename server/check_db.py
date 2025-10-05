#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import os

# 获取数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "net_manager_server.db")

def check_database():
    """检查数据库中的system_info表内容"""
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询所有系统信息
        cursor.execute('SELECT mac_address, hostname, ip_address, gateway, netmask, services, processes, client_id, timestamp FROM system_info')
        rows = cursor.fetchall()
        
        print(f"数据库中有 {len(rows)} 条记录:")
        print("-" * 50)
        
        for row in rows:
            mac_address, hostname, ip_address, gateway, netmask, services, processes, client_id, timestamp = row
            print(f"MAC地址: {mac_address}")
            print(f"主机名: {hostname}")
            print(f"IP地址: {ip_address}")
            print(f"网关: {gateway}")
            print(f"子网掩码: {netmask}")
            print(f"服务数量: {len(json.loads(services))}")
            print(f"进程数量: {len(json.loads(processes))}")
            print(f"客户端ID: {client_id}")
            print(f"时间戳: {timestamp}")
            print("-" * 50)
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_database()