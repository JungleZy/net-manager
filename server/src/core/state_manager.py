#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Jungle
"""增强版统一状态管理器

提供线程安全的状态管理、事件发布订阅机制、性能监控和错误处理功能。
"""

import json

# 标准库导入
import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Union
from src.core.logger import logger

# 第三方库导入
import tornado.ioloop

class StateManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """实现线程安全的单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(StateManager, cls).__new__(cls)
        return cls._instance
      
    def __init__(self):
        """初始化状态管理器，确保只初始化一次"""
        # 确保只初始化一次
        if not hasattr(self, "initialized"):
            self.initialized = True

            # 基础状态数据结构
            self.connected_clients: Set = set()
            self.scan_task_id: Optional[str] = None
            
            # 事件监听器存储
            self._event_listeners: Dict[str, List[Callable]] = defaultdict(list)

            # 性能监控计数器
            self._message_count = 0
            self._broadcast_errors = 0

            # 主线程IOLoop引用
            self._main_ioloop = None

            # 线程锁，提高细粒度控制
            self._clients_lock = threading.RLock()
            self._event_lock = threading.RLock()

    # -------- WebSocket客户端管理 --------
    def set_main_ioloop(self, ioloop) -> None:
        """设置主线程IOLoop引用"""
        self._main_ioloop = ioloop

    def add_client(self, client) -> None:
        """线程安全地添加WebSocket客户端连接"""
        with self._clients_lock:
            self.connected_clients.add(client)

    def remove_client(self, client) -> None:
        """线程安全地移除WebSocket客户端连接"""
        with self._clients_lock:
            if client in self.connected_clients:
                self.connected_clients.remove(client)
            else:
                # 使用discard避免KeyError，但记录异常情况
                self.connected_clients.discard(client)

    def get_clients(self) -> Set:
        """获取所有连接的客户端的线程安全副本"""
        with self._clients_lock:
            return self.connected_clients.copy()

    def get_client_count(self) -> int:
        """获取当前连接的客户端数量"""
        with self._clients_lock:
            return len(self.connected_clients)
    
    # -------- 消息广播功能 --------
    def _send_message_in_main_thread(self, message: Dict[str, Any]) -> None:
        """在主线程中向所有客户端发送消息的内部方法"""
        start_time = time.time()
        clients = self.get_clients()

        if not clients:
            logger.debug("没有连接的客户端，跳过消息发送")
            return

        client_count = len(clients)
        disconnected_clients = []
        success_count = 0

        try:
            # 确保消息是JSON可序列化的
            message_str = json.dumps(message, ensure_ascii=False)
            self._message_count += 1

            for client in clients:
                try:
                    client.write_message(message_str)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"向客户端发送消息时出错: {str(e)}")
                    disconnected_clients.append(client)

            # 移除已断开的客户端
            for client in disconnected_clients:
                self.remove_client(client)

            execution_time = time.time() - start_time
            logger.debug(
                f"消息广播完成: 成功发送给{success_count}/{client_count}个客户端，耗时: {execution_time:.3f}秒"
            )

            # 如果有大量发送失败，记录警告
            if len(disconnected_clients) > client_count * 0.5:
                logger.warning(f"消息广播异常: 超过50%的客户端连接已断开")

        except Exception as e:
            self._broadcast_errors += 1
            logger.error(f"消息序列化或发送过程中出错: {str(e)}")

    def broadcast_message(
        self, message: Dict[str, Any], message_type: str = "general"
    ) -> None:
        """向所有连接的客户端广播消息

        Args:
            message: 要发送的消息内容，必须是JSON可序列化的
            message_type: 消息类型，用于客户端识别消息用途
        """
        try:
            
            # 添加消息元数据
            enriched_message = {
                **message,
                "type": message.get("type", message_type),
                "timestamp": time.time(),
                "sequence": self._message_count,
            }

            # 检查是否在主线程中
            current_ioloop = tornado.ioloop.IOLoop.current(instance=False)

            if current_ioloop is not None:
                # 在主线程中，直接发送消息
                self._send_message_in_main_thread(enriched_message)
            else:
                # 不在主线程中，需要通过IOLoop的add_callback方法在主线程中执行
                
                # 使用保存的主线程IOLoop引用
                try:
                    if self._main_ioloop is not None:
                        # 将消息发送任务添加到主线程的事件循环中
                        self._main_ioloop.add_callback(
                            self._send_message_in_main_thread, enriched_message
                        )
                        logger.debug("已将消息发送任务添加到主线程事件循环")
                    else:
                        # 如果没有保存的引用，尝试获取正在运行的IOLoop实例
                        main_ioloop = tornado.ioloop.IOLoop.instance()
                        main_ioloop.add_callback(
                            self._send_message_in_main_thread, enriched_message
                        )
                        logger.debug("已将消息发送任务添加到主线程事件循环")

                except Exception as e:
                    logger.error(f"无法获取主IOLoop实例: {str(e)}")
                    # 如果无法通过IOLoop发送，记录错误但不阻塞程序
        except Exception as e:
            self._broadcast_errors += 1
            logger.error(f"广播消息时发生错误: {str(e)}")


    # -------- 事件发布订阅系统 --------
    def subscribe_event(self, event_name: str, callback: Callable) -> None:
        """订阅特定事件

        Args:
            event_name: 事件名称
            callback: 事件触发时的回调函数
        """
        if not callable(callback):
            raise TypeError("回调必须是可调用对象")

        with self._event_lock:
            self._event_listeners[event_name].append(callback)

    def unsubscribe_event(self, event_name: str, callback: Callable) -> None:
        """取消订阅特定事件

        Args:
            event_name: 事件名称
            callback: 要移除的回调函数
        """
        with self._event_lock:
            if event_name in self._event_listeners:
                try:
                    self._event_listeners[event_name].remove(callback)

                    # 如果没有监听器了，清理事件
                    if not self._event_listeners[event_name]:
                        del self._event_listeners[event_name]
                except ValueError:
                    pass
    
    def _notify_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """通知所有订阅者事件已发生

        Args:
            event_name: 事件名称
            event_data: 事件数据
        """
        # 创建一个副本，避免在迭代过程中修改列表
        with self._event_lock:
            listeners = self._event_listeners.get(event_name, []).copy()

        if not listeners:
            return  # 没有监听器，直接返回

        # 在锁外执行回调，避免死锁
        for callback in listeners:
            try:
                callback(event_data)
            except Exception as e:
                pass
              
# 创建全局状态管理器实例
state_manager = StateManager()