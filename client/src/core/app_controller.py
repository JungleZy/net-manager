#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用程序控制器
负责管理NetManager客户端的生命周期和核心逻辑
"""

import time
import json
import hashlib
import threading
from typing import Optional
from datetime import datetime

from ..config_module.config import config
from ..system.system_collector import SystemCollector, SystemInfo
from ..network.tcp_client import TCPClient
from ..utils.logger import logger
from ..utils.platform_utils import setup_signal_handlers
from ..system.autostart import enable_autostart, disable_autostart, is_autostart_enabled, create_daemon_script
from ..utils.singleton_manager import get_client_singleton_manager
from ..core.state_manager import get_state_manager


class AppController:
    """应用程序控制器，管理客户端的核心逻辑"""
    
    def __init__(self):
        """初始化应用程序控制器"""
        # 配置值
        self.collect_interval = config.COLLECT_INTERVAL
        
        # 核心组件
        self.collector: Optional[SystemCollector] = None
        self.tcp_client: Optional[TCPClient] = None
        
        # 状态管理
        self.last_system_info_hash: Optional[str] = None
        self.shutdown_event = threading.Event()
        
        # 单例管理器
        self.singleton_manager = get_client_singleton_manager()
        
        # 初始化标志
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        初始化应用程序控制器
        
        Returns:
            bool: 初始化成功返回True，否则返回False
        """
        if self.initialized:
            return True
            
        try:
            # 尝试获取锁
            if not self.singleton_manager.acquire_lock():
                logger.error("客户端已在运行中，请勿重复启动")
                return False
            
            # 获取状态管理器实例
            self.state_manager = get_state_manager()
            client_id = self.state_manager.get_client_id()
            logger.info(f"客户端唯一标识符: {client_id}")
            
            # 初始化各组件
            self.collector = SystemCollector()
            self.tcp_client = TCPClient()
            
            # 设置信号处理器
            setup_signal_handlers(self._signal_handler)
            
            self.initialized = True
            logger.info("应用程序控制器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"应用程序控制器初始化失败: {e}")
            return False
    
    def _signal_handler(self, sig, frame):
        """信号处理函数"""
        logger.info("接收到终止信号，正在关闭程序...")
        self.shutdown()
    
    def _calculate_system_info_hash(self, system_info: SystemInfo) -> str:
        """
        计算系统信息的哈希值，用于比较两次数据是否相同
        
        Args:
            system_info (SystemInfo): 系统信息对象
            
        Returns:
            str: 系统信息的MD5哈希值
        """
        try:
            # 将SystemInfo对象转换为字典，排除时间戳字段
            info_dict = {
                'hostname': system_info.hostname,
                'ip_address': system_info.ip_address,
                'mac_address': system_info.mac_address,
                'services': system_info.services,  # 这已经是JSON字符串
                'processes': system_info.processes  # 这已经是JSON字符串
            }
            
            # 将字典转换为JSON字符串并计算哈希值
            info_str = json.dumps(info_dict, sort_keys=True)
            return hashlib.md5(info_str.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"计算系统信息哈希值失败: {e}")
            return ""
    
    def _handle_autostart(self) -> None:
        """处理开机自启动和守护进程功能"""
        try:
            import sys
            # 检查是否处于打包环境（Nuitka或PyInstaller）
            is_frozen = hasattr(sys, 'frozen') and sys.frozen
            is_nuitka = '__compiled__' in globals()
            
            if is_frozen or is_nuitka:
                logger.info("检测到打包环境，执行开机自启动和守护进程功能")
                
                # 默认启动时自动启用开机自启动和创建守护进程
                if is_autostart_enabled():
                    logger.info("开机自启动已启用")
                else:
                    if enable_autostart():
                        logger.info("已自动启用开机自启动")
                    else:
                        logger.warning("自动启用开机自启动失败")
                    
                if create_daemon_script():
                    logger.info("已自动创建守护进程脚本")
                else:
                    logger.warning("自动创建守护进程脚本失败")
            else:
                logger.info("检测到开发环境，跳过开机自启动和守护进程功能")
        except Exception as e:
            logger.error(f"处理开机自启动功能时出错: {e}")
    
    def _connect_to_server(self) -> bool:
        """
        连接到服务端
        
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        connection_retry_count = 0
        max_retries = 3
        
        while connection_retry_count < max_retries and not self.shutdown_event.is_set():
            try:
                # 尝试通过UDP发现并连接到服务端
                if self.tcp_client.discover_server():
                    if self.tcp_client.connect_to_server():
                        logger.info("已通过TCP连接到服务端")
                        return True
                    else:
                        connection_retry_count += 1
                        logger.warning(f"TCP连接失败，正在进行第{connection_retry_count}次重试...")
                else:
                    connection_retry_count += 1
                    logger.warning(f"无法通过UDP发现服务端，正在进行第{connection_retry_count}次重试...")
                
                # 添加延迟
                if self.shutdown_event.wait(5):
                    break
                    
            except Exception as e:
                connection_retry_count += 1
                logger.error(f"连接到服务端时发生错误: {e}，正在进行第{connection_retry_count}次重试...")
        
        if connection_retry_count >= max_retries:
            logger.error("达到最大重试次数，无法连接到服务端")
        
        return False
    
    def _send_system_info(self, system_info: SystemInfo) -> bool:
        """
        发送系统信息到服务端
        
        Args:
            system_info (SystemInfo): 系统信息对象
            
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        try:
            # 计算当前系统信息的哈希值
            current_hash = self._calculate_system_info_hash(system_info)
            
            # 比较当前数据与上一次数据是否相同
            if current_hash != self.last_system_info_hash:
                logger.info("系统信息发生变化，准备发送到服务端...")
                
                # 通过TCP发送到服务端
                send_success = False
                if self.tcp_client and self.tcp_client.is_connected():
                    success_tcp = self.tcp_client.send_system_info(system_info)
                    if success_tcp:
                        # 更新上一次的哈希值
                        self.last_system_info_hash = current_hash
                        logger.info("系统信息已发送到服务端")
                        send_success = True
                    else:
                        logger.warning("系统信息TCP发送失败")
                else:
                    logger.warning("TCP连接已断开")
                
                # 如果发送失败，尝试重新连接
                if not send_success:
                    logger.info("尝试重新连接到服务端...")
                    if self._connect_to_server():
                        logger.info("TCP连接已恢复")
                        if self.tcp_client.send_system_info(system_info):
                            self.last_system_info_hash = current_hash
                            logger.info("系统信息已重新发送到服务端")
                            send_success = True
                        else:
                            logger.warning("重新发送数据失败")
                    else:
                        logger.warning("重新连接失败")
                
                return send_success
            else:
                logger.debug("系统信息未发生变化，跳过发送")
                return True
        except Exception as e:
            logger.error(f"发送系统信息时发生错误: {e}")
            return False
    
    def _reconnect_to_server(self) -> bool:
        """
        重新连接到服务端
        
        Returns:
            bool: 重连成功返回True，否则返回False
        """
        try:
            logger.info("尝试重新连接到服务端...")
            if self.tcp_client.discover_server() and self.tcp_client.connect_to_server():
                logger.info("TCP连接已恢复")
                return True
            else:
                logger.warning("重新连接失败")
                return False
        except Exception as e:
            logger.error(f"重新连接到服务端时出错: {e}")
            return False
    
    def run(self) -> None:
        """运行应用程序主循环"""
        try:
            if not self.initialized:
                logger.error("应用程序控制器未初始化")
                return
            
            logger.info("Net Manager 启动...")
            
            # 处理开机自启动功能
            self._handle_autostart()
            
            # 连接到服务端
            if not self._connect_to_server():
                logger.error("无法连接到服务端，程序退出")
                return
            
            # 主循环
            logger.info("开始主循环")
            while not self.shutdown_event.is_set():
                try:
                    logger.debug("开始收集系统信息...")
                    
                    # 收集系统信息
                    system_info = self.collector.collect_system_info()
                    
                    # 计算当前系统信息的哈希值
                    current_hash = self._calculate_system_info_hash(system_info)
                    
                    # 比较当前数据与上一次数据是否相同
                    if current_hash != self.last_system_info_hash:
                        logger.info("系统信息发生变化，准备发送到服务端...")
                        
                        # 发送系统信息
                        send_success = self._send_system_info(system_info)
                        
                        if send_success:
                            # 更新上一次的哈希值
                            self.last_system_info_hash = current_hash
                        else:
                            # 如果发送失败，尝试重新连接
                            if self._reconnect_to_server():
                                # 重新连接成功后再次尝试发送
                                if self._send_system_info(system_info):
                                    self.last_system_info_hash = current_hash
                                    logger.info("系统信息已重新发送到服务端")
                                else:
                                    logger.warning("重新发送数据失败")
                    else:
                        logger.debug("系统信息未发生变化，跳过发送")
                    
                    # 等待下次收集周期
                    if self.shutdown_event.wait(self.collect_interval):
                        break
                        
                except Exception as e:
                    logger.error(f"主循环中发生错误: {e}")
                    # 如果是系统性错误，可能需要重新连接
                    if not self.tcp_client or not self.tcp_client.is_connected():
                        if not self._reconnect_to_server():
                            logger.error("重新连接失败，程序退出")
                            break
                    # 继续下一次循环
                    if self.shutdown_event.wait(5):  # 短暂延迟后重试
                        break
            
            logger.info("主循环结束")
            
        except Exception as e:
            logger.error(f"运行应用程序时发生未处理的错误: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """关闭应用程序"""
        try:
            logger.info("正在关闭应用程序...")
            
            # 设置关闭事件
            self.shutdown_event.set()
            
            # 断开TCP连接
            if self.tcp_client:
                self.tcp_client.disconnect()
            
            # 释放单例锁
            self.singleton_manager.release_lock()
            
            logger.info("应用程序已关闭")
        except Exception as e:
            logger.error(f"关闭应用程序时出错: {e}")


# 全局应用程序控制器实例
_app_controller: Optional[AppController] = None


def get_app_controller() -> AppController:
    """获取全局应用程序控制器实例"""
    global _app_controller
    if _app_controller is None:
        _app_controller = AppController()
    return _app_controller