#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用控制器模块
负责协调和管理应用程序的各个组件
包括配置管理、系统信息收集、网络通信等功能
"""

import signal
import time
import json
import threading
from typing import Optional, Any, Dict, Callable

# 第三方库导入
import psutil

# 本地应用/库导入
from src.config_module.config import config
from src.exceptions.exceptions import (
    NetworkDiscoveryError,
    NetworkConnectionError,
    SystemInfoCollectionError,
    ConfigurationError
)
from src.network.tcp_client import get_tcp_client, initialize_tcp_client
from src.system.system_collector import SystemCollector
from src.system.autostart import enable_autostart, disable_autostart, is_autostart_enabled
from src.utils.logger import get_logger
from src.utils.platform_utils import get_executable_path


class AppController:
    """
    应用控制器类
    负责协调和管理应用程序的各个组件
    """
    
    def __init__(self):
        """
        初始化应用控制器
        """
        self.logger = get_logger()
        self.tcp_client: Optional[Any] = None
        self.system_collector = SystemCollector()
        self.running = False
        self.main_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # 注册信号处理器
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """
        设置信号处理器
        """
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self.logger.debug("信号处理器设置成功")
        except Exception as e:
            self.logger.error(f"设置信号处理器失败: {e}")
    
    def _signal_handler(self, signum: int, frame: Any) -> None:
        """
        信号处理函数
        
        Args:
            signum (int): 信号编号
            frame (Any): 帧对象
        """
        self.logger.info(f"收到信号 {signum}，准备退出...")
        self.stop()
    
    def _calculate_system_info_hash(self, system_info: Any) -> str:
        """
        计算系统信息的哈希值，用于检测系统信息是否发生变化
        
        Args:
            system_info: 系统信息对象
            
        Returns:
            str: 系统信息的哈希值
        """
        try:
            # 提取关键信息用于哈希计算
            key_info = {
                "hostname": system_info.hostname,
                "ip_address": system_info.ip_address,
                "mac_address": system_info.mac_address,
                "gateway": system_info.gateway,
                "netmask": system_info.netmask,
                "os_name": system_info.os_name,
                "os_version": system_info.os_version,
                "os_architecture": system_info.os_architecture,
                "machine_type": system_info.machine_type
            }
            
            # 转换为JSON字符串并计算哈希值
            info_str = json.dumps(key_info, sort_keys=True)
            import hashlib
            return hashlib.md5(info_str.encode('utf-8')).hexdigest()
        except Exception as e:
            self.logger.error(f"计算系统信息哈希值失败: {e}")
            return ""
    
    def _handle_autostart(self) -> None:
        """
        处理开机自启动设置
        """
        try:
            # 启用开机自启动
            client_path = get_executable_path()
            if enable_autostart(client_path):
                self.logger.info("已启用开机自启动")
            else:
                self.logger.error("启用开机自启动失败")
        except Exception as e:
            self.logger.error(f"处理开机自启动设置失败: {e}")
    
    def _connect_to_server_with_retry(self, retry_delay: float = 5.0) -> bool:
        """
        尝试连接到服务端，带无限重试机制
        
        Args:
            retry_delay (float): 重试间隔（秒）
            
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        attempt = 0
        server_address = None
        
        while self.running:
            try:
                attempt += 1
                self.logger.info(f"尝试连接到服务端 (第{attempt}次)")
                
                # 只在第一次尝试时初始化TCP客户端和发现服务端
                if attempt == 1:
                    # 初始化TCP客户端
                    self.tcp_client = initialize_tcp_client()
                    
                    # 发现服务端
                    server_address = self.tcp_client.discover_server()
                    if not server_address:
                        self.logger.warning("未发现服务端")
                        self.logger.info(f"等待{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        continue
                
                # 检查是否已获取到服务端地址
                if not server_address:
                    self.logger.warning("未发现服务端")
                    self.logger.info(f"等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                
                # 连接到服务端
                if self.tcp_client.connect():
                    self.logger.info(f"成功连接到服务端 {server_address}")
                    return True
                else:
                    self.logger.error("连接到服务端失败")
                    self.logger.info(f"等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                        
            except NetworkDiscoveryError as e:
                # 只在第一次尝试时处理发现错误
                if attempt == 1:
                    self.logger.warning(f"服务端发现失败: {e}")
                    self.logger.info(f"等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    # 如果不是第一次尝试，直接重试连接
                    self.logger.info(f"等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
            except NetworkConnectionError as e:
                self.logger.warning(f"连接到服务端失败: {e}")
                self.logger.info(f"等待{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                continue
            except Exception as e:
                self.logger.error(f"连接到服务端时发生未知错误: {e}")
                self.logger.info(f"等待{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                continue
        
        # 如果running为False，则返回False
        return False
    
    def _send_system_info(self) -> bool:
        """
        收集并发送系统信息到服务端
        
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        try:
            # 发送系统信息
            if self.tcp_client and self.tcp_client.is_connected():
                success = self.tcp_client.send_system_info()
                if success:
                    self.logger.info("系统信息发送成功")
                    return True
                else:
                    self.logger.error("系统信息发送失败")
                    return False
            else:
                self.logger.warning("TCP客户端未连接，无法发送系统信息")
                return False
                
        except SystemInfoCollectionError as e:
            self.logger.error(f"系统信息收集失败: {e}")
            return False
        except NetworkConnectionError as e:
            self.logger.error(f"发送系统信息失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送系统信息时发生未知错误: {e}")
            return False
    
    def _run_main_loop(self) -> None:
        """
        运行应用主循环
        """
        self.logger.info("应用主循环开始")
        
        # 连接到服务端
        if not self._connect_to_server_with_retry():
            self.logger.error("无法连接到服务端，应用退出")
            self.running = False
            return
        
        # 发送初始系统信息
        self._send_system_info()
        
        # 主循环
        while self.running and not self.stop_event.is_set():
            try:
                # 检查TCP连接状态
                if not self.tcp_client or not self.tcp_client.is_connected():
                    self.logger.warning("与服务端的连接已断开，尝试重新连接...")
                    if not self._connect_to_server_with_retry():
                        self.logger.error("重新连接到服务端失败")
                        break
                
                # 定期发送心跳或系统信息（使用配置的间隔时间）
                self.stop_event.wait(config.COLLECT_INTERVAL)
                if self.running and not self.stop_event.is_set():
                    self._send_system_info()
                    
            except Exception as e:
                self.logger.error(f"主循环中发生错误: {e}")
                if self.running and not self.stop_event.is_set():
                    # 出错后短暂等待再继续
                    self.stop_event.wait(5)
        
        self.logger.info("应用主循环结束")
    
    def start(self) -> None:
        """
        启动应用控制器
        """
        if self.running:
            self.logger.warning("应用已在运行中")
            return
        
        self.logger.info("启动应用控制器")
        self.running = True
        self.stop_event.clear()
        
        try:
            # 处理开机自启动设置
            self._handle_autostart()
            
            # 在单独的线程中运行主循环
            self.main_thread = threading.Thread(target=self._run_main_loop, daemon=True)
            self.main_thread.start()
            
            self.logger.info("应用控制器启动成功")
        except Exception as e:
            self.logger.error(f"启动应用控制器失败: {e}")
            self.running = False
            raise
    
    def stop(self) -> None:
        """
        停止应用控制器
        """
        if not self.running:
            return
        
        self.logger.info("停止应用控制器")
        self.running = False
        self.stop_event.set()
        
        try:
            # 断开TCP连接
            if self.tcp_client:
                self.tcp_client.disconnect()
            
            # 等待主循环线程结束
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join(timeout=5.0)
                
        except Exception as e:
            self.logger.error(f"停止应用控制器时发生错误: {e}")
        finally:
            self.logger.info("应用控制器已停止")
    
    def wait(self) -> None:
        """
        等待应用控制器结束
        """
        if self.main_thread and self.main_thread.is_alive():
            # 使用循环等待，每次等待一小段时间，以便能够响应中断信号
            while self.main_thread.is_alive():
                self.main_thread.join(timeout=1.0)  # 每秒检查一次
    
    def cleanup(self) -> None:
        """
        清理资源
        """
        self.logger.info("清理应用控制器资源")
        self.stop()


# 全局应用控制器实例
_app_controller_instance: Optional[AppController] = None
_app_controller_lock = threading.RLock()


def get_app_controller() -> AppController:
    """
    获取应用控制器单例实例
    
    Returns:
        AppController: 应用控制器实例
    """
    global _app_controller_instance
    
    with _app_controller_lock:
        if _app_controller_instance is None:
            _app_controller_instance = AppController()
            get_logger().info("应用控制器实例已创建")
        return _app_controller_instance