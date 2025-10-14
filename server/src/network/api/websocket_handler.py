#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Jungle
"""WebSocket处理器模块"""

import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime

import tornado.ioloop

# 导入Tornado库
import tornado.websocket
from src.core.logger import logger
from src.core.state_manager import state_manager


# WebSocket处理器
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        # 允许所有来源的WebSocket连接
        return True

    def open(self, *args, **kwargs):
        """新的WebSocket连接建立

        Args:
            *args: 从URL路由提取的位置参数
            **kwargs: 从URL路由提取的关键字参数
        """
        state_manager.add_client(self)
        self.send_message(
            {
                "type": "scanTask",
                "data": {
                    "task_id": state_manager.scan_task_id,
                    "event": "scan_push",
                },
            }
        )

    def on_message(self, message):
        """处理接收到的WebSocket消息"""
        try:
            data = json.loads(message)

        except json.JSONDecodeError:
            self.send_error_message("无效的JSON格式")
        except Exception as e:
            self.send_error_message(f"处理消息时发生错误: {str(e)}")

    def on_close(self):
        """WebSocket连接关闭"""
        state_manager.remove_client(self)

    def send_message(self, message):
        """向客户端发送WebSocket消息"""
        try:
            self.write_message(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(msg=f"发送WebSocket消息时出错: {e}，消息内容: {message}")
            # 发送失败可能意味着连接已断开，尝试从客户端集合中移除
            state_manager.remove_client(self)

    def send_error_message(self, error_message):
        """向客户端发送错误消息

        Args:
            error_message: 错误消息内容
        """
        self.send_message({"type": "error", "data": {"message": error_message}})
