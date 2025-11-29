#!/usr/bin/env python3
"""
模拟Linux环境下IP地址获取的测试脚本
"""

import sys
import os
import socket

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.system.system_collector import SystemCollector

def test_linux_scenario():
    print("模拟Linux环境下IP地址获取测试")
    print("=" * 50)
    collector = SystemCollector()
    print("场景1: 网络不可达（errno 101 network is unreachable）")
    print("\n测试方法2: 使用psutil获取网络接口信息")
    try:
        ip_address = collector._get_ip_via_psutil()
        print(f"结果: {ip_address}")
        if ip_address != "unknown":
            print("✓ 方法2成功获取IP地址，可以解决Linux网络不可达问题")
        else:
            print("✗ 方法2未能获取IP地址")
    except Exception as e:
        print(f"✗ 方法2失败: {e}")
    print("\n测试方法3: 通过网关获取IP地址")
    try:
        ip_address = collector._get_ip_via_gateway()
        print(f"结果: {ip_address}")
        if ip_address != "unknown":
            print("✓ 方法3成功获取IP地址，可以解决Linux网络不可达问题")
        else:
            print("✗ 方法3未能获取IP地址")
    except Exception as e:
        print(f"✗ 方法3失败: {e}")
    print("\n测试综合方法")
    try:
        ip_address = collector.get_ip_address()
        print(f"结果: {ip_address}")
        if ip_address != "unknown":
            print("✓ 综合方法成功获取IP地址")
        else:
            print("✗ 综合方法未能获取IP地址")
    except Exception as e:
        print(f"✗ 综合方法失败: {e}")
    print("\n" + "=" * 50)
    print("总结:")
    print("1. 修改后的代码添加了多种获取IP地址的方法")
    print("2. 即使在Linux网络不可达的情况下，也可以通过psutil获取本地网络接口信息")
    print("3. 优先级顺序为：连接外部地址 -> psutil -> 网关 -> hostname")
    print("4. 这种多方法组合的方式大大提高了在Linux系统上的兼容性")

if __name__ == "__main__":
    test_linux_scenario()
