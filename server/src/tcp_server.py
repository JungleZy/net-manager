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
    
    def __init__(self):
        self.tcp_port = TCP_PORT
        self.clients = []  # 存储连接的客户端
        self.running = False
        self.db_manager = DatabaseManager()  # 初始化数据库管理器
        
    def handle_client(self, client_socket, address):
        """处理客户端连接"""
        logger.info(f"客户端 {address} 已连接")
        
        try:
            while self.running:
                # 接收数据
                data = client_socket.recv(65536)  # 64KB缓冲区
                if not data:
                    break
                    
                receive_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"收到来自 {address} 的数据:")
                
                try:
                    # 解析JSON数据
                    info = json.loads(data.decode('utf-8'))
                    logger.info(f"  主机名: {info.get('hostname', 'N/A')}")
                    logger.info(f"  IP地址: {info.get('ip_address', 'N/A')}")
                    logger.info(f"  MAC地址: {info.get('mac_address', 'N/A')}")
                    logger.info(f"  时间戳: {info.get('timestamp', 'N/A')}")
                    
                    # 创建SystemInfo对象用于保存到数据库
                    system_info = SystemInfo(
                        hostname=info.get('hostname', 'N/A'),
                        ip_address=info.get('ip_address', 'N/A'),
                        mac_address=info.get('mac_address', 'N/A'),
                        services=info.get('services', '[]'),
                        processes=info.get('processes', '[]'),
                        timestamp=info.get('timestamp', 'N/A')
                    )
                    
                    # 保存到数据库
                    self.db_manager.save_system_info(system_info)
                    logger.info("系统信息已保存到数据库")
                    
                    # 解析服务信息
                    services_data = info.get('services', '[]')
                    try:
                        # 如果services_data是字符串，则解析它；否则直接使用
                        if isinstance(services_data, str):
                            services = json.loads(services_data)
                        else:
                            services = services_data
                        logger.info(f"  服务数量: {len(services)}")
                        
                        # 显示前5个服务作为示例
                        logger.info("  服务列表 (前5个):")
                        for i, service in enumerate(services[:5]):
                            logger.info(f"    {i+1}. {service.get('protocol', 'N/A')} - {service.get('local_address', 'N/A')} - {service.get('status', 'N/A')}")
                        if len(services) > 5:
                            logger.info(f"    ... 还有 {len(services) - 5} 个服务")
                    except json.JSONDecodeError:
                        logger.warning(f"  服务信息无法解析: {services_data}")
                    
                    # 解析进程信息
                    processes_data = info.get('processes', '[]')
                    try:
                        # 如果processes_data是字符串，则解析它；否则直接使用
                        if isinstance(processes_data, str):
                            processes = json.loads(processes_data)
                        else:
                            processes = processes_data
                        logger.info(f"  进程数量: {len(processes)}")
                        
                        # 显示前5个进程作为示例
                        logger.info("  进程列表 (前5个):")
                        for i, process in enumerate(processes[:5]):
                            logger.info(f"    {i+1}. PID:{process.get('pid', 'N/A')} NAME:{process.get('name', 'N/A')} CPU:{process.get('cpu_percent', 0.0)}% MEM:{process.get('memory_percent', 0.0)}%")
                        if len(processes) > 5:
                            logger.info(f"    ... 还有 {len(processes) - 5} 个进程")
                    except json.JSONDecodeError:
                        logger.warning(f"  进程信息无法解析: {processes_data}")
                    
                    logger.info("-" * 50)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"  无法解析的JSON数据: {data.decode('utf-8')}")
                    logger.debug(f"  JSON解析错误详情: {str(e)}")
                except Exception as e:
                    logger.error(f"  处理数据时出错: {e}")
                    
        except ConnectionResetError:
            logger.info(f"客户端 {address} 断开连接")
        except Exception as e:
            logger.error(f"处理客户端 {address} 数据时出错: {e}")
        finally:
            # 移除客户端
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            logger.info(f"客户端 {address} 连接已关闭")
    
    def start(self):
        """启动TCP服务端"""
        # 创建TCP套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置SO_REUSEADDR选项，允许地址重用
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_address = ('0.0.0.0', self.tcp_port)
        logger.info(f"TCP服务端启动，监听端口 {self.tcp_port}...")
        logger.info("按Ctrl+C停止服务")
        
        try:
            server_socket.bind(server_address)
            server_socket.listen(5)  # 最多允许5个连接排队
            self.running = True
            
            while self.running:
                try:
                    # 设置accept超时，以便能够响应Ctrl+C
                    server_socket.settimeout(1.0)
                    client_socket, address = server_socket.accept()
                    client_socket.settimeout(None)  # 重置客户端套接字超时
                    
                    # 将客户端添加到列表
                    self.clients.append(client_socket)
                    
                    # 为每个客户端创建一个线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True  # 设置为守护线程
                    client_thread.start()
                    
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
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            server_socket.close()
            logger.info("TCP服务端已停止")

if __name__ == "__main__":
    tcp_server = TCPServer()
    tcp_server.start()