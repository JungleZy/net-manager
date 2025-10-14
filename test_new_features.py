#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统信息收集器的新功能
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
sys.path.insert(0, str(project_dir / "client"))

from src.system.system_collector import SystemCollector

def test_new_features():
    """测试新添加的系统信息收集功能"""
    print("测试新添加的系统信息收集功能...")
    
    # 创建SystemCollector实例
    collector = SystemCollector()
    
    # 1. 测试网络接口信息收集
    print("\n1. 测试网络接口信息收集:")
    network_interfaces = collector.get_network_interfaces()
    print(f"   网络接口数量: {len(network_interfaces)}")
    for interface in network_interfaces:  # 打印全部接口
        print(f"   接口名称: {interface.get('name', 'N/A')}")
        print(f"   IP地址: {interface.get('ip_address', 'N/A')}")
        print(f"   MAC地址: {interface.get('mac_address', 'N/A')}")
        print(f"   网关: {interface.get('gateway', 'N/A')}")
        print(f"   子网掩码: {interface.get('netmask', 'N/A')}")
        print(f"   上传速率: {interface.get('upload_rate', 0)} bytes/sec")
        print(f"   下载速率: {interface.get('download_rate', 0)} bytes/sec")
        print("   ---")
    
    # 2. 测试CPU信息收集
    print("\n2. 测试CPU信息收集:")
    cpu_info = collector.get_cpu_info()
    print(f"   物理核心数: {cpu_info.get('physical_cores', 'N/A')}")
    print(f"   逻辑核心数: {cpu_info.get('logical_cores', 'N/A')}")
    print(f"   最大频率: {cpu_info.get('max_frequency', 'N/A')} MHz")
    print(f"   当前频率: {cpu_info.get('current_frequency', 'N/A')} MHz")
    print(f"   使用率: {cpu_info.get('usage_percent', 'N/A')}%")
    
    # 3. 测试内存信息收集
    print("\n3. 测试内存信息收集:")
    memory_info = collector.get_memory_info()
    print(f"   总内存: {memory_info.get('total', 'N/A')} bytes")
    print(f"   可用内存: {memory_info.get('available', 'N/A')} bytes")
    print(f"   已使用内存: {memory_info.get('used', 'N/A')} bytes")
    print(f"   内存使用率: {memory_info.get('percentage', 'N/A')}%")
    print(f"   交换空间总量: {memory_info.get('swap_total', 'N/A')} bytes")
    print(f"   交换空间已使用: {memory_info.get('swap_used', 'N/A')} bytes")
    print(f"   交换空间使用率: {memory_info.get('swap_percentage', 'N/A')}%")
    
    # 4. 测试磁盘信息收集
    print("\n4. 测试磁盘信息收集:")
    disk_info = collector.get_disk_info()
    print(f"   磁盘总空间: {disk_info.get('total', 'N/A')} bytes")
    print(f"   磁盘已使用空间: {disk_info.get('used', 'N/A')} bytes")
    print(f"   磁盘可用空间: {disk_info.get('free', 'N/A')} bytes")
    print(f"   磁盘使用率: {disk_info.get('percentage', 'N/A')}%")
    
    # 5. 测试完整的系统信息收集
    print("\n5. 测试完整的系统信息收集:")
    system_info = collector.collect_system_info()
    print(f"   网络接口数量: {len(system_info.network_interfaces)}")
    print(f"   CPU信息字段数: {len(system_info.cpu_info)}")
    print(f"   内存信息字段数: {len(system_info.memory_info)}")
    print(f"   磁盘信息字段数: {len(system_info.disk_info)}")
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    test_new_features()