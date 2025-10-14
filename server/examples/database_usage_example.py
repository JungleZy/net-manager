#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库管理器使用示例
展示如何使用重构后的数据库管理器模块
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager
from src.models.devices_info import DevicesInfo
from src.models.switch_info import SwitchInfo


def example_device_management():
    """设备管理示例"""
    print("=== 设备管理示例 ===")
    
    # 创建数据库管理器实例
    db_manager = DatabaseManager("example.db")
    
    # 创建系统信息对象
    devices_info = DevicesInfo(
        hostname="example-host",
        ip_address="192.168.1.100",
        mac_address="00:11:22:33:44:55",
        gateway="192.168.1.1",
        netmask="255.255.255.0",
        services=json.dumps(["ssh", "http"]),
        processes=json.dumps(["nginx", "mysql"]),
        timestamp=datetime.now().isoformat(),
        os_name="Ubuntu 20.04",
        os_version="20.04",
        os_architecture="x86_64",
        machine_type="PC",
        type="computer"
    )
    
    # 保存系统信息
    try:
        db_manager.save_devices_info(devices_info)
        print("✓ 设备信息保存成功")
    except Exception as e:
        print(f"✗ 系统信息保存失败: {e}")
        return
    
    # 查询所有系统信息
    try:
        all_system_info = db_manager.get_all_system_info()
        print(f"✓ 查询到 {len(all_system_info)} 条系统信息")
        for info in all_system_info:
            print(f"  主机名: {info['hostname']}, IP: {info['ip_address']}")
    except Exception as e:
        print(f"✗ 查询系统信息失败: {e}")
    
    # 根据MAC地址查询系统信息
    try:
        info = db_manager.get_system_info_by_mac("00:11:22:33:44:55")
        if info:
            print(f"✓ 找到设备: {info['hostname']}")
        else:
            print("✗ 未找到指定设备")
    except Exception as e:
        print(f"✗ 查询设备失败: {e}")


def example_switch_management():
    """交换机管理示例"""
    print("\n=== 交换机管理示例 ===")
    
    # 创建数据库管理器实例
    db_manager = DatabaseManager("example.db")
    
    # 创建交换机信息对象
    switch_info = SwitchInfo(
        ip="192.168.1.200",
        snmp_version="2c",
        community="public",
        user="admin",
        auth_key="password123"
    )
    
    # 添加交换机
    try:
        success, message = db_manager.add_switch(switch_info)
        if success:
            print("✓ 交换机添加成功")
        else:
            print(f"✗ 交换机添加失败: {message}")
    except Exception as e:
        print(f"✗ 交换机添加异常: {e}")
        return
    
    # 查询所有交换机
    try:
        all_switches = db_manager.get_all_switches()
        print(f"✓ 查询到 {len(all_switches)} 台交换机")
        for switch in all_switches:
            print(f"  IP: {switch['ip']}, SNMP版本: {switch['snmp_version']}")
    except Exception as e:
        print(f"✗ 查询交换机失败: {e}")
    
    # 根据IP地址查询交换机
    try:
        switch = db_manager.get_switch_by_ip("192.168.1.200")
        if switch:
            print(f"✓ 找到交换机: {switch['ip']}")
        else:
            print("✗ 未找到指定交换机")
    except Exception as e:
        print(f"✗ 查询交换机失败: {e}")


def main():
    """主函数"""
    print("数据库管理器使用示例")
    print("=" * 30)
    
    # 检查数据库健康状态
    db_manager = DatabaseManager("example.db")
    if db_manager.health_check():
        print("✓ 数据库连接正常")
    else:
        print("✗ 数据库连接异常")
        return
    
    # 运行示例
    example_device_management()
    example_switch_management()
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    main()