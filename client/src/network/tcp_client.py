#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCP客户端模块
负责与服务端建立TCP连接，处理数据传输和命令接收
"""

import socket
import json
import threading
import time
import uuid
from typing import Optional, Dict, Any, Callable
from datetime import datetime

# 第三方库导入
# 无

# 本地应用/库导入
# 延迟导入config，避免在获取客户端锁之前加载
# from src.config_module.config import config
from src.exceptions.exceptions import NetworkConnectionError, NetworkDiscoveryError
from src.utils.logger import get_logger
from src.system.system_collector import SystemCollector


class TCPClient:
    """TCP客户端类，负责与服务端通信"""
    
    def __init__(self):
        """初始化TCP客户端"""
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.reconnecting = False
        self.client_id = str(uuid.uuid4())
        self.stop_event = threading.Event()
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.receive_thread: Optional[threading.Thread] = None
        self.command_handlers: Dict[str, Callable] = {}
        self.logger = get_logger()
        self.system_collector = SystemCollector()
        self.server_ip: Optional[str] = None
        self.server_port: Optional[int] = None
        
        # 注册默认命令处理器
        self.register_command_handler("disconnect", self._handle_disconnect_command)
    
    def register_command_handler(self, command: str, handler: Callable) -> None:
        """
        注册命令处理器
        
        Args:
            command (str): 命令名称
            handler (Callable): 处理函数
        """
        self.command_handlers[command] = handler
        self.logger.debug(f"注册命令处理器: {command}")
    
    def discover_server(self) -> tuple:
        """
        通过UDP广播发现服务端
        
        Returns:
            tuple: (server_ip, server_port)
            
        Raises:
            NetworkDiscoveryError: 服务发现失败
        """
        return self._discover_server()
        
    def _discover_server(self) -> tuple:
        """
        通过UDP广播发现服务端
        
        Returns:
            tuple: (server_ip, server_port)
            
        Raises:
            NetworkDiscoveryError: 服务发现失败
        """
        # 延迟导入config
        from src.config_module.config import config
        broadcast_address = config.get_server_broadcast_address()
        broadcast_port = config.get_server_broadcast_port()
        try:
            # 创建UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_socket.settimeout(5.0)  # 5秒超时
            
            # 广播发现消息
            discovery_message = {
                "type": "discovery",
                "timestamp": datetime.now().isoformat()
            }
            
            broadcast_address = config.get_server_broadcast_address()
            broadcast_port = config.get_server_broadcast_port()
            
            # 初始化重试计数器
            retry_count = 0
            
            # 发送服务发现广播并等待响应
            while not self.stop_event.is_set():
                if retry_count == 0:
                    # 首次发送
                    self.logger.info(f"发送服务发现广播到 {broadcast_address}:{broadcast_port}")
                else:
                    # 超时重试
                    self.logger.warning(f"服务发现超时，正在进行第{retry_count}次重试")
                
                udp_socket.sendto(json.dumps(discovery_message).encode('utf-8'), (broadcast_address, broadcast_port))
                
                try:
                    data, server_addr = udp_socket.recvfrom(1024)
                    response = json.loads(data.decode('utf-8'))
                    
                    if response.get("type") == "discovery_response":
                        server_ip = server_addr[0]
                        # 确保server_port是整数类型
                        server_port = response.get("tcp_port")
                        if isinstance(server_port, str):
                            server_port = int(server_port)
                        udp_socket.close()
                        return server_ip, server_port
                except socket.timeout:
                    retry_count += 1
                    continue  # 继续下一次循环进行重试
                except Exception as e:
                    self.logger.error(f"服务发现过程中出错: {e}")
                    break
            
            udp_socket.close()
            raise NetworkDiscoveryError("无法发现服务端")
        except Exception as e:
            self.logger.error(f"服务发现失败: {e}")
            raise NetworkDiscoveryError(f"服务发现失败: {e}")
    
    def connect(self, server_address: Optional[tuple] = None) -> bool:
        """
        连接到服务端
        
        Args:
            server_address (Optional[tuple]): 服务端地址 (ip, port)，如果未提供则自动发现
            
        Returns:
            bool: 连接是否成功
        """
        try:
            if self.connected:
                self.logger.warning("客户端已经连接到服务端")
                return True
            
            # 如果提供了服务端地址，则直接使用；否则发现服务端
            if server_address:
                server_ip, server_port = server_address
            else:
                # 发现服务端
                server_ip, server_port = self._discover_server()
            
            # 创建TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)  # 10秒连接超时
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 启用TCP keepalive
            
            # 连接到服务端
            self.logger.info(f"正在连接到服务端 {server_ip}:{server_port}")
            self.socket.connect((server_ip, server_port))
            
            # 执行握手
            if self._perform_handshake():
                # 保存服务端地址以便重连时使用
                self.server_ip = server_ip
                self.server_port = server_port
                self.connected = True
                self.reconnecting = False
                
                # 启动接收线程
                self.receive_thread = threading.Thread(target=self._receive_data, daemon=True)
                self.receive_thread.start()
                
                return True
            else:
                self.logger.error("握手失败")
                self._close_socket()
                return False
        except NetworkDiscoveryError:
            self.logger.error("服务发现失败，无法连接到服务端")
            return False
        except Exception as e:
            self.logger.error(f"连接到服务端失败: {e}")
            self._close_socket()
            return False
    
    def _perform_handshake(self) -> bool:
        """
        执行与服务端的握手过程
        
        Returns:
            bool: 握手是否成功
        """
        try:
            # 发送握手消息
            handshake_message = {
                "type": "handshake",
                "client_id": self.client_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.socket.send(json.dumps(handshake_message).encode('utf-8'))
            
            # 等待服务端响应
            self.socket.settimeout(10.0)
            
            self.logger.debug("握手成功")
            return True
        except Exception as e:
            self.logger.error(f"握手过程中出错: {e}")
            return False
    
    def _receive_data(self) -> None:
        """接收来自服务端的数据"""
        try:
            self.socket.settimeout(None)  # 接收数据时不设置超时
            buffer = ""
            
            while not self.stop_event.is_set() and self.connected:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        self.logger.warning("服务端关闭了连接")
                        self._handle_disconnect()
                        break
                    
                    # 处理接收到的数据
                    buffer += data.decode('utf-8')
                    messages = buffer.split('\n')
                    buffer = messages[-1]  # 最后一个可能是不完整的消息
                    
                    # 处理完整的消息
                    for message_str in messages[:-1]:
                        if message_str:
                            try:
                                message = json.loads(message_str)
                                self._handle_message(message)
                            except json.JSONDecodeError:
                                self.logger.warning(f"收到无效的JSON消息: {message_str}")
                except socket.timeout:
                    # 这里不应该发生超时，因为我们设置了None，但为了安全起见还是处理一下
                    continue
                except Exception as e:
                    if not self.stop_event.is_set():
                        self.logger.error(f"接收数据时出错: {e}")
                        self._handle_disconnect()
                    break
        except Exception as e:
            if not self.stop_event.is_set():
                self.logger.error(f"接收数据线程出错: {e}")
                self._handle_disconnect()
    
    def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        处理接收到的消息
        
        Args:
            message (Dict[str, Any]): 消息内容
        """
        try:
            msg_type = message.get("type")
            if msg_type == "command":
                command = message.get("command")
                if command in self.command_handlers:
                    self.command_handlers[command](message)
                else:
                    self.logger.warning(f"未知命令: {command}")
            else:
                self.logger.debug(f"收到未处理的消息类型: {msg_type}")
        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}")
    
    def _handle_disconnect_command(self, message: Dict[str, Any]) -> None:
        """
        处理服务端发送的断开连接命令
        
        Args:
            message (Dict[str, Any]): 断开连接命令消息
        """
        self.logger.info("收到服务端断开连接命令")
        self._handle_disconnect()
    
    def send_system_info(self) -> bool:
        """
        发送系统信息到服务端
        
        Returns:
            bool: 发送是否成功
        """
        try:
            if not self.connected:
                self.logger.warning("客户端未连接，无法发送系统信息")
                return False
            
            # 收集系统信息
            system_info = self.system_collector.collect_system_info()
            
            # 构造消息
            info_dict = {
                "hostname": system_info.hostname,
                "ip_address": system_info.ip_address,
                "mac_address": system_info.mac_address,
                "gateway": system_info.gateway,
                "netmask": system_info.netmask,
                "services": system_info.services,  # 这已经是JSON格式的字符串
                "processes": system_info.processes,  # 这已经是JSON格式的字符串
                "os_name": system_info.os_name,  # 操作系统名称
                "os_version": system_info.os_version,  # 操作系统版本
                "os_architecture": system_info.os_architecture,  # 操作系统架构
                "machine_type": system_info.machine_type,  # 机器类型
                "timestamp": system_info.timestamp,
                "client_id": system_info.client_id  # 客户端唯一标识符
            }
            message = json.dumps(info_dict, ensure_ascii=False)
            # 验证数据不为空
            if not message:
                self.logger.error("要发送的数据为空")
                return False
            
            # 验证数据长度
            message_bytes = message.encode('utf-8')
            if len(message_bytes) == 0:
                self.logger.error("要发送的字节数据为空")
                return False
            # 先发送数据长度（4字节），再发送数据内容
            import struct
            length_prefix = struct.pack('!I', len(message_bytes))  # 网络字节序
            self.socket.sendall(length_prefix + message_bytes)
            return True
        except Exception as e:
            self.logger.error(f"发送系统信息失败: {e}")
            if not self.stop_event.is_set():
                self._handle_disconnect()
            return False
    
    def disconnect(self) -> None:
        """断开与服务端的连接"""
        self.logger.info("正在断开与服务端的连接")
        self.stop_event.set()
        
        # 等待线程结束
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=5)
        
        # 发送断开连接消息
        try:
            if self.socket and self.connected:
                disconnect_message = {
                    "type": "disconnect",
                    "client_id": self.client_id,
                    "timestamp": datetime.now().isoformat()
                }
                self.socket.send((json.dumps(disconnect_message) + '\n').encode('utf-8'))
        except Exception as e:
            self.logger.error(f"发送断开连接消息失败: {e}")
        
        # 关闭socket
        self._close_socket()
        self.connected = False
        self.logger.info("已断开与服务端的连接")
    
    def _handle_disconnect(self) -> None:
        """处理连接断开"""
        if self.connected:
            self.logger.warning("与服务端的连接已断开")
            self.connected = False
            
            # 尝试重连
            if not self.reconnecting:
                self.reconnecting = True
                threading.Thread(target=self._reconnect, daemon=True).start()
    
    def _reconnect(self) -> None:
        """重新连接到服务端"""
        self.logger.info("开始重新连接到服务端")
        reconnect_delay = 5  # 初始重连延迟5秒
        
        while not self.stop_event.is_set():
            try:
                time.sleep(reconnect_delay)
                
                # 检查是否有已知的服务端地址
                if self.server_ip and self.server_port:
                    # 尝试连接，传递之前已知的服务端地址以避免重新发现
                    if self.connect((self.server_ip, self.server_port)):
                        self.logger.info("重新连接成功")
                        self.reconnecting = False
                        return
                    else:
                        self.logger.warning(f"重新连接失败，{reconnect_delay}秒后重试")
                        # 指数退避，最大延迟60秒
                        reconnect_delay = min(reconnect_delay * 2, 60)
                else:
                    # 如果没有已知的服务端地址，则进行完整的服务发现和连接过程
                    if self.connect():
                        self.logger.info("重新连接成功")
                        self.reconnecting = False
                        return
                    else:
                        self.logger.warning(f"重新连接失败，{reconnect_delay}秒后重试")
                        # 指数退避，最大延迟60秒
                        reconnect_delay = min(reconnect_delay * 2, 60)
            except Exception as e:
                self.logger.error(f"重连过程中出错: {e}")
                reconnect_delay = min(reconnect_delay * 2, 60)
    
    def _close_socket(self) -> None:
        """关闭socket连接"""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except Exception as e:
            self.logger.error(f"关闭socket时出错: {e}")
    
    def is_connected(self) -> bool:
        """
        检查客户端是否连接到服务端
        
        Returns:
            bool: 是否连接
        """
        return self.connected


# 全局TCP客户端实例
_tcp_client: Optional[TCPClient] = None
_tcp_client_lock = threading.Lock()


def get_tcp_client() -> TCPClient:
    """
    获取全局TCP客户端实例（单例模式）
    
    Returns:
        TCPClient: TCP客户端实例
    """
    global _tcp_client
    if _tcp_client is None:
        with _tcp_client_lock:
            if _tcp_client is None:
                _tcp_client = TCPClient()
    return _tcp_client


def initialize_tcp_client() -> TCPClient:
    """
    初始化TCP客户端
    
    Returns:
        TCPClient: 初始化的TCP客户端实例
    """
    global _tcp_client
    with _tcp_client_lock:
        if _tcp_client is None:
            _tcp_client = TCPClient()
    return _tcp_client
