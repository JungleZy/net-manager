#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库管理器测试文件
用于验证重构后的DatabaseManager类功能
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径以便导入模块
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.database_manager import DatabaseManager
from src.models.system_info import SystemInfo

class TestDatabaseManager(unittest.TestCase):
    """数据库管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        
    def tearDown(self):
        """测试后清理"""
        # 删除临时数据库文件
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
            
    def test_init_db(self):
        """测试数据库初始化"""
        # 验证表是否创建成功
        self.assertTrue(self.db_manager.health_check())
        
    def test_save_system_info(self):
        """测试保存系统信息"""
        # 创建测试数据
        system_info = SystemInfo(
            hostname="test-host",
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:55",
            gateway="192.168.1.1",
            netmask="255.255.255.0",
            services=json.dumps(["ssh", "http"]),
            processes=json.dumps([{"name": "test", "pid": 1234}]),
            timestamp=datetime.now().isoformat(),
            client_id="test-client-1",
            os_name="Ubuntu",
            os_version="20.04",
            os_architecture="x86_64",
            machine_type="PC",
            type="server"
        )
        
        # 保存系统信息
        self.db_manager.save_system_info(system_info)
        
        # 验证信息是否保存成功
        result = self.db_manager.get_system_info_by_mac("00:11:22:33:44:55")
        self.assertIsNotNone(result)
        self.assertEqual(result['hostname'], "test-host")
        self.assertEqual(result['ip_address'], "192.168.1.100")
        self.assertEqual(result['mac_address'], "00:11:22:33:44:55")
        
    def test_get_all_system_info(self):
        """测试获取所有系统信息"""
        # 添加测试数据
        system_info1 = SystemInfo(
            hostname="host1",
            ip_address="192.168.1.101",
            mac_address="00:11:22:33:44:56",
            gateway="192.168.1.1",
            netmask="255.255.255.0",
            services=json.dumps([]),
            processes=json.dumps([]),
            timestamp=datetime.now().isoformat()
        )
        
        system_info2 = SystemInfo(
            hostname="host2",
            ip_address="192.168.1.102",
            mac_address="00:11:22:33:44:57",
            gateway="192.168.1.1",
            netmask="255.255.255.0",
            services=json.dumps([]),
            processes=json.dumps([]),
            timestamp=datetime.now().isoformat()
        )
        
        self.db_manager.save_system_info(system_info1)
        self.db_manager.save_system_info(system_info2)
        
        # 获取所有系统信息
        all_info = self.db_manager.get_all_system_info()
        self.assertEqual(len(all_info), 2)
        
    def test_update_system_type(self):
        """测试更新系统类型"""
        # 添加测试数据
        system_info = SystemInfo(
            hostname="test-host",
            ip_address="192.168.1.100",
            mac_address="00:11:22:33:44:58",
            gateway="192.168.1.1",
            netmask="255.255.255.0",
            services=json.dumps([]),
            processes=json.dumps([]),
            timestamp=datetime.now().isoformat()
        )
        
        self.db_manager.save_system_info(system_info)
        
        # 更新系统类型
        result = self.db_manager.update_system_type("00:11:22:33:44:58", "switch")
        self.assertTrue(result)
        
        # 验证更新结果
        updated_info = self.db_manager.get_system_info_by_mac("00:11:22:33:44:58")
        self.assertEqual(updated_info['type'], "switch")
        
    def test_create_device(self):
        """测试创建设备"""
        device_data = {
            'mac_address': '00:11:22:33:44:59',
            'hostname': 'new-device',
            'ip_address': '192.168.1.103',
            'gateway': '192.168.1.1',
            'netmask': '255.255.255.0',
            'os_name': 'Ubuntu',
            'os_version': '20.04',
            'type': 'server'
        }
        
        # 创建设备
        success, message = self.db_manager.create_device(device_data)
        self.assertTrue(success)
        
        # 验证设备是否创建成功
        result = self.db_manager.get_system_info_by_mac('00:11:22:33:44:59')
        self.assertIsNotNone(result)
        self.assertEqual(result['hostname'], 'new-device')
        
    def test_update_device(self):
        """测试更新设备"""
        # 先创建设备
        device_data = {
            'mac_address': '00:11:22:33:44:60',
            'hostname': 'old-device',
            'ip_address': '192.168.1.104',
            'gateway': '192.168.1.1',
            'netmask': '255.255.255.0'
        }
        
        self.db_manager.create_device(device_data)
        
        # 更新设备
        updated_data = {
            'mac_address': '00:11:22:33:44:60',
            'hostname': 'updated-device',
            'ip_address': '192.168.1.105',
            'gateway': '192.168.1.1',
            'netmask': '255.255.255.0',
            'type': 'workstation'
        }
        
        success, message = self.db_manager.update_device(updated_data)
        self.assertTrue(success)
        
        # 验证更新结果
        result = self.db_manager.get_system_info_by_mac('00:11:22:33:44:60')
        self.assertEqual(result['hostname'], 'updated-device')
        self.assertEqual(result['ip_address'], '192.168.1.105')
        self.assertEqual(result['type'], 'workstation')
        
    def test_delete_device(self):
        """测试删除设备"""
        # 先创建设备
        device_data = {
            'mac_address': '00:11:22:33:44:61',
            'hostname': 'device-to-delete',
            'ip_address': '192.168.1.106',
            'gateway': '192.168.1.1',
            'netmask': '255.255.255.0'
        }
        
        self.db_manager.create_device(device_data)
        
        # 验证设备存在
        result = self.db_manager.get_system_info_by_mac('00:11:22:33:44:61')
        self.assertIsNotNone(result)
        
        # 删除设备
        success, message = self.db_manager.delete_device('00:11:22:33:44:61')
        self.assertTrue(success)
        
        # 验证设备已删除
        result = self.db_manager.get_system_info_by_mac('00:11:22:33:44:61')
        self.assertIsNone(result)
        
    def test_get_device_count(self):
        """测试获取设备总数"""
        # 初始设备数应该为0
        count = self.db_manager.get_device_count()
        self.assertEqual(count, 0)
        
        # 添加设备
        device_data = {
            'mac_address': '00:11:22:33:44:62',
            'hostname': 'count-test',
            'ip_address': '192.168.1.107',
            'gateway': '192.168.1.1',
            'netmask': '255.255.255.0'
        }
        
        self.db_manager.create_device(device_data)
        
        # 验证设备数
        count = self.db_manager.get_device_count()
        self.assertEqual(count, 1)

if __name__ == '__main__':
    unittest.main()