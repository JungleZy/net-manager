#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.tcp_client import TCPClient

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def test_service_discovery():
    """测试服务发现功能"""
    print("1. 测试服务发现...")
    
    # 创建TCP客户端实例
    client = TCPClient()
    
    # 尝试发现服务端
    server_info = client.discover_server()
    
    if server_info:
        print(f"   ✓ 服务发现成功: {server_info[0]}:{server_info[1]}")
        return True
    else:
        print("   ✗ 服务发现失败")
        return False

def test_connection():
    """测试连接功能"""
    print("2. 测试连接功能...")
    
    # 创建TCP客户端实例
    client = TCPClient()
    
    # 尝试连接到服务端
    if client.connect():
        print("   ✓ 连接成功")
        # 断开连接
        client.disconnect()
        return True
    else:
        print("   ✗ 连接失败")
        return False

def main():
    """主函数"""
    print("开始测试TCP连接功能...")
    
    # 设置日志
    setup_logging()
    
    # 测试服务发现
    discovery_success = test_service_discovery()
    
    # 如果服务发现成功，测试连接
    if discovery_success:
        connection_success = test_connection()
        if connection_success:
            print("\n所有测试通过!")
            return 0
        else:
            print("\n连接测试失败!")
            return 1
    else:
        print("\n服务发现测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())