#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态管理器测试文件
用于验证StateManager类的功能
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path

# 添加项目路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.state_manager import StateManager, get_state_manager
from src.utils.unique_id import get_or_create_unique_id


class TestStateManager(unittest.TestCase):
    """状态管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_app_path = None
        
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        self.temp_dir.cleanup()
        
        # 重置单例实例
        StateManager._instance = None
        
    def test_singleton_instance(self):
        """测试单例实例"""
        # 获取状态管理器实例
        state_manager1 = get_state_manager()
        state_manager2 = get_state_manager()
        
        # 验证是否为同一实例
        self.assertIs(state_manager1, state_manager2)
        
    def test_client_id_generation(self):
        """测试客户端ID生成"""
        # 获取状态管理器实例
        state_manager = get_state_manager()
        
        # 获取客户端ID
        client_id = state_manager.get_client_id()
        
        # 验证客户端ID不为空且为字符串
        self.assertIsInstance(client_id, str)
        self.assertNotEqual(client_id, "")
        
    def test_state_set_and_get(self):
        """测试状态设置和获取"""
        # 获取状态管理器实例
        state_manager = get_state_manager()
        
        # 设置状态值
        state_manager.set_state("test_key", "test_value")
        
        # 获取状态值
        value = state_manager.get_state("test_key")
        
        # 验证状态值正确性
        self.assertEqual(value, "test_value")
        
    def test_state_get_with_default(self):
        """测试带默认值的状态获取"""
        # 获取状态管理器实例
        state_manager = get_state_manager()
        
        # 获取不存在的状态值，应返回默认值
        value = state_manager.get_state("nonexistent_key", "default_value")
        
        # 验证返回默认值
        self.assertEqual(value, "default_value")
        
    def test_batch_state_update(self):
        """测试批量状态更新"""
        # 获取状态管理器实例
        state_manager = get_state_manager()
        
        # 批量更新状态
        state_data = {
            "status": "active",
            "version": "1.0.0",
            "last_update": "2025-10-05"
        }
        state_manager.update_client_state(state_data)
        
        # 验证状态是否正确更新
        self.assertEqual(state_manager.get_state("status"), "active")
        self.assertEqual(state_manager.get_state("version"), "1.0.0")
        self.assertEqual(state_manager.get_state("last_update"), "2025-10-05")
        
    def test_state_persistence(self):
        """测试状态持久化"""
        # 在临时目录中创建状态管理器
        temp_path = self.temp_dir.name
        state_file_path = os.path.join(temp_path, "client_state.json")
        
        # 创建第一个状态管理器实例并设置状态
        sm1 = StateManager.__new__(StateManager)
        sm1._app_path = temp_path
        sm1.__init__()
        sm1.set_state("persistent_key", "persistent_value")
        client_id1 = sm1.get_client_id()
        
        # 创建第二个状态管理器实例，应该从文件加载状态
        sm2 = StateManager.__new__(StateManager)
        sm2._app_path = temp_path
        sm2.__init__()
        loaded_value = sm2.get_state("persistent_key")
        client_id2 = sm2.get_client_id()
        
        # 验证状态已持久化并正确加载
        self.assertEqual(loaded_value, "persistent_value")
        self.assertEqual(client_id1, client_id2)
        
    def test_unique_id_consistency(self):
        """测试客户端ID的一致性"""
        # 在临时目录中测试
        temp_path = self.temp_dir.name
        
        # 多次获取客户端ID，应该保持一致
        client_id1 = get_or_create_unique_id(temp_path)
        client_id2 = get_or_create_unique_id(temp_path)
        
        # 验证客户端ID一致性
        self.assertEqual(client_id1, client_id2)


if __name__ == '__main__':
    unittest.main()