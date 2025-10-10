#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络调试脚本：用于检查网络配置和改进扫描方法
"""

import sys
import os
import asyncio
import socket
import subprocess

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'src'))

from src.snmp.manager import SNMPManager

def get_local_network_info():
    """获取本地网络信息"""
    print("获取本地网络信息...")
    
    try:
        # 获取本机IP地址
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"本机主机名: {hostname}")
        print(f"本机IP地址: {local_ip}")
        
        # 获取网络接口信息
        import psutil
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, interface_addresses in net_if_addrs.items():
            if interface_name in net_if_stats and net_if_stats[interface_name].isup:
                print(f"\n网络接口: {interface_name}")
                for address in interface_addresses:
                    if address.family == socket.AF_INET:
                        print(f"  IP地址: {address.address}")
                        print(f"  子网掩码: {address.netmask}")
                        if address.broadcast:
                            print(f"  广播地址: {address.broadcast}")
                        
                        # 计算网络段
                        if address.netmask:
                            import ipaddress
                            network = ipaddress.IPv4Network(f"{address.address}/{address.netmask}", strict=False)
                            print(f"  网络段: {network}")
    except Exception as e:
        print(f"获取本地网络信息出错: {e}")

def ping_test():
    """测试PING连通性"""
    print("\n测试PING连通性...")
    test_ips = ["192.168.43.194", "192.168.43.195"]
    
    for ip in test_ips:
        try:
            # 使用系统ping命令
            result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"  ✓ {ip} PING成功")
                # 提取延迟信息
                if "平均" in result.stdout:
                    print(f"    延迟信息: {result.stdout.split('平均')[1].split('ms')[0]}ms")
            else:
                print(f"  ✗ {ip} PING失败")
        except Exception as e:
            print(f"  ✗ {ip} PING测试出错: {e}")

async def improved_scan():
    """改进的扫描方法"""
    print("\n使用改进的扫描方法...")
    
    # 创建SNMP管理器实例
    snmp_manager = SNMPManager()
    
    # 直接测试特定IP，不依赖ARP发现
    test_ips = ["192.168.43.194", "192.168.43.195"]
    
    print("直接扫描特定IP地址...")
    snmp_devices = []
    for ip in test_ips:
        try:
            print(f"扫描设备 {ip}...")
            # 增加超时时间并提供更多调试信息
            result = await snmp_manager.snmp_scan_device(ip, "v2c", "public")
            if result:
                snmp_devices.append(result)
                print(f"  ✓ 发现SNMP设备: {result}")
            else:
                print(f"  ✗ 未发现SNMP设备: {ip}")
        except Exception as e:
            print(f"  ✗ 扫描设备 {ip} 时出错: {e}")
    
    print(f"总共发现 {len(snmp_devices)} 个SNMP设备")

def check_network_topology():
    """检查网络拓扑"""
    print("\n检查网络拓扑...")
    
    try:
        # 获取路由表信息
        result = subprocess.run(["route", "print"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("本地路由表:")
            lines = result.stdout.split('\n')
            for line in lines:
                if '192.168.43' in line:
                    print(f"  {line.strip()}")
        else:
            print("无法获取路由表信息")
    except Exception as e:
        print(f"检查网络拓扑出错: {e}")

if __name__ == "__main__":
    get_local_network_info()
    ping_test()
    asyncio.run(improved_scan())
    check_network_topology()