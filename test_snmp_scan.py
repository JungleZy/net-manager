#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试SNMP设备扫描性能的脚本
验证分批并发处理是否生效
"""

import asyncio
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from src.snmp.manager import SNMPManager

async def test_snmp_scan_performance():
    """测试SNMP扫描性能"""
    print("开始测试SNMP设备扫描性能...")
    
    # 创建SNMP管理器
    manager = SNMPManager()
    
    # 使用一个较小的网络范围进行测试
    network = "192.168.1.0/24"
    version = "v2c"
    community = "public"
    
    print(f"扫描网络: {network}")
    print(f"SNMP版本: {version}")
    print(f"Community: {community}")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 执行设备扫描
        devices = await manager.scan_network_devices(network, version, community)
        
        # 记录结束时间
        end_time = time.time()
        
        print(f"\n扫描完成!")
        print(f"发现设备数量: {len(devices)}")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
        if devices:
            print("发现的设备:")
            for device in devices:
                print(f"  - {device}")
        else:
            print("未发现设备")
            
    except Exception as e:
        print(f"扫描过程中出现错误: {e}")
        end_time = time.time()
        print(f"耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(test_snmp_scan_performance())