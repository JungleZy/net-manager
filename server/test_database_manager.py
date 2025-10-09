#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据库管理器功能
"""

import sys
import os
import tempfile
import datetime

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.database import DatabaseManager
from src.models.system_info import SystemInfo
from src.models.switch_info import SwitchInfo

def test_database_manager():
    """测试数据库管理器功能"""
    # 创建临时数据库文件
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # 创建数据库管理器实例
        db_manager = DatabaseManager(db_path)
        print("数据库管理器创建成功")
        
        # 测试数据库健康检查
        if db_manager.health_check():
            print("数据库健康检查通过")
        else:
            print("数据库健康检查失败")
            return False
            
        # 测试设备管理功能
        print("\n--- 测试设备管理功能 ---")
        
        # 创建系统信息
        system_info = SystemInfo(
            hostname="test-host",
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:55",
            gateway="192.168.1.1",
            netmask="255.255.255.0",
            services=["ssh", "http"],
            processes=["process1", "process2"],
            client_id="client-001",
            os_name="Ubuntu",
            os_version="20.04",
            os_architecture="x86_64",
            machine_type="PC",
            timestamp=datetime.datetime.now().isoformat()
        )
        
        # 保存系统信息
        db_manager.save_system_info(system_info)
        print("系统信息保存成功")
        
        # 查询系统信息
        retrieved_info = db_manager.get_system_info_by_mac("00:11:22:33:44:55")
        if retrieved_info:
            print("系统信息查询成功")
            print(f"主机名: {retrieved_info['hostname']}")
            print(f"IP地址: {retrieved_info['ip_address']}")
        else:
            print("系统信息查询失败")
            return False
            
        # 测试设备计数
        device_count = db_manager.get_device_count()
        print(f"设备总数: {device_count}")
        
        # 测试交换机管理功能
        print("\n--- 测试交换机管理功能 ---")
        
        # 创建交换机信息
        switch_info = SwitchInfo(
            ip="192.168.1.200",
            snmp_version="2c",
            community="public",
            description="Test Switch"
        )
        
        # 添加交换机
        success, message = db_manager.add_switch(switch_info)
        if success:
            print("交换机添加成功")
        else:
            print(f"交换机添加失败: {message}")
            return False
            
        # 查询交换机
        retrieved_switch = db_manager.get_switch_by_ip("192.168.1.200")
        if retrieved_switch:
            print("交换机查询成功")
            print(f"交换机IP: {retrieved_switch['ip']}")
            print(f"SNMP版本: {retrieved_switch['snmp_version']}")
        else:
            print("交换机查询失败")
            return False
            
        # 测试交换机计数
        switch_count = db_manager.get_switch_count()
        print(f"交换机总数: {switch_count}")
        
        print("\n所有测试通过!")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时数据库文件
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    success = test_database_manager()
    sys.exit(0 if success else 1)