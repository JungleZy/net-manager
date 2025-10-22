#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务发现功能测试
测试UDP客户端的服务发现功能
"""

import unittest
import sys
import os
import socket
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from src.network.udp_client import UDPClient


class TestServiceDiscovery(unittest.TestCase):
    """服务发现功能测试类"""

    def setUp(self):
        """测试前准备"""
        self.udp_client = UDPClient()

    def test_init(self):
        """测试UDP客户端初始化"""
        self.assertIsInstance(self.udp_client, UDPClient)
        self.assertIsNotNone(self.udp_client.logger)

    @patch("src.network.udp_client.socket.socket")
    def test_discover_server_multicast_success(self, mock_socket_class):
        """测试多播服务发现成功"""
        # 模拟socket对象
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # 模拟接收数据
        mock_socket_instance.recvfrom.return_value = (
            b'{"type": "discovery_response", "tcp_port": 12346}',
            ("192.168.1.100", 37020),
        )

        # 调用被测试的方法
        result = self.udp_client.discover_server_multicast()

        # 验证结果
        self.assertEqual(result, ("192.168.1.100", 12346))

        # 验证socket方法被正确调用
        mock_socket_class.assert_called()
        mock_socket_instance.sendto.assert_called()
        mock_socket_instance.recvfrom.assert_called()

    @patch("src.network.udp_client.socket.socket")
    def test_discover_server_multicast_no_response(self, mock_socket_class):
        """测试多播服务发现无响应"""
        # 模拟socket对象
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # 模拟接收超时
        mock_socket_instance.recvfrom.side_effect = socket.timeout

        # 调用被测试的方法
        result = self.udp_client.discover_server_multicast()

        # 验证结果
        self.assertIsNone(result)

    def test_get_udp_client_singleton(self):
        """测试UDP客户端单例模式"""
        from src.network.udp_client import get_udp_client

        client1 = get_udp_client()
        client2 = get_udp_client()

        self.assertIs(client1, client2)


if __name__ == "__main__":
    unittest.main()
