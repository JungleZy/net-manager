#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCP服务端 - 用于与Net Manager客户端建立长连接并接收数据
"""

import socket
import json
import threading
import sys
import os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.core.config import TCP_PORT
from src.core.logger import logger
from src.database import DatabaseManager
from src.models.device_info import DeviceInfo

class TCPServer:
    """TCP服务端，用于与客户端建立长连接"""
    
    def __init__(self, db_manager=None, max_workers=100):
        self.tcp_port = TCP_PORT
        self.clients = set()  # 使用set存储连接的客户端，提高查找效率
        self.client_id_map = {}  # 存储client_id到地址的映射关系
        self.clients_lock = threading.Lock()  # 保护clients集合的锁
        self.running = False
        # 如果传入了数据库管理器实例，则使用它；否则创建新的实例
        self.db_manager = db_manager if db_manager else DatabaseManager()
        # 使用线程池来处理客户端连接，避免为每个客户端创建新线程
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def handle_client(self, client_socket, address):
        """处理客户端连接"""
        logger.info(f"客户端 {address} 已连接")
        
        # 将客户端添加到集合
        with self.clients_lock:
            self.clients.add((client_socket, address))
        
        client_id = None
        try:
            # 首先接收握手消息
            handshake_data = client_socket.recv(1024)  # 握手消息应该很小
            if handshake_data:
                try:
                    handshake_info = json.loads(handshake_data.decode('utf-8'))
                    if handshake_info.get('type') == 'handshake':
                        client_id = handshake_info.get('client_id', 'unknown')
                        logger.info(f"客户端 {address} 握手成功，client_id: {client_id}")
                        # 存储client_id与客户端地址的映射关系
                        with self.clients_lock:
                            self.client_id_map[client_id] = address
                    else:
                        logger.warning(f"客户端 {address} 发送的不是握手消息")
                except json.JSONDecodeError:
                    logger.warning(f"客户端 {address} 发送的握手消息无法解析")
            
            while self.running:
                # 接收数据长度（4字节）
                import struct
                raw_length = self._recv_all(client_socket, 4)
                if not raw_length:
                    break
                    
                # 解析数据长度
                message_length = struct.unpack('!I', raw_length)[0]
                
                # 接收指定长度的数据
                data = self._recv_all(client_socket, message_length)
                if not data:
                    break
                    
                # 异步处理客户端数据，避免阻塞
                # 在提交任务前检查executor是否已关闭
                try:
                    self.executor.submit(self._process_client_data, data, address, client_id)
                except RuntimeError as e:
                    if "cannot schedule new futures after shutdown" in str(e):
                        logger.debug(f"服务器正在关闭，不再处理来自 {address} 的新数据")
                        break
                    else:
                        raise
                    
        except ConnectionResetError:
            logger.info(f"客户端 {address} 断开连接")
        except Exception as e:
            logger.error(f"处理客户端 {address} 数据时出错: {e}")
        finally:
            self._cleanup_client_connection(client_socket, address, client_id)
    
    def _process_client_data(self, data, address, client_id=None):
        """处理来自客户端的数据"""
        # 检查数据是否为空
        if not data:
            logger.debug(f"收到来自 {address} 的空数据包，忽略")
            return
            
        logger.debug(f"收到来自 {address} 的数据，长度: {len(data)} 字节")
        
        try:
            # 解析JSON数据
            json_str = data.decode('utf-8').strip()  # 去除首尾空白字符，包括换行符
            
            # 检查解码后的字符串是否为空
            if not json_str:
                logger.warning(f"收到来自 {address} 的空JSON字符串，忽略")
                return
                
            info = json.loads(json_str)
            
            # 检查是否提供了client_id
            client_id = info.get('client_id')
            if client_id:
                # 根据client_id查询设备信息
                existing_device = self.db_manager.get_device_info_by_client_id(client_id)
                if existing_device:
                    # 如果存在，则使用现有设备的ID进行更新
                    info['id'] = existing_device['id']
                    logger.debug(f"使用现有设备ID更新: {info['id']}")
                else:
                    # 如果不存在，则生成新的ID
                    import uuid
                    info['id'] = str(uuid.uuid4())
                    logger.debug(f"为新设备生成ID: {info['id']}")
            else:
                # 如果没有提供client_id，则生成新的ID
                import uuid
                info['id'] = str(uuid.uuid4())
                logger.debug(f"未提供client_id，生成新ID: {info['id']}")
            
            # 创建DeviceInfo对象用于保存到数据库
            device_info = self._create_device_info_with_id(info)
            
            # 保存到数据库
            self.db_manager.save_device_info(device_info)
            logger.debug("设备信息已保存到数据库")
            
        except json.JSONDecodeError as e:
                # 记录更详细的错误信息，包括有问题的数据片段
                error_msg = f"  无法解析的JSON数据: {e}"
                # 记录数据的前200个字符用于调试（避免日志过大）
                data_preview = json_str[:200] + ("..." if len(json_str) > 200 else "")
                logger.warning(f"{error_msg}。数据预览: {data_preview}")
                logger.debug(f"  JSON解析错误详情: {str(e)}")
                # 记录原始数据的十六进制表示，有助于诊断编码问题
                hex_data = data.hex()[:200] + ("..." if len(data.hex()) > 200 else "")
                logger.debug(f"原始数据(十六进制): {hex_data}")
        except Exception as e:
            logger.error(f"  处理数据时出错: {e}")
    
    def _create_device_info(self, info):
        """创建设备信息对象"""
        
        import uuid
        return DeviceInfo(
            id=str(uuid.uuid4()),  # 生成唯一ID
            client_id=info.get('client_id', ''),  # 客户端唯一标识符
            hostname=info.get('hostname', 'N/A'),  # 主机名
            os_name=info.get('os_name', 'N/A'),  # 操作系统名称
            os_version=info.get('os_version', 'N/A'),  # 操作系统版本
            os_architecture=info.get('os_architecture', 'N/A'),  # 操作系统架构
            machine_type=info.get('machine_type', 'N/A'),   # 机器类型
            services=info.get('services', '[]'),  # 服务信息
            processes=info.get('processes', '[]'),  # 进程信息
            networks=info.get('networks', '[]'),  # 网络信息
            timestamp=info.get('timestamp', 'N/A'),  # 时间戳
            cpu_info=info.get('cpu_info', ''),  # CPU信息
            memory_info=info.get('memory_info', ''),  # 内存信息
            disk_info=info.get('disk_info', ''),  # 磁盘信息
        )
    
    def _create_device_info_with_id(self, info):
        """创建带有指定ID的设备信息对象"""
        return DeviceInfo(
            id=info['id'],  # 使用指定的ID
            client_id=info.get('client_id', ''),  # 客户端唯一标识符
            hostname=info.get('hostname', 'N/A'),  # 主机名
            os_name=info.get('os_name', 'N/A'),  # 操作系统名称
            os_version=info.get('os_version', 'N/A'),  # 操作系统版本
            os_architecture=info.get('os_architecture', 'N/A'),  # 操作系统架构
            machine_type=info.get('machine_type', 'N/A'),   # 机器类型
            services=info.get('services', '[]'),  # 服务信息
            processes=info.get('processes', '[]'),  # 进程信息
            networks=info.get('networks', '[]'),  # 网络信息
            timestamp=info.get('timestamp', 'N/A'),  # 时间戳
            cpu_info=info.get('cpu_info', ''),  # CPU信息
            memory_info=info.get('memory_info', ''),  # 内存信息
            disk_info=info.get('disk_info', ''),  # 磁盘信息
        )
    
    def _process_services_info(self, info):
        """处理服务信息"""
        services_data = info.get('services', '[]')
        try:
            # 如果services_data是字符串，则解析它；否则直接使用
            if isinstance(services_data, str):
                services = json.loads(services_data)
            else:
                services = services_data
            logger.debug(f"  服务数量: {len(services)}")

        except json.JSONDecodeError:
            logger.warning(f"  服务信息无法解析: {services_data}")
    
    def _process_processes_info(self, info):
        """处理进程信息"""
        processes_data = info.get('processes', '[]')
        try:
            # 如果processes_data是字符串，则解析它；否则直接使用
            if isinstance(processes_data, str):
                processes = json.loads(processes_data)
            else:
                processes = processes_data
            logger.debug(f"  进程数量: {len(processes)}")
            
        except json.JSONDecodeError:
            logger.warning(f"  进程信息无法解析: {processes_data}")
    
    def get_client_address(self, client_id):
        """根据client_id获取客户端地址"""
        with self.clients_lock:
            return self.client_id_map.get(client_id)
    
    def _cleanup_client_connection(self, client_socket, address, client_id=None):
        """清理客户端连接"""
        # 移除客户端
        with self.clients_lock:
            self.clients.discard((client_socket, address))
            # 如果有client_id，也从映射中移除
            if client_id and client_id in self.client_id_map:
                del self.client_id_map[client_id]
        client_socket.close()
        logger.info(f"客户端 {address} 连接已关闭")
    
    def _recv_all(self, sock, length):
        """确保接收指定长度的数据"""
        data = b''
        while len(data) < length:
            packet = sock.recv(length - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def start(self):
        """启动TCP服务端"""
        # 创建TCP套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置SO_REUSEADDR选项，允许地址重用
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设置TCP_NODELAY选项，禁用Nagle算法，减少延迟
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        server_address = ('0.0.0.0', self.tcp_port)
        logger.info(f"TCP服务端启动，监听端口 {self.tcp_port}")
        
        try:
            server_socket.bind(server_address)
            # 增加监听队列大小，以处理更多并发连接
            server_socket.listen(128)
            self.running = True
            
            while self.running:
                try:
                    # 设置accept超时，以便能够响应Ctrl+C
                    server_socket.settimeout(1.0)
                    client_socket, address = server_socket.accept()
                    client_socket.settimeout(None)  # 重置客户端套接字超时
                    
                    # 为每个客户端提交到线程池处理
                    # 在提交前检查服务器是否仍在运行
                    if self.running:
                        try:
                            self.executor.submit(self.handle_client, client_socket, address)
                        except RuntimeError as e:
                            if "cannot schedule new futures after shutdown" in str(e):
                                logger.debug("服务器正在关闭，不再接受新连接")
                                client_socket.close()
                                break
                            else:
                                raise
                    
                except socket.timeout:
                    # accept超时，继续循环
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"接受连接时出错: {e}")
                        
        except KeyboardInterrupt:
            logger.info("TCP服务端正在停止...")
        except Exception as e:
            logger.error(f"服务端运行出错: {e}")
        finally:
            self.running = False
            # 关闭所有客户端连接
            with self.clients_lock:
                for client_socket, address in self.clients:
                    try:
                        client_socket.close()
                    except Exception as e:
                        logger.warning(f"关闭客户端连接时出错: {e}")
                self.clients.clear()
                # 清空client_id映射
                self.client_id_map.clear()
            server_socket.close()
            # 关闭线程池
            self.executor.shutdown(wait=True)
            logger.info("TCP服务端已停止")
