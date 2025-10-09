#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
持续监控脚本
定期获取设备的SNMP数据并显示
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from src.snmp.manager import SNMPManager

# SNMP配置数组
snmp_configs = [
    {
        'ip': '192.168.43.195',      # 设备IP地址
        'snmp_version': 'v3',        # SNMP版本
        'user': 'wjkjv3user',        # SNMP用户名
        'auth_key': 'Wjkj6912',      # 认证密钥
        'auth_protocol': 'sha'       # 认证协议 ('md5' 或 'sha')
    },
    {
        'ip': '192.168.43.195',      # 设备IP地址
        'snmp_version': 'v3',        # SNMP版本
        'user': 'wjkjv3user',        # SNMP用户名
    },
    {
        'ip': '192.168.43.194',      # 设备IP地址
        'snmp_version': 'v2c',       # SNMP版本
        'community': 'wjkjv3user'    # SNMPv2c团体名
    }
]

# 监控间隔（秒）
MONITOR_INTERVAL = 10

async def monitor_device(manager, config):
    """监控设备"""
    ip = config['ip']
    version = config['snmp_version']
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控设备 {ip}...")
    
    try:
        # 根据SNMP版本准备参数
        if version == 'v3':
            # SNMPv3参数
            user = config['user']
            auth_key = config['auth_key']
            auth_protocol = config.get('auth_protocol', 'md5')
            
            # 获取设备概览信息
            device_info = await manager.get_device_overview(
                ip, version,
                user=user,
                auth_key=auth_key,
                auth_protocol=auth_protocol
            )
        else:
            # SNMPv1/v2c参数
            community = config.get('community', 'public')
            
            # 获取设备概览信息
            device_info = await manager.get_device_overview(
                ip, version,
                community=community
            )
        if device_info.get('error'):
            print(f"  错误: {device_info['error']}")
        else:
            print(f"  设备类型: {device_info.get('device_type', 'N/A')}")
            print(f"  设备名称: {device_info.get('name', 'N/A')}")
            print(f"  设备位置: {device_info.get('location', 'N/A')}")
            print(f"  运行时长: {device_info.get('uptime', 'N/A')}")
            print(f"  设备描述: {device_info.get('description', 'N/A')}")
            
        # # 获取CPU使用率
        # cpu_info = await manager.get_cpu_usage(
        #     ip, version,
        #     user=user,
        #     auth_key=auth_key,
        #     auth_protocol=auth_protocol
        # )
        
        # if cpu_info.get('usage') is not None:
        #     print(f"  CPU使用率: {cpu_info['usage']:.2f}%")
        
        # # 获取内存使用情况
        # memory_info = await manager.get_memory_usage(
        #     ip, version,
        #     user=user,
        #     auth_key=auth_key,
        #     auth_protocol=auth_protocol
        # )
        
        # if memory_info.get('usage') is not None:
        #     print(f"  内存使用率: {memory_info['usage']:.2f}%")
        
        # # 获取接口统计信息
        # interface_stats = await manager.get_interface_statistics(
        #     ip, version,
        #     user=user,
        #     auth_key=auth_key,
        #     auth_protocol=auth_protocol
        # )
        
        # print(f"  接口数量: {len(interface_stats)}")
        
        # # 显示前5个接口的流量信息
        # print("  前5个接口流量信息:")
        # for i, stat in enumerate(interface_stats[:5]):
        #     desc = stat.get('description', 'N/A')
        #     in_octets = stat.get('in_octets', 0)
        #     out_octets = stat.get('out_octets', 0)
        #     print(f"    {desc}: 入流量={in_octets}, 出流量={out_octets}")
            
    except Exception as e:
        print(f"  监控设备时出错: {e}")

async def continuous_monitor():
    """持续监控主函数"""
    print("SNMP持续监控启动...")
    print(f"监控间隔: {MONITOR_INTERVAL}秒")
    print("按Ctrl+C停止监控")
    print("-" * 50)
    
    # 创建SNMP管理器
    manager = SNMPManager()
    print("SNMP管理器创建成功")
    try:
        while True:
            # 遍历所有设备配置并执行监控
            for config in snmp_configs:
                await monitor_device(manager, config)
                print("-" * 50)
            
            # 等待下次监控
            await asyncio.sleep(MONITOR_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    asyncio.run(continuous_monitor())