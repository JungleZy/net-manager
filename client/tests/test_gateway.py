#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from system_collector import SystemCollector
import platform

def test_gateway_detection():
    """测试网关检测功能"""
    print(f"操作系统: {platform.system()}")
    
    collector = SystemCollector()
    
    # 测试获取IP地址
    ip = collector.get_ip_address()
    print(f"IP地址: {ip}")
    
    # 测试获取网关和子网掩码
    gateway, netmask = collector.get_gateway_and_netmask()
    print(f"网关: {gateway}")
    print(f"子网掩码: {netmask}")

if __name__ == "__main__":
    test_gateway_detection()