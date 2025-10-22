#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证TCP和UDP客户端优化代码
检查是否有语法错误和基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)


def validate_tcp_client():
    """验证TCP客户端"""
    print("验证TCP客户端...")
    try:
        from src.network.tcp_client import TCPClient, get_tcp_client

        # 测试初始化
        client = TCPClient()
        print("✓ TCPClient初始化成功")

        # 测试单例模式
        client1 = get_tcp_client()
        client2 = get_tcp_client()
        assert client1 is client2
        print("✓ TCP客户端单例模式正常")

        print("TCP客户端验证通过\n")
        return True
    except Exception as e:
        print(f"✗ TCP客户端验证失败: {e}\n")
        return False


def validate_udp_client():
    """验证UDP客户端"""
    print("验证UDP客户端...")
    try:
        from src.network.udp_client import UDPClient, get_udp_client

        # 测试初始化
        client = UDPClient()
        print("✓ UDPClient初始化成功")

        # 测试单例模式
        client1 = get_udp_client()
        client2 = get_udp_client()
        assert client1 is client2
        print("✓ UDP客户端单例模式正常")

        print("UDP客户端验证通过\n")
        return True
    except Exception as e:
        print(f"✗ UDP客户端验证失败: {e}\n")
        return False


def main():
    """主函数"""
    print("开始验证TCP和UDP客户端优化...\n")

    tcp_ok = validate_tcp_client()
    udp_ok = validate_udp_client()

    if tcp_ok and udp_ok:
        print("所有验证通过！优化代码没有明显问题。")
        return 0
    else:
        print("验证失败，请检查代码。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
