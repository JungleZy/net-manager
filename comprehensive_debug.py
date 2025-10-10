#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合调试脚本：测试不同的SNMP配置和扫描方法
"""

import sys
import os
import asyncio
import subprocess
import socket

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'src'))

from src.snmp.manager import SNMPManager

async def test_snmp_configurations():
    """测试不同的SNMP配置"""
    print("测试不同的SNMP配置...")
    
    # 创建SNMP管理器实例
    snmp_manager = SNMPManager()
    
    # 要测试的具体IP地址
    test_ips = ["192.168.43.194", "192.168.43.195"]
    
    # 不同的SNMP配置
    snmp_configs = [
        {"version": "v2c", "community": "public"},
        {"version": "v2c", "community": "private"},
        {"version": "v1", "community": "public"},
        {"version": "v1", "community": "private"},
    ]
    
    # 从测试文件中获取可能的配置
    try:
        # 尝试读取可能的配置文件
        possible_configs = [
            {"version": "v2c", "community": "wjkjv2user"},
            {"version": "v3", "user": "wjkjv3user", "auth_key": "Wjkj6912"}
        ]
        snmp_configs.extend(possible_configs)
    except:
        pass
    
    for ip in test_ips:
        print(f"\n测试设备 {ip}:")
        
        # 1. 测试基本连通性
        print("  1. 测试基本连通性...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, 161))  # SNMP端口
            if result == 0:
                print(f"    ✓ SNMP端口(161)开放")
            else:
                print(f"    ✗ SNMP端口(161)关闭")
            sock.close()
        except Exception as e:
            print(f"    ✗ 端口测试出错: {e}")
        
        # 2. 测试不同的SNMP配置
        print("  2. 测试不同的SNMP配置...")
        for i, config in enumerate(snmp_configs, 1):
            version = config["version"]
            try:
                print(f"    配置 {i}: {version}", end="")
                if "community" in config:
                    print(f" (community={config['community']})")
                elif "user" in config:
                    print(f" (user={config['user']})")
                else:
                    print()
                
                if version == "v3":
                    # SNMP v3测试
                    if "user" in config and "auth_key" in config:
                        try:
                            result = await snmp_manager.snmp_scan_device(
                                ip, version, 
                                user=config["user"], 
                                auth_key=config["auth_key"]
                            )
                            if result:
                                print(f"      ✓ SNMP v3访问成功")
                            else:
                                print(f"      ✗ SNMP v3访问失败")
                        except Exception as e:
                            print(f"      ✗ SNMP v3访问出错: {e}")
                    else:
                        print(f"      ✗ SNMP v3配置不完整")
                else:
                    # SNMP v1/v2c测试
                    community = config.get("community", "public")
                    try:
                        result = await snmp_manager.snmp_scan_device(ip, version, community)
                        if result:
                            print(f"      ✓ SNMP {version}访问成功 (community={community})")
                        else:
                            print(f"      ✗ SNMP {version}访问失败 (community={community})")
                    except Exception as e:
                        print(f"      ✗ SNMP {version}访问出错 (community={community}): {e}")
            except Exception as e:
                print(f"      ✗ 配置测试出错: {e}")

async def improved_network_scan():
    """改进的网络扫描方法"""
    print("\n使用改进的网络扫描方法...")
    
    # 创建SNMP管理器实例
    snmp_manager = SNMPManager()
    
    # 直接扫描特定IP范围，不依赖ARP发现
    target_network = "192.168.43.192/28"  # 包含目标IP的小范围
    print(f"扫描网络段: {target_network}")
    
    # 手动生成IP列表
    import ipaddress
    network = ipaddress.IPv4Network(target_network)
    ip_list = [str(ip) for ip in network.hosts()]
    
    print(f"生成IP列表: {ip_list}")
    
    # 对每个IP进行SNMP扫描
    snmp_devices = []
    for ip in ip_list:
        try:
            print(f"扫描设备 {ip}...")
            # 使用不同的community字符串尝试
            communities = ["public", "private", "wjkjv2user"]
            found = False
            
            for community in communities:
                try:
                    result = await snmp_manager.snmp_scan_device(ip, "v2c", community)
                    if result:
                        snmp_devices.append(result)
                        print(f"  ✓ 发现SNMP设备: {result} (community={community})")
                        found = True
                        break  # 找到后就停止尝试其他community
                except Exception as e:
                    continue  # 继续尝试下一个community
                    
            if not found:
                print(f"  ✗ 未发现SNMP设备: {ip}")
        except Exception as e:
            print(f"  ✗ 扫描设备 {ip} 时出错: {e}")
    
    print(f"总共发现 {len(snmp_devices)} 个SNMP设备")
    return snmp_devices

def check_snmp_service():
    """检查本地SNMP服务"""
    print("\n检查本地SNMP服务...")
    
    try:
        # 检查Windows SNMP服务
        result = subprocess.run(["sc", "query", "SNMP"], capture_output=True, text=True, timeout=10)
        if "RUNNING" in result.stdout:
            print("  ✓ 本地SNMP服务正在运行")
        elif "STOPPED" in result.stdout:
            print("  ✗ 本地SNMP服务已停止")
        else:
            print("  ? 未找到本地SNMP服务")
    except Exception as e:
        print(f"  ✗ 检查SNMP服务出错: {e}")

if __name__ == "__main__":
    print("=== 综合网络和SNMP调试 ===")
    
    # 运行测试
    asyncio.run(test_snmp_configurations())
    check_snmp_service()
    
    # 运行改进的扫描
    devices = asyncio.run(improved_network_scan())
    
    print(f"\n=== 调试总结 ===")
    if devices:
        print(f"成功发现 {len(devices)} 个SNMP设备: {devices}")
    else:
        print("未发现任何SNMP设备")
        print("\n可能的原因:")
        print("1. 目标设备未启用SNMP服务")
        print("2. SNMP配置不正确(community字符串、用户名、密码等)")
        print("3. 防火墙阻止了SNMP通信")
        print("4. 设备不在同一网络段")
        print("5. 设备禁用了SNMP响应")