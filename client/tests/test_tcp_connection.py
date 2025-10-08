#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试TCP连接功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.network.tcp_client import TCPClient
from src.system.system_collector import SystemCollector

def test_tcp_connection():
    """测试TCP连接功能"""
    print("开始测试TCP连接功能...")
    
    # 创建TCP客户端
    tcp_client = TCPClient()
    
    # 测试服务发现
    print("1. 测试服务发现...")
    if tcp_client.discover_server():
        print("   ✓ 服务发现成功")
    else:
        print("   ✗ 服务发现失败")
        return
    
    # 测试连接到服务端
    print("2. 测试连接到服务端...")
    if tcp_client.connect_to_server():
        print("   ✓ 连接成功")
    else:
        print("   ✗ 连接失败")
        return
    
    # 测试发送数据
    print("3. 测试发送数据...")
    collector = SystemCollector()
    system_info = collector.collect_system_info()
    
    if tcp_client.send_system_info(system_info):
        print("   ✓ 数据发送成功")
    else:
        print("   ✗ 数据发送失败")
    
    # 保持连接一段时间
    print("4. 保持连接10秒...")
    time.sleep(10)
    
    # 断开连接
    print("5. 断开连接...")
    tcp_client.disconnect()
    print("   ✓ 连接已断开")
    
    print("TCP连接功能测试完成")

if __name__ == "__main__":
    test_tcp_connection()