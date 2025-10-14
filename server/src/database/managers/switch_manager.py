#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交换机信息管理器 - 用于管理交换机配置信息的数据库操作
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple

from src.core.logger import logger
from src.models.switch_info import SwitchInfo
from src.database.db_exceptions import (
    DatabaseError, 
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError
)
from src.database.managers.base_manager import BaseDatabaseManager


class SwitchManager(BaseDatabaseManager):
    """交换机信息管理器类
    
    提供交换机配置信息的增删改查操作。
    """
    
    def __init__(self, db_path: str = "net_manager_server.db"):
        """
        初始化交换机信息管理器
        
        Args:
            db_path: 数据库文件路径
        """
        super().__init__(db_path)
        self.init_tables()

    def init_tables(self) -> None:
        """初始化交换机信息表结构
        
        创建交换机配置表（如果不存在）。
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 创建交换机配置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS switch_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL UNIQUE,
                        snmp_version TEXT NOT NULL,
                        community TEXT,
                        user TEXT,
                        auth_key TEXT,
                        auth_protocol TEXT,
                        priv_key TEXT,
                        priv_protocol TEXT,
                        description TEXT,
                        device_name TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("交换机信息表初始化成功")
        except Exception as e:
            logger.error(f"交换机信息表初始化失败: {e}")
            raise DatabaseError(f"交换机信息表初始化失败: {e}") from e

    def add_switch(self, switch_info: 'SwitchInfo') -> Tuple[bool, str]:
        """
        添加新的交换机配置
        
        Args:
            switch_info: SwitchInfo对象
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
            DeviceAlreadyExistsError: 交换机IP已存在时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查交换机是否已存在（通过IP地址）
                cursor.execute('''
                    SELECT COUNT(*) FROM switch_info WHERE ip = ?
                ''', (switch_info.ip,))
                
                count = cursor.fetchone()[0]
                if count > 0:
                    raise DeviceAlreadyExistsError(f"交换机IP地址已存在: {switch_info.ip}")
                
                # 插入新的交换机配置
                cursor.execute('''
                    INSERT INTO switch_info (
                        ip, snmp_version, community, user, auth_key, auth_protocol,
                        priv_key, priv_protocol, description, device_name, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ''', (
                    switch_info.ip,
                    switch_info.snmp_version,
                    switch_info.community,
                    switch_info.user,
                    switch_info.auth_key,
                    switch_info.auth_protocol,
                    switch_info.priv_key,
                    switch_info.priv_protocol,
                    switch_info.description,
                    switch_info.device_name
                ))
                
                conn.commit()
                logger.info(f"交换机配置添加成功，IP地址: {switch_info.ip}")
                return True, "交换机配置添加成功"
        except DeviceAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"添加交换机配置失败: {e}")
            raise DatabaseQueryError(f"添加交换机配置失败: {e}") from e

    def update_switch(self, switch_info: 'SwitchInfo') -> Tuple[bool, str]:
        """
        更新交换机配置
        
        Args:
            switch_info: SwitchInfo对象
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 更新失败时抛出
            DeviceNotFoundError: 交换机不存在时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查交换机是否存在
                cursor.execute('''
                    SELECT COUNT(*) FROM switch_info WHERE id = ?
                ''', (switch_info.id,))
                
                count = cursor.fetchone()[0]
                if count == 0:
                    raise DeviceNotFoundError(f"交换机不存在，ID: {switch_info.id}")
                
                # 更新交换机配置
                cursor.execute('''
                    UPDATE switch_info SET 
                        ip = ?, snmp_version = ?, community = ?, user = ?, 
                        auth_key = ?, auth_protocol = ?, priv_key = ?, 
                        priv_protocol = ?, description = ?, device_name = ?, updated_at = datetime('now')
                    WHERE id = ?
                ''', (
                    switch_info.ip,
                    switch_info.snmp_version,
                    switch_info.community,
                    switch_info.user,
                    switch_info.auth_key,
                    switch_info.auth_protocol,
                    switch_info.priv_key,
                    switch_info.priv_protocol,
                    switch_info.description,
                    switch_info.device_name,
                    switch_info.id
                ))
                
                conn.commit()
                logger.info(f"交换机配置更新成功，ID: {switch_info.id}")
                return True, "交换机配置更新成功"
        except DeviceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新交换机配置失败: {e}")
            raise DatabaseQueryError(f"更新交换机配置失败: {e}") from e

    def delete_switch(self, switch_id: int) -> Tuple[bool, str]:
        """
        删除交换机配置
        
        Args:
            switch_id: 交换机ID
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 删除失败时抛出
            DeviceNotFoundError: 交换机不存在时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查交换机是否存在
                cursor.execute('''
                    SELECT COUNT(*) FROM switch_info WHERE id = ?
                ''', (switch_id,))
                
                count = cursor.fetchone()[0]
                if count == 0:
                    raise DeviceNotFoundError(f"交换机不存在，ID: {switch_id}")
                
                # 删除交换机配置
                cursor.execute('''
                    DELETE FROM switch_info WHERE id = ?
                ''', (switch_id,))
                
                conn.commit()
                logger.info(f"交换机配置删除成功，ID: {switch_id}")
                return True, "交换机配置删除成功"
        except DeviceNotFoundError:
            # 重新抛出DeviceNotFoundError，不包装在DatabaseQueryError中
            raise
        except Exception as e:
            logger.error(f"删除交换机配置失败: {e}")
            raise DatabaseQueryError(f"删除交换机配置失败: {e}") from e

    def get_switch_by_id(self, switch_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取交换机配置
        
        Args:
            switch_id: 交换机ID
            
        Returns:
            交换机配置字典，如果未找到则返回None
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, ip, snmp_version, community, user, auth_key, auth_protocol,
                           priv_key, priv_protocol, description, device_name, created_at, updated_at
                    FROM switch_info
                    WHERE id = ?
                ''', (switch_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'ip': row[1],
                        'snmp_version': row[2],
                        'community': row[3],
                        'user': row[4],
                        'auth_key': row[5],
                        'auth_protocol': row[6],
                        'priv_key': row[7],
                        'priv_protocol': row[8],
                        'description': row[9],
                        'device_name': row[10],
                        'created_at': row[11],
                        'updated_at': row[12]
                    }
                return None
        except Exception as e:
            logger.error(f"根据ID查询交换机配置失败: {e}")
            raise DatabaseQueryError(f"根据ID查询交换机配置失败: {e}") from e

    def get_switch_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        根据IP地址获取交换机配置
        
        Args:
            ip: 交换机IP地址
            
        Returns:
            交换机配置字典，如果未找到则返回None
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, ip, snmp_version, community, user, auth_key, auth_protocol,
                           priv_key, priv_protocol, description, device_name, created_at, updated_at
                    FROM switch_info
                    WHERE ip = ?
                ''', (ip,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'ip': row[1],
                        'snmp_version': row[2],
                        'community': row[3],
                        'user': row[4],
                        'auth_key': row[5],
                        'auth_protocol': row[6],
                        'priv_key': row[7],
                        'priv_protocol': row[8],
                        'description': row[9],
                        'device_name': row[10],
                        'created_at': row[11],
                        'updated_at': row[12]
                    }
                return None
        except Exception as e:
            logger.error(f"根据IP查询交换机配置失败: {e}")
            raise DatabaseQueryError(f"根据IP查询交换机配置失败: {e}") from e

    def get_all_switches(self) -> List[Dict[str, Any]]:
        """
        获取所有交换机配置
        
        Returns:
            包含所有交换机配置的字典列表，按创建时间降序排列
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, ip, snmp_version, community, user, auth_key, auth_protocol,
                           priv_key, priv_protocol, description, device_name, created_at, updated_at
                    FROM switch_info
                    ORDER BY created_at DESC
                ''')
                
                rows = cursor.fetchall()
                
                # 转换为字典列表
                result = []
                for row in rows:
                    result.append({
                        'id': row[0],
                        'ip': row[1],
                        'snmp_version': row[2],
                        'community': row[3],
                        'user': row[4],
                        'auth_key': row[5],
                        'auth_protocol': row[6],
                        'priv_key': row[7],
                        'priv_protocol': row[8],
                        'description': row[9],
                        'device_name': row[10],
                        'created_at': row[11],
                        'updated_at': row[12]
                    })
                
                return result
        except Exception as e:
            logger.error(f"查询所有交换机配置失败: {e}")
            raise DatabaseQueryError(f"查询所有交换机配置失败: {e}") from e

    def switch_exists(self, ip: str, snmp_version: str) -> bool:
        """
        检查交换机是否已存在（基于IP地址和SNMP版本）
        
        Args:
            ip: 交换机IP地址
            snmp_version: SNMP版本
            
        Returns:
            如果交换机已存在返回True，否则返回False
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*) FROM switch_info WHERE ip = ? AND snmp_version = ?
                ''', (ip, snmp_version))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"检查交换机是否存在失败: {e}")
            raise DatabaseQueryError(f"检查交换机是否存在失败: {e}") from e

    def get_switch_count(self) -> int:
        """
        获取交换机总数
        
        Returns:
            交换机总数
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM switch_info')
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"查询交换机总数失败: {e}")
            raise DatabaseQueryError(f"查询交换机总数失败: {e}") from e