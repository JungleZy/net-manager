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
import sqlite3
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config import TCP_PORT
from src.logger import logger

class SystemInfo:
    """系统信息模型"""
    def __init__(self, hostname, ip_address, mac_address, services, processes, timestamp):
        self.hostname = hostname
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.services = services  # 存储为JSON字符串
        self.processes = processes  # 存储为JSON字符串
        self.timestamp = timestamp

class DatabaseManager:
    """数据库管理器"""
    def __init__(self, db_path="net_manager_server.db"):
        self.db_path = Path(db_path)
        self.init_db()
        # 使用连接池来优化数据库访问
        self.db_lock = threading.Lock()
    
    def init_db(self):
        """初始化数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建系统信息表，使用mac_address作为主键
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_info (
                    mac_address TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    services TEXT NOT NULL,
                    processes TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def save_system_info(self, system_info):
        """保存系统信息到数据库，使用mac_address作为主键进行更新或插入"""
        try:
            # 使用锁保护数据库访问
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 使用INSERT OR REPLACE语句，如果mac_address已存在则更新，否则插入新记录
                cursor.execute('''
                    INSERT OR REPLACE INTO system_info (mac_address, hostname, ip_address, services, processes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (system_info.mac_address, system_info.hostname, system_info.ip_address, 
                      system_info.services, system_info.processes, system_info.timestamp))
                
                conn.commit()
                conn.close()
            logger.info(f"系统信息保存成功，MAC地址: {system_info.mac_address}")
        except Exception as e:
            logger.error(f"保存系统信息失败: {e}")
            raise

class TCPServer:
    """TCP服务端，用于与客户端建立长连接"""
    
    def __init__(self, max_workers=100):
        self.tcp_port = TCP_PORT
        self.clients = set()  # 使用set存储连接的客户端，提高查找效率
        self.clients_lock = threading.Lock()  # 保护clients集合的锁
        self.running = False
        self.db_manager = DatabaseManager()  # 初始化数据库管理器
        # 使用线程池来处理客户端连接，避免为每个客户端创建新线程
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def handle_client(self, client_socket, address):
        """处理客户端连接"""
        logger.info(f"客户端 {address} 已连接")
        
        # 将客户端添加到集合
        with self.clients_lock:
            self.clients.add((client_socket, address))
        
        try:
            while self.running:
                # 接收数据
                data = client_socket.recv(65536)  # 64KB缓冲区
                if not data:
                    break
                    
                # 异步处理客户端数据，避免阻塞
                self.executor.submit(self._process_client_data, data, address)
                    
        except ConnectionResetError:
            logger.info(f"客户端 {address} 断开连接")
        except Exception as e:
            logger.error(f"处理客户端 {address} 数据时出错: {e}")
        finally:
            self._cleanup_client_connection(client_socket, address)
    
    def _process_client_data(self, data, address):
        """处理来自客户端的数据"""
        logger.debug(f"收到来自 {address} 的数据:")
        
        try:
            # 解析JSON数据
            json_str = data.decode('utf-8')
            info = json.loads(json_str)
            
            # 创建SystemInfo对象用于保存到数据库
            system_info = self._create_system_info(info)
            
            # 保存到数据库
            self.db_manager.save_system_info(system_info)
            logger.debug("系统信息已保存到数据库")
            
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
    
    def _create_system_info(self, info):
        """创建系统信息对象"""
        return SystemInfo(
            hostname=info.get('hostname', 'N/A'),
            ip_address=info.get('ip_address', 'N/A'),
            mac_address=info.get('mac_address', 'N/A'),
            services=info.get('services', '[]'),
            processes=info.get('processes', '[]'),
            timestamp=info.get('timestamp', 'N/A')
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
    
    def _cleanup_client_connection(self, client_socket, address):
        """清理客户端连接"""
        # 移除客户端
        with self.clients_lock:
            self.clients.discard((client_socket, address))
        client_socket.close()
        logger.info(f"客户端 {address} 连接已关闭")
    
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
                    self.executor.submit(self.handle_client, client_socket, address)
                    
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
            server_socket.close()
            # 关闭线程池
            self.executor.shutdown(wait=True)
            logger.info("TCP服务端已停止")

if __name__ == "__main__":
    # 为支持500个客户端连接，增加线程池大小
    tcp_server = TCPServer(max_workers=200)
    tcp_server.start()