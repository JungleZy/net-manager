#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备信息管理器 - 用于管理设备信息的数据库操作
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple

from src.core.logger import logger
from src.models.system_info import SystemInfo
from src.database.db_exceptions import (
    DatabaseError, 
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError
)
from src.database.managers.base_manager import BaseDatabaseManager


class DeviceManager(BaseDatabaseManager):
    """设备信息管理器类
    
    提供设备信息的增删改查操作。
    """
    
    def __init__(self, db_path: str = "net_manager_server.db"):
        """
        初始化设备信息管理器
        
        Args:
            db_path: 数据库文件路径
        """
        super().__init__(db_path)
        self.init_tables()

    def init_tables(self) -> None:
        """初始化设备信息表结构
        
        创建设备信息表（如果不存在）。
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 创建设备信息表，使用mac_address作为主键
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS devices_info (
                        mac_address TEXT PRIMARY KEY,
                        hostname TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        gateway TEXT,
                        netmask TEXT,
                        services TEXT NOT NULL,
                        processes TEXT NOT NULL,
                        client_id TEXT,
                        os_name TEXT,
                        os_version TEXT,
                        os_architecture TEXT,
                        machine_type TEXT,
                        type TEXT,  -- 设备类型字段（计算机、交换机、服务器等）
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("设备信息表初始化成功")
        except Exception as e:
            logger.error(f"设备信息表初始化失败: {e}")
            raise DatabaseError(f"设备信息表初始化失败: {e}") from e

    def save_system_info(self, system_info: SystemInfo) -> None:
        """
        保存设备信息到数据库
        
        使用mac_address作为主键进行更新或插入操作。
        注意：通过TCP更新数据时不更新type字段，type字段只能通过API手动设置。
        
        Args:
            system_info: SystemInfo对象
            
        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        try:
            with self.db_lock:  # 使用锁保护数据库访问
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 将services和processes转换为JSON字符串
                    services_json = json.dumps(system_info.services) if system_info.services else '[]'
                    processes_json = json.dumps(system_info.processes) if system_info.processes else '[]'
                    
                    # 使用INSERT OR REPLACE语句，如果mac_address已存在则更新，否则插入新记录
                    cursor.execute('''
                        INSERT OR REPLACE INTO devices_info 
                        (mac_address, hostname, ip_address, gateway, netmask, services, processes, 
                         client_id, os_name, os_version, os_architecture, machine_type, type, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT type FROM devices_info WHERE mac_address = ?), ''), 
                            ?)
                    ''', (
                        system_info.mac_address, 
                        system_info.hostname, 
                        system_info.ip_address, 
                        system_info.gateway, 
                        system_info.netmask, 
                        services_json,
                        processes_json,
                        system_info.client_id,
                        system_info.os_name, 
                        system_info.os_version, 
                        system_info.os_architecture, 
                        system_info.machine_type, 
                        system_info.mac_address,  # 用于子查询
                        system_info.timestamp
                    ))
                    
                    conn.commit()
                    # logger.info(f"系统信息保存成功，MAC地址: {system_info.mac_address}")
        except Exception as e:
            logger.error(f"保存系统信息失败: {e}")
            raise DatabaseQueryError(f"保存系统信息失败: {e}") from e

    def get_all_system_info(self) -> List[Dict[str, Any]]:
        """
        获取所有设备信息
        
        Returns:
            包含所有设备信息的字典列表，按时间戳降序排列
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT mac_address, hostname, ip_address, gateway, netmask, services, processes, 
                           client_id, os_name, os_version, os_architecture, machine_type, type, timestamp
                    FROM devices_info
                    ORDER BY timestamp DESC
                ''')
                
                rows = cursor.fetchall()
                
                # 转换为字典列表
                result = []
                for row in rows:
                    # 处理services字段
                    services_data = row[5]
                    if services_data:
                        try:
                            services = json.loads(services_data)
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析services数据，使用空列表: {services_data}")
                            services = []
                    else:
                        services = []
                    
                    # 处理processes字段
                    processes_data = row[6]
                    if processes_data:
                        try:
                            processes = json.loads(processes_data)
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析processes数据，使用空列表: {processes_data}")
                            processes = []
                    else:
                        processes = []
                    
                    result.append({
                        'mac_address': row[0],
                        'hostname': row[1],
                        'ip_address': row[2],
                        'gateway': row[3],
                        'netmask': row[4],
                        'services': services,
                        'processes': processes,
                        'client_id': row[7],
                        'os_name': row[8],
                        'os_version': row[9],
                        'os_architecture': row[10],
                        'machine_type': row[11],
                        'type': row[12],
                        'timestamp': row[13]
                    })
                
                return result
        except Exception as e:
            logger.error(f"查询所有系统信息失败: {e}")
            raise DatabaseQueryError(f"查询所有系统信息失败: {e}") from e

    def get_system_info_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """
        根据MAC地址获取设备信息
        
        Args:
            mac_address: MAC地址
            
        Returns:
            设备信息字典，如果未找到则返回None
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT mac_address, hostname, ip_address, gateway, netmask, services, processes, 
                           client_id, os_name, os_version, os_architecture, machine_type, type, timestamp
                    FROM devices_info
                    WHERE mac_address = ?
                ''', (mac_address,))
                
                row = cursor.fetchone()
                
                if row:
                    # 处理services字段
                    services_data = row[5]
                    if services_data:
                        try:
                            services = json.loads(services_data)
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析services数据，使用空列表: {services_data}")
                            services = []
                    else:
                        services = []
                    
                    # 处理processes字段
                    processes_data = row[6]
                    if processes_data:
                        try:
                            processes = json.loads(processes_data)
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析processes数据，使用空列表: {processes_data}")
                            processes = []
                    else:
                        processes = []
                    
                    return {
                        'mac_address': row[0],
                        'hostname': row[1],
                        'ip_address': row[2],
                        'gateway': row[3],
                        'netmask': row[4],
                        'services': services,
                        'processes': processes,
                        'client_id': row[7],
                        'os_name': row[8],
                        'os_version': row[9],
                        'os_architecture': row[10],
                        'machine_type': row[11],
                        'type': row[12],
                        'timestamp': row[13]
                    }
                return None
        except Exception as e:
            logger.error(f"根据MAC地址查询系统信息失败: {e}")
            raise DatabaseQueryError(f"根据MAC地址查询系统信息失败: {e}") from e

    def update_system_type(self, mac_address: str, device_type: str) -> bool:
        """
        更新设备类型
        
        Args:
            mac_address: MAC地址
            device_type: 设备类型
            
        Returns:
            更新成功返回True，设备不存在返回False
            
        Raises:
            DatabaseQueryError: 更新失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查系统是否存在
                cursor.execute('''
                    SELECT COUNT(*) FROM devices_info WHERE mac_address = ?
                ''', (mac_address,))
                
                count = cursor.fetchone()[0]
                if count == 0:
                    return False
                
                # 更新设备类型
                cursor.execute('''
                    UPDATE devices_info SET type = ? WHERE mac_address = ?
                ''', (device_type, mac_address))
                
                conn.commit()
                logger.info(f"设备类型更新成功，MAC地址: {mac_address}, 类型: {device_type}")
                return True
        except Exception as e:
            logger.error(f"更新系统设备类型失败: {e}")
            raise DatabaseQueryError(f"更新系统设备类型失败: {e}") from e

    def create_device(self, device_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        创建新设备
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 创建失败时抛出
            DeviceAlreadyExistsError: 设备已存在时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查设备是否已存在
                cursor.execute('''
                    SELECT COUNT(*) FROM devices_info WHERE mac_address = ?
                ''', (device_data['mac_address'],))
                
                count = cursor.fetchone()[0]
                if count > 0:
                    raise DeviceAlreadyExistsError(f"设备MAC地址已存在: {device_data['mac_address']}")
                
                # 插入新设备信息
                cursor.execute('''
                    INSERT INTO devices_info (
                        mac_address, hostname, ip_address, gateway, netmask, 
                        services, processes, client_id, os_name, os_version, 
                        os_architecture, machine_type, type, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    device_data['mac_address'],
                    device_data['hostname'],
                    device_data['ip_address'],
                    device_data.get('gateway', ''),
                    device_data.get('netmask', ''),
                    json.dumps([]),  # services
                    json.dumps([]),  # processes
                    '',  # client_id
                    device_data.get('os_name', ''),
                    device_data.get('os_version', ''),
                    device_data.get('os_architecture', ''),
                    device_data.get('machine_type', ''),
                    device_data.get('type', '')
                ))
                
                conn.commit()
                logger.info(f"设备创建成功，MAC地址: {device_data['mac_address']}")
                return True, "设备创建成功"
        except DeviceAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"创建设备失败: {e}")
            raise DatabaseQueryError(f"创建设备失败: {e}") from e

    def update_device(self, device_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新设备信息
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 更新失败时抛出
            DeviceNotFoundError: 设备不存在时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查设备是否存在
                cursor.execute('''
                    SELECT COUNT(*) FROM devices_info WHERE mac_address = ?
                ''', (device_data['mac_address'],))
                
                count = cursor.fetchone()[0]
                if count == 0:
                    raise DeviceNotFoundError(f"设备不存在: {device_data['mac_address']}")
                
                # 更新设备信息
                cursor.execute('''
                    UPDATE devices_info SET 
                        hostname = ?, ip_address = ?, gateway = ?, netmask = ?,
                        os_name = ?, os_version = ?, os_architecture = ?, 
                        machine_type = ?, type = ?
                    WHERE mac_address = ?
                ''', (
                    device_data['hostname'],
                    device_data['ip_address'],
                    device_data.get('gateway', ''),
                    device_data.get('netmask', ''),
                    device_data.get('os_name', ''),
                    device_data.get('os_version', ''),
                    device_data.get('os_architecture', ''),
                    device_data.get('machine_type', ''),
                    device_data.get('type', ''),
                    device_data['mac_address']
                ))
                
                conn.commit()
                logger.info(f"设备更新成功，MAC地址: {device_data['mac_address']}")
                return True, "设备更新成功"
        except DeviceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新设备失败: {e}")
            raise DatabaseQueryError(f"更新设备失败: {e}") from e

    def delete_device(self, mac_address: str) -> Tuple[bool, str]:
        """
        删除设备
        
        Args:
            mac_address: MAC地址
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 删除失败时抛出
            DeviceNotFoundError: 设备不存在时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查设备是否存在
                cursor.execute('''
                    SELECT COUNT(*) FROM devices_info WHERE mac_address = ?
                ''', (mac_address,))
                
                count = cursor.fetchone()[0]
                if count == 0:
                    raise DeviceNotFoundError(f"设备不存在: {mac_address}")
                
                # 删除设备
                cursor.execute('''
                    DELETE FROM devices_info WHERE mac_address = ?
                ''', (mac_address,))
                
                conn.commit()
                logger.info(f"设备删除成功，MAC地址: {mac_address}")
                return True, "设备删除成功"
        except DeviceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除设备失败: {e}")
            raise DatabaseQueryError(f"删除设备失败: {e}") from e

    def get_device_count(self) -> int:
        """
        获取设备总数
        
        Returns:
            设备总数
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM devices_info')
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"查询设备总数失败: {e}")
            raise DatabaseQueryError(f"查询设备总数失败: {e}") from e