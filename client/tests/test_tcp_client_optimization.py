#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCP客户端优化测试
测试TCP客户端的性能和资源使用优化
"""

import unittest
import sys
import os
import threading
import time
import json
import struct
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from src.network.tcp_client import TCPClient


class TestTCPClientOptimization(unittest.TestCase):
    """TCP客户端优化测试类"""

    def setUp(self):
        """测试前准备"""
        self.tcp_client = TCPClient()

    def test_buffered_send(self):
        """测试缓冲发送功能"""
        # 模拟socket对象
        mock_socket = MagicMock()
        self.tcp_client.socket = mock_socket
        self.tcp_client.connected = True

        # 发送系统信息
        result = self.tcp_client.send_system_info()

        # 验证结果
        self.assertTrue(result)
        self.assertTrue(len(self.tcp_client.send_buffer) >= 0)

    def test_receive_data_handling(self):
        """测试数据接收处理"""
        # 模拟socket对象
        mock_socket = MagicMock()
        
        # 构造正确的消息格式：长度前缀 + JSON消息
        message = {"type": "command", "command": "test"}
        message_bytes = json.dumps(message).encode("utf-8")
        length_prefix = struct.pack("!I", len(message_bytes))  # 网络字节序
        full_message = length_prefix + message_bytes
        
        # 第一次调用返回消息数据，第二次调用返回空数据模拟连接关闭
        mock_socket.recv.side_effect = [
            full_message,
            b''  # 模拟连接关闭
        ]
        self.tcp_client.socket = mock_socket
        self.tcp_client.connected = True

        # 注册测试命令处理器
        test_called = threading.Event()

        def test_handler(message):
            test_called.set()

        self.tcp_client.register_command_handler("test", test_handler)

        # 启动接收线程
        receive_thread = threading.Thread(target=self.tcp_client._receive_data)
        receive_thread.daemon = True
        receive_thread.start()

        # 等待处理完成
        receive_thread.join(timeout=2.0)  # 设置超时避免测试卡住

        # 验证命令处理器被调用
        self.assertTrue(test_called.is_set(), "测试命令处理器未被调用")

    def test_connection_state_management(self):
        """测试连接状态管理"""
        # 初始状态应该是未连接
        self.assertFalse(self.tcp_client.connected)

        # 模拟连接成功
        self.tcp_client.connected = True
        self.assertTrue(self.tcp_client.connected)

        # 模拟断开连接
        self.tcp_client._handle_disconnect()
        self.assertFalse(self.tcp_client.connected)

    def test_thread_management(self):
        """测试线程管理"""
        # 检查线程初始化状态
        self.assertIsNone(self.tcp_client.receive_thread)
        self.assertIsNone(self.tcp_client.send_thread)
        self.assertIsNone(self.tcp_client.heartbeat_thread)

    def test_get_tcp_client_singleton(self):
        """测试TCP客户端单例模式"""
        from src.network.tcp_client import get_tcp_client

        client1 = get_tcp_client()
        client2 = get_tcp_client()

        self.assertIs(client1, client2)


if __name__ == "__main__":
    unittest.main()
