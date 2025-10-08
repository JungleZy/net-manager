#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
跨平台兼容性测试脚本
用于验证客户端在Windows和Linux系统上的兼容性
"""

import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from src.utils.platform_utils import (
    get_platform, 
    is_windows, 
    is_linux, 
    get_path_separator,
    get_line_separator,
    normalize_path,
    get_executable_path
)
from src.config_module.config import config
LOG_FILE = config.get_log_file_path()


class TestCrossPlatformCompatibility(unittest.TestCase):
    
    def test_platform_detection(self):
        """测试平台检测功能"""
        platform_name = get_platform()
        self.assertIn(platform_name, ['windows', 'linux', 'darwin'])
        
        # 验证平台检测一致性
        if platform_name == 'windows':
            self.assertTrue(is_windows())
            self.assertFalse(is_linux())
        elif platform_name == 'linux':
            self.assertTrue(is_linux())
            self.assertFalse(is_windows())
    
    def test_path_separator(self):
        """测试路径分隔符"""
        separator = get_path_separator()
        if is_windows():
            self.assertEqual(separator, '\\')
        else:
            self.assertEqual(separator, '/')
    
    def test_line_separator(self):
        """测试行分隔符"""
        separator = get_line_separator()
        if is_windows():
            self.assertEqual(separator, '\r\n')
        else:
            self.assertEqual(separator, '\n')
    
    def test_path_normalization(self):
        """测试路径标准化"""
        # 测试相对路径
        relative_path = "test/path/file.txt"
        normalized = normalize_path(relative_path)
        self.assertIsInstance(normalized, str)
        
        # 测试包含不同分隔符的路径
        mixed_path = "test/path\\file.txt"
        normalized = normalize_path(mixed_path)
        self.assertIsInstance(normalized, str)
    
    def test_config_paths(self):
        """测试配置中的路径是否为Path对象"""
        self.assertIsInstance(LOG_FILE, Path)
        
        # 验证路径存在性
        # LOG_FILE的父目录应该存在
        self.assertTrue(LOG_FILE.parent.exists())
    
    def test_executable_path(self):
        """测试可执行文件路径获取"""
        exec_path = get_executable_path()
        self.assertIsInstance(exec_path, str)
        self.assertTrue(os.path.exists(exec_path))


if __name__ == "__main__":
    print("运行跨平台兼容性测试...")
    print(f"当前平台: {get_platform()}")
    unittest.main()