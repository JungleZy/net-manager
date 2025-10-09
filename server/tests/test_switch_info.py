#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwitchInfo模型和数据库操作测试脚本
"""

import sys
import os
import unittest
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.switch_info import SwitchInfo
from src.database import DatabaseManager
from src.database.db_exceptions import DeviceAlreadyExistsError, DeviceNotFoundError

class TestSwitchInfoModel(unittest.TestCase):
    """SwitchInfo模型测试类"""

    def test_switch_info_creation(self):
        """测试SwitchInfo对象的创建"""
        switch = SwitchInfo(
            ip="192.168.1.100",
            snmp_version="2c",
            community="public",
            description="Core Switch"
        )
        
        self.assertEqual(switch.ip, "192.168.1.100")
        self.assertEqual(switch.snmp_version, "2c")
        self.assertEqual(switch.community, "public")
        self.assertEqual(switch.description, "Core Switch")
        self.assertIsNotNone(switch.created_at)
        self.assertIsNotNone(switch.updated_at)

    def test_switch_info_to_dict(self):
        """测试SwitchInfo对象转换为字典"""
        switch = SwitchInfo(
            id=1,
            ip="192.168.1.100",
            snmp_version="2c",
            community="public",
            description="Core Switch"
        )
        
        switch_dict = switch.to_dict()
        self.assertEqual(switch_dict['id'], 1)
        self.assertEqual(switch_dict['ip'], "192.168.1.100")
        self.assertEqual(switch_dict['snmp_version'], "2c")
        self.assertEqual(switch_dict['community'], "public")
        self.assertEqual(switch_dict['description'], "Core Switch")

    def test_switch_info_from_dict(self):
        """测试从字典创建SwitchInfo对象"""
        switch_data = {
            'id': 1,
            'ip': "192.168.1.100",
            'snmp_version': "2c",
            'community': "public",
            'user': "",
            'auth_key': "",
            'auth_protocol': "",
            'priv_key': "",
            'priv_protocol': "",
            'description': "Core Switch",
            'created_at': "2023-01-01T10:00:00",
            'updated_at': "2023-01-01T10:00:00"
        }
        
        switch = SwitchInfo.from_dict(switch_data)
        self.assertEqual(switch.id, 1)
        self.assertEqual(switch.ip, "192.168.1.100")
        self.assertEqual(switch.snmp_version, "2c")
        self.assertEqual(switch.community, "public")
        self.assertEqual(switch.description, "Core Switch")
        self.assertEqual(switch.created_at, "2023-01-01T10:00:00")
        self.assertEqual(switch.updated_at, "2023-01-01T10:00:00")


class TestSwitchDatabaseOperations(unittest.TestCase):
    """交换机数据库操作测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建测试数据库
        cls.db_manager = DatabaseManager("test_net_manager_server.db")

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 删除测试数据库
        if os.path.exists("test_net_manager_server.db"):
            os.remove("test_net_manager_server.db")

    def test_add_switch(self):
        """测试添加交换机"""
        switch = SwitchInfo(
            ip="192.168.1.101",
            snmp_version="2c",
            community="public",
            description="Test Switch"
        )
        
        success, message = self.db_manager.add_switch(switch)
        self.assertTrue(success)
        self.assertEqual(message, "交换机配置添加成功")

    def test_add_duplicate_switch(self):
        """测试添加重复IP的交换机"""
        switch1 = SwitchInfo(
            ip="192.168.1.102",
            snmp_version="2c",
            community="public",
            description="Test Switch 1"
        )
        
        switch2 = SwitchInfo(
            ip="192.168.1.102",  # 相同IP
            snmp_version="3",
            user="admin",
            auth_key="authkey",
            auth_protocol="SHA",
            description="Test Switch 2"
        )
        
        # 添加第一个交换机
        self.db_manager.add_switch(switch1)
        
        # 尝试添加具有相同IP的交换机，应该抛出异常
        with self.assertRaises(DeviceAlreadyExistsError):
            self.db_manager.add_switch(switch2)

    def test_get_switch_by_id(self):
        """测试根据ID获取交换机"""
        switch = SwitchInfo(
            ip="192.168.1.103",
            snmp_version="3",
            user="admin",
            auth_key="authkey",
            auth_protocol="SHA",
            description="Test Switch for Get by ID"
        )
        
        # 添加交换机
        self.db_manager.add_switch(switch)
        
        # 获取所有交换机以找到新添加的交换机ID
        switches = self.db_manager.get_all_switches()
        new_switch = next((s for s in switches if s['ip'] == "192.168.1.103"), None)
        self.assertIsNotNone(new_switch)
        
        # 根据ID获取交换机
        retrieved_switch = self.db_manager.get_switch_by_id(new_switch['id'])
        self.assertIsNotNone(retrieved_switch)
        self.assertEqual(retrieved_switch['ip'], "192.168.1.103")
        self.assertEqual(retrieved_switch['snmp_version'], "3")
        self.assertEqual(retrieved_switch['description'], "Test Switch for Get by ID")

    def test_get_switch_by_ip(self):
        """测试根据IP获取交换机"""
        switch = SwitchInfo(
            ip="192.168.1.104",
            snmp_version="2c",
            community="private",
            description="Test Switch for Get by IP"
        )
        
        # 添加交换机
        self.db_manager.add_switch(switch)
        
        # 根据IP获取交换机
        retrieved_switch = self.db_manager.get_switch_by_ip("192.168.1.104")
        self.assertIsNotNone(retrieved_switch)
        self.assertEqual(retrieved_switch['ip'], "192.168.1.104")
        self.assertEqual(retrieved_switch['snmp_version'], "2c")
        self.assertEqual(retrieved_switch['community'], "private")
        self.assertEqual(retrieved_switch['description'], "Test Switch for Get by IP")

    def test_get_all_switches(self):
        """测试获取所有交换机"""
        # 获取当前交换机数量
        initial_count = self.db_manager.get_switch_count()
        
        # 添加几个测试交换机
        switch1 = SwitchInfo(
            ip="192.168.1.105",
            snmp_version="2c",
            community="public",
            description="Test Switch 1"
        )
        
        switch2 = SwitchInfo(
            ip="192.168.1.106",
            snmp_version="3",
            user="admin",
            auth_key="authkey",
            auth_protocol="SHA",
            description="Test Switch 2"
        )
        
        self.db_manager.add_switch(switch1)
        self.db_manager.add_switch(switch2)
        
        # 获取所有交换机
        switches = self.db_manager.get_all_switches()
        self.assertGreaterEqual(len(switches), 2)
        
        # 验证新添加的交换机在结果中
        switch_ips = [s['ip'] for s in switches]
        self.assertIn("192.168.1.105", switch_ips)
        self.assertIn("192.168.1.106", switch_ips)

    def test_update_switch(self):
        """测试更新交换机"""
        # 添加一个交换机
        switch = SwitchInfo(
            ip="192.168.1.107",
            snmp_version="2c",
            community="public",
            description="Original Description"
        )
        
        self.db_manager.add_switch(switch)
        
        # 获取该交换机的ID
        retrieved_switch = self.db_manager.get_switch_by_ip("192.168.1.107")
        self.assertIsNotNone(retrieved_switch)
        
        # 更新交换机信息
        updated_switch = SwitchInfo(
            id=retrieved_switch['id'],
            ip="192.168.1.107",
            snmp_version="3",
            user="admin",
            auth_key="newauthkey",
            auth_protocol="SHA",
            description="Updated Description"
        )
        
        success, message = self.db_manager.update_switch(updated_switch)
        self.assertTrue(success)
        self.assertEqual(message, "交换机配置更新成功")
        
        # 验证更新结果
        updated_retrieved_switch = self.db_manager.get_switch_by_id(retrieved_switch['id'])
        self.assertEqual(updated_retrieved_switch['snmp_version'], "3")
        self.assertEqual(updated_retrieved_switch['description'], "Updated Description")
        self.assertEqual(updated_retrieved_switch['user'], "admin")

    def test_delete_switch(self):
        """测试删除交换机"""
        # 添加一个交换机
        switch = SwitchInfo(
            ip="192.168.1.108",
            snmp_version="2c",
            community="public",
            description="Test Switch for Deletion"
        )
        
        self.db_manager.add_switch(switch)
        
        # 获取该交换机的ID
        retrieved_switch = self.db_manager.get_switch_by_ip("192.168.1.108")
        self.assertIsNotNone(retrieved_switch)
        
        # 删除交换机
        success, message = self.db_manager.delete_switch(retrieved_switch['id'])
        self.assertTrue(success)
        self.assertEqual(message, "交换机配置删除成功")
        
        # 验证交换机已被删除
        deleted_switch = self.db_manager.get_switch_by_id(retrieved_switch['id'])
        self.assertIsNone(deleted_switch)

    def test_delete_nonexistent_switch(self):
        """测试删除不存在的交换机"""
        # 尝试删除一个不存在的交换机，应该抛出异常
        with self.assertRaises(DeviceNotFoundError):
            self.db_manager.delete_switch(99999)


if __name__ == '__main__':
    unittest.main()