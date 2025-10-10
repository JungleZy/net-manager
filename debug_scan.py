#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试脚本：用于测试特定IP地址的SNMP扫描
"""

import sys
import os
import asyncio

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'src'))

from src.snmp.manager import SNMPManager

async def debug_specific_ips():
    """调试特定IP地址的扫描"""
    print("调试特定IP地址的SNMP扫描...")
    
    # 创建SNMP管理器实例
    snmp_manager = SNMPManager()
    
    # 要测试的具体IP地址
    test_ips = ["192.168.43.194", "192.168.43.195"]
    
    print("1. 直接测试这些IP的SNMP连接...")
    for ip in test_ips:
        print(f"\n测试设备 {ip}:")
        try:
            # 直接扫描单个设备
            result = await snmp_manager.snmp_scan_device(ip, "v2c", "public")
            if result:
                print(f"  ✓ 设备 {ip} 可以通过SNMP访问")
            else:
                print(f"  ✗ 设备 {ip} 无法通过SNMP访问")
        except Exception as e:
            print(f"  ✗ 扫描设备 {ip} 时出错: {e}")
    
    print("\n2. 使用Ping发现测试...")
    # 先测试Ping发现是否能找到这些设备
    try:
        import subprocess
        import platform
        import ipaddress
        
        # 根据平台设置ping命令参数
        system = platform.system().lower()
        if system == "windows":
            ping_cmd = ["ping", "-n", "1", "-w", "1000"]  # Windows: -w is timeout in milliseconds
        else:
            ping_cmd = ["ping", "-c", "1", "-W", "1"]     # Linux/macOS: -W is timeout in seconds
        
        print("正在进行Ping发现...")
        ping_found = []
        for ip in test_ips:
            try:
                cmd = ping_cmd + [str(ip)]
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2
                )
                # 如果返回码为0，表示设备在线
                if result.returncode == 0:
                    ping_found.append(ip)
                    print(f"  Ping发现找到设备: {ip}")
                else:
                    print(f"  Ping发现未找到设备: {ip}")
            except Exception as e:
                print(f"  Ping发现测试 {ip} 出错: {e}")
        
        print(f"Ping发现完成，共找到 {len(ping_found)} 个设备")
    except Exception as e:
        print(f"Ping发现测试出错: {e}")

    print("\n3. 综合扫描测试...")
    # 测试综合扫描
    try:
        network = "192.168.43.192/28"  # 包含目标IP的较小网络段
        print(f"扫描网络段: {network}")
        devices = snmp_manager.snmp_discovery_arp(network)
        print(f"ARP发现找到 {len(devices)} 个设备: {devices}")
        
        if devices:
            # 对发现的设备进行SNMP扫描
            snmp_devices = []
            for ip in devices:
                try:
                    result = await snmp_manager.snmp_scan_device(ip, "v2c", "public")
                    if result:
                        snmp_devices.append(result)
                        print(f"  ✓ SNMP扫描成功: {result}")
                    else:
                        print(f"  ✗ SNMP扫描失败: {ip}")
                except Exception as e:
                    print(f"  ✗ 扫描设备 {ip} 时出错: {e}")
            
            print(f"总共发现 {len(snmp_devices)} 个SNMP设备")
        else:
            print("ARP未发现任何设备")
    except Exception as e:
        print(f"综合扫描测试出错: {e}")

if __name__ == "__main__":
    asyncio.run(debug_specific_ips())