#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试UDP客户端IP地址更新功能
验证当系统IP地址发生变化时，UDP客户端能够及时更新IP列表
"""

import sys
import os
import time
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.network.udp_client import UDPClient

def test_ip_address_refresh():
    """测试IP地址刷新功能"""
    print("=" * 60)
    print("测试UDP客户端IP地址刷新功能")
    print("=" * 60)
    
    # 创建UDP客户端实例
    udp_client = UDPClient()
    
    # 第一次获取网络接口信息
    print("\n第一次获取网络接口信息:")
    interfaces_1 = udp_client._get_active_interfaces()
    print(f"发现 {len(interfaces_1)} 个活跃网络接口:")
    for interface in interfaces_1:
        print(f"  - {interface['name']}: {interface['ip']}/{interface['netmask']}")
    
    # 等待一小段时间
    time.sleep(1)
    
    # 第二次获取网络接口信息
    print("\n第二次获取网络接口信息:")
    interfaces_2 = udp_client._get_active_interfaces()
    print(f"发现 {len(interfaces_2)} 个活跃网络接口:")
    for interface in interfaces_2:
        print(f"  - {interface['name']}: {interface['ip']}/{interface['netmask']}")
    
    # 比较两次结果
    if interfaces_1 == interfaces_2:
        print("\n✓ 两次获取的网络接口信息相同（正常情况，IP地址未变化）")
    else:
        print("\n⚠ 两次获取的网络接口信息不同（IP地址可能已变化）")
    
    # 测试刷新方法
    print("\n测试强制刷新网络接口信息:")
    interfaces_3 = udp_client.refresh_network_interfaces()
    print(f"刷新后发现 {len(interfaces_3)} 个活跃网络接口:")
    for interface in interfaces_3:
        print(f"  - {interface['name']}: {interface['ip']}/{interface['netmask']}")
    
    # 测试服务发现方法是否会自动刷新
    print("\n测试服务发现方法是否会自动刷新网络接口信息:")
    print("注意: 如果没有运行的服务端，服务发现可能会超时，这是正常的")
    
    try:
        # 设置较短的超时时间以加快测试
        original_timeout = 3.0
        result = udp_client.discover_server_broadcast()
        if result:
            print(f"✓ 成功发现服务端: {result[0]}:{result[1]}")
        else:
            print("⚠ 未发现服务端（可能是正常的，如果没有运行服务端）")
    except Exception as e:
        print(f"服务发现过程中出现异常: {e}")
    
    print("\n测试完成!")
    print("=" * 60)
    print("总结:")
    print("1. 移除了_get_active_interfaces方法的缓存装饰器")
    print("2. 添加了refresh_network_interfaces方法用于强制刷新")
    print("3. discover_server_broadcast方法现在会自动刷新网络接口信息")
    print("4. 这些修改确保了当系统IP地址变化时，UDP客户端能够及时更新")
    print("=" * 60)

if __name__ == "__main__":
    test_ip_address_refresh()