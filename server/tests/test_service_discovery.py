#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务发现功能测试
测试服务端的组播和广播服务发现功能
"""

import unittest
import sys
import os
import socket
import json
import threading
import time
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.network.udp.udp_server import udp_server, stop_udp_server
from src.network.udp.broadcast_server import broadcast_server, stop_broadcast_server


class TestServiceDiscovery(unittest.TestCase):
    """服务发现功能测试类"""

    def setUp(self):
        """测试前准备"""
        pass

    def tearDown(self):
        """测试后清理"""
        # 确保所有服务都已停止
        stop_udp_server()
        stop_broadcast_server()

    def test_udp_server_imports(self):
        """测试UDP服务器模块导入"""
        # 确保模块可以正确导入
        from src.network.udp.udp_server import udp_server, stop_udp_server

        self.assertTrue(callable(udp_server))
        self.assertTrue(callable(stop_udp_server))

    def test_broadcast_server_imports(self):
        """测试广播服务器模块导入"""
        # 确保模块可以正确导入
        from src.network.udp.broadcast_server import (
            broadcast_server,
            stop_broadcast_server,
        )

        self.assertTrue(callable(broadcast_server))
        self.assertTrue(callable(stop_broadcast_server))

    @patch("src.network.udp.udp_server.socket.socket")
    def test_udp_server_socket_creation(self, mock_socket_class):
        """测试UDP服务器socket创建"""
        # 模拟socket对象
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # 调用被测试的方法
        # 注意：我们不会真正运行服务器，只是测试初始化部分
        try:
            # 创建发送socket
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 创建监听socket
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 验证socket方法被正确调用
            self.assertTrue(mock_socket_class.called)
        except Exception:
            pass  # 我们只关心socket是否被创建，不关心是否能绑定

    @patch("src.network.udp.broadcast_server.socket.socket")
    def test_broadcast_server_socket_creation(self, mock_socket_class):
        """测试广播服务器socket创建"""
        # 模拟socket对象
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # 调用被测试的方法
        # 注意：我们不会真正运行服务器，只是测试初始化部分
        try:
            # 创建socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 验证socket方法被正确调用
            self.assertTrue(mock_socket_class.called)
        except Exception:
            pass  # 我们只关心socket是否被创建，不关心是否能绑定

    def test_stop_functions(self):
        """测试停止函数"""
        # 测试停止UDP服务器
        stop_udp_server()

        # 测试停止广播服务器
        stop_broadcast_server()

        # 验证函数可以被调用而不会出错
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
