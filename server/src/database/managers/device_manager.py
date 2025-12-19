#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备信息管理器 - 用于管理设备信息的数据库操作
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager

from src.core.logger import logger
from src.core.config import DB_ACQUIRE_TIMEOUT
from src.models.device_info import DeviceInfo
from src.database.connection_pool import AsyncConnectionPool
from src.database.db_exceptions import (
    DatabaseError,
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError,
    DatabaseConnectionError,
)
from src.database.managers.base_manager import BaseDatabaseManager


class DeviceManager(BaseDatabaseManager):
    """设备信息管理器类

    提供设备信息的增删改查操作。
    """

    def __init__(
        self,
        db_path: str = "net_manager_server.db",
        max_connections: int = 10,
        cleanup_interval: int = 60,
        max_idle_time: int = 300,
        shared_pool=None,
    ):
        """
        初始化设备信息管理器

        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            cleanup_interval: 连接池清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
            shared_pool: 共享的连接池实例（可选）
        """
        super().__init__(
            db_path, max_connections, cleanup_interval, max_idle_time, shared_pool
        )
        self.init_tables()
        # 初始化异步连接池引用
        self.async_pool = None

    @asynccontextmanager
    async def get_async_connection(self):
        """
        异步数据库连接上下文管理器

        从异步连接池获取数据库连接，使用完毕后自动归还到连接池。

        Yields:
            sqlite3.Connection: 数据库连接对象

        Raises:
            DatabaseConnectionError: 数据库连接失败时抛出
        """
        if self.async_pool is None:
            raise DatabaseConnectionError("异步连接池未初始化")

        try:
            async with self.async_pool.get_connection_context() as conn:
                yield conn
        except Exception as e:
            logger.error(f"获取异步数据库连接失败: {e}")
            raise DatabaseConnectionError(f"获取异步数据库连接失败: {e}") from e

    def init_async_pool(
        self,
        async_pool=None,
        max_connections: int = 10,
        min_connections: int = 2,
        cleanup_interval: int = 60,
        max_idle_time: int = 300,
    ):
        """
        初始化异步连接池

        Args:
            async_pool: 异步连接池实例（可选）
            max_connections: 最大连接数
            min_connections: 最小连接数
            cleanup_interval: 清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
        """
        if async_pool is not None:
            self.async_pool = async_pool
        elif self.async_pool is None:
            self.async_pool = AsyncConnectionPool(
                db_path=str(self.db_path),
                max_connections=max_connections,
                min_connections=min_connections,
                cleanup_interval=cleanup_interval,
                max_idle_time=max_idle_time,
                acquire_timeout=DB_ACQUIRE_TIMEOUT,
            )

    def init_tables(self) -> None:
        """初始化设备信息表结构

        创建设备信息表（如果不存在），启用外键约束和优化设置。
        如果表已存在，则更新数据结构以包含新字段。
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # 启用外键约束
                cursor.execute("PRAGMA foreign_keys = ON")

                # 设置优化参数
                cursor.execute("PRAGMA journal_mode = WAL")
                cursor.execute("PRAGMA synchronous = NORMAL")
                cursor.execute("PRAGMA cache_size = 10000")
                cursor.execute("PRAGMA temp_store = MEMORY")

                # 创建设备信息表，使用id作为主键，时间使用本地时间
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS device_info (
                        id TEXT PRIMARY KEY, -- 流程编号
                        client_id TEXT,
                        hostname TEXT,
                        os_name TEXT,
                        os_version TEXT,
                        os_architecture TEXT,
                        machine_type TEXT,
                        services TEXT,
                        processes TEXT,
                        networks TEXT,
                        cpu_info TEXT,
                        memory_info TEXT,
                        disk_info TEXT,
                        type TEXT,  -- 设备类型字段（计算机、交换机、服务器等）
                        alias TEXT DEFAULT '',  -- 设备别名字段
                        grouping TEXT DEFAULT '',  -- 设备分组字段
                        timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
                        created_at DATETIME DEFAULT (datetime('now', 'localtime'))
                    )
                """)

                # 检查并添加新字段（如果不存在）
                # 获取当前表结构
                cursor.execute("PRAGMA table_info(device_info)")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # 定义表的完整字段结构
                table_columns = [
                    ("id", "TEXT PRIMARY KEY"),
                    ("client_id", "TEXT"),
                    ("hostname", "TEXT"),
                    ("os_name", "TEXT"),
                    ("os_version", "TEXT"),
                    ("os_architecture", "TEXT"),
                    ("machine_type", "TEXT"),
                    ("services", "TEXT"),
                    ("processes", "TEXT"),
                    ("networks", "TEXT"),
                    ("cpu_info", "TEXT"),
                    ("memory_info", "TEXT"),
                    ("disk_info", "TEXT"),
                    ("type", "TEXT"),
                    ("alias", "TEXT DEFAULT ''"),
                    ("grouping", "TEXT DEFAULT ''"),
                    ("timestamp", "DATETIME DEFAULT (datetime('now', 'localtime'))"),
                    ("created_at", "DATETIME DEFAULT (datetime('now', 'localtime'))")
                ]
                
                # 添加缺失的字段
                for column_name, column_def in table_columns:
                    if column_name not in existing_columns:
                        # 提取字段类型，忽略约束和默认值
                        column_type = column_def.split()[0]
                        try:
                            # 尝试添加字段
                            cursor.execute(f"ALTER TABLE device_info ADD COLUMN {column_name} {column_type}")
                            # 设置默认值（如果需要）
                            if "DEFAULT" in column_def:
                                default_value = column_def.split("DEFAULT")[1].strip()
                                # 处理字符串默认值
                                if default_value.startswith("'") and default_value.endswith("'"):
                                    cursor.execute(f"UPDATE device_info SET {column_name} = {default_value} WHERE {column_name} IS NULL")
                                elif default_value.startswith('"') and default_value.endswith('"'):
                                    cursor.execute(f"UPDATE device_info SET {column_name} = {default_value} WHERE {column_name} IS NULL")
                            conn.commit()
                            logger.info(f"已添加字段 {column_name} 到 device_info 表")
                        except sqlite3.OperationalError as oe:
                            # 如果字段已存在（可能是因为并发操作），忽略错误
                            if "duplicate column name" not in str(oe).lower():
                                logger.warning(f"添加字段 {column_name} 失败: {oe}")
                
                conn.commit()

                # 为常用查询字段创建索引
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_device_info_client_id 
                    ON device_info(client_id)
                """)

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_device_info_timestamp 
                    ON device_info(timestamp)
                """)

                conn.commit()
                # 迁移修复：清理重复client_id，仅保留最新记录
                try:
                    cursor.execute(
                        """
                        SELECT client_id FROM device_info 
                        WHERE client_id IS NOT NULL AND client_id <> ''
                        GROUP BY client_id HAVING COUNT(*) > 1
                        """)
                    dup_rows = cursor.fetchall()
                    for (cid,) in dup_rows:
                        # 保留最新created_at的记录
                        cursor.execute(
                            """
                            SELECT id FROM device_info 
                            WHERE client_id = ? 
                            ORDER BY created_at DESC 
                            LIMIT 1
                            """,
                            (cid,),
                        )
                        keep_row = cursor.fetchone()
                        keep_id = keep_row[0] if keep_row else None
                        if keep_id:
                            cursor.execute(
                                """
                                DELETE FROM device_info 
                                WHERE client_id = ? AND id != ?
                                """,
                                (cid, keep_id),
                            )
                    # 创建唯一索引以防止后续重复
                    cursor.execute(
                        """
                        CREATE UNIQUE INDEX IF NOT EXISTS uniq_device_info_client_id
                        ON device_info(client_id)
                        """)
                    conn.commit()
                except Exception as mig_e:
                    # 迁移过程不中断初始化，记录日志
                    logger.warning(f"清理重复client_id或创建唯一索引时出错: {mig_e}")
                # logger.info("设备信息表初始化成功，已启用外键约束和优化设置")
        except Exception as e:
            logger.error(f"设备信息表初始化失败: {e}")
            raise DatabaseError(f"设备信息表初始化失败: {e}") from e

    def save_device_info(self, device_info: DeviceInfo) -> None:
        """
        保存设备信息到数据库

        使用id作为主键进行更新或插入操作。
        注意：通过TCP更新数据时不更新type、alias和grouping字段，这些字段只能通过API手动设置。

        Args:
            device_info: DeviceInfo对象

        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        self.save_device_info_batch([device_info])

    def save_device_info_batch(self, device_infos: List[DeviceInfo]) -> None:
        """
        批量保存设备信息到数据库

        使用id作为主键进行更新或插入操作。
        注意：通过TCP更新数据时不更新type、alias和grouping字段，这些字段只能通过API手动设置。

        Args:
            device_infos: DeviceInfo对象列表

        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        if not device_infos:
            return

        try:
            with self.db_lock:  # 使用锁保护数据库访问
                with self.transaction() as conn:
                    cursor = conn.cursor()

                    # 批量处理所有设备信息
                    for device_info in device_infos:
                        # 将复杂数据结构转换为JSON字符串
                        services_json = (
                            json.dumps(device_info.services, ensure_ascii=False)
                            if device_info.services
                            else "[]"
                        )
                        processes_json = (
                            json.dumps(device_info.processes, ensure_ascii=False)
                            if device_info.processes
                            else "[]"
                        )
                        networks_json = (
                            json.dumps(device_info.networks, ensure_ascii=False)
                            if device_info.networks
                            else "[]"
                        )
                        cpu_info_json = (
                            json.dumps(device_info.cpu_info, ensure_ascii=False)
                            if device_info.cpu_info
                            else "{}"
                        )
                        memory_info_json = (
                            json.dumps(device_info.memory_info, ensure_ascii=False)
                            if device_info.memory_info
                            else "{}"
                        )
                        disk_info_json = (
                            json.dumps(device_info.disk_info, ensure_ascii=False)
                            if device_info.disk_info
                            else "{}"
                        )

                        # 使用INSERT OR REPLACE语句，如果id已存在则更新，否则插入新记录
                        # 注意：通过TCP更新数据时不更新type、alias和grouping字段，这些字段只能通过API手动设置，同时确保created_at字段在创建后不会被更新
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO device_info 
                            (id, client_id, hostname, os_name, os_version, os_architecture, machine_type, 
                            services, processes, networks, cpu_info, memory_info, disk_info, type, alias, grouping, timestamp, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                COALESCE((SELECT type FROM device_info WHERE client_id = ?), ''), 
                                COALESCE((SELECT alias FROM device_info WHERE client_id = ?), ''),
                                COALESCE((SELECT grouping FROM device_info WHERE client_id = ?), ''),
                                ?, COALESCE((SELECT created_at FROM device_info WHERE client_id = ?), ?))
                        """,
                            (
                                device_info.id,
                                device_info.client_id,
                                device_info.hostname,
                                device_info.os_name,
                                device_info.os_version,
                                device_info.os_architecture,
                                device_info.machine_type,
                                services_json,
                                processes_json,
                                networks_json,
                                cpu_info_json,
                                memory_info_json,
                                disk_info_json,
                                device_info.client_id,  # 用于COALESCE子查询的参数（type）
                                device_info.client_id,  # 用于COALESCE子查询的参数（alias）
                                device_info.client_id,  # 用于COALESCE子查询的参数（grouping）
                                device_info.timestamp,
                                device_info.client_id,  # 用于created_at COALESCE子查询的参数
                                device_info.created_at,
                            ),
                        )

                    # 事务会在退出时自动提交
                    # logger.info(f"批量保存设备信息成功，共 {len(device_infos)} 条")
        except Exception as e:
            logger.error(f"批量保存设备信息失败: {e}")
            raise DatabaseQueryError(f"批量保存设备信息失败: {e}") from e

    def get_all_device_info(self) -> List[Dict[str, Any]]:
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

                cursor.execute(
                    """
                    SELECT id, client_id, hostname, os_name, os_version, os_architecture, machine_type, 
                           services, processes, networks, cpu_info, memory_info, disk_info, type, alias, grouping, timestamp, created_at
                    FROM device_info
                    ORDER BY created_at DESC
                """
                )

                rows = cursor.fetchall()

                # 转换为字典列表
                result = []
                for row in rows:
                    # 处理JSON字段
                    try:
                        services = json.loads(row[7]) if row[7] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析services数据，使用空列表: {row[7]}")
                        services = []

                    try:
                        processes = json.loads(row[8]) if row[8] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析processes数据，使用空列表: {row[8]}")
                        processes = []

                    try:
                        networks = json.loads(row[9]) if row[9] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析networks数据，使用空列表: {row[9]}")
                        networks = []

                    try:
                        cpu_info = json.loads(row[10]) if row[10] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析cpu_info数据，使用空字典: {row[10]}")
                        cpu_info = {}

                    try:
                        memory_info = json.loads(row[11]) if row[11] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(
                            f"无法解析memory_info数据，使用空字典: {row[11]}"
                        )
                        memory_info = {}

                    try:
                        disk_info = json.loads(row[12]) if row[12] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析disk_info数据，使用空字典: {row[12]}")
                        disk_info = {}

                    result.append(
                        {
                            "id": row[0],
                            "client_id": row[1],
                            "hostname": row[2],
                            "os_name": row[3],
                            "os_version": row[4],
                            "os_architecture": row[5],
                            "machine_type": row[6],
                            "services": services,
                            "processes": processes,
                            "networks": networks,
                            "cpu_info": cpu_info,
                            "memory_info": memory_info,
                            "disk_info": disk_info,
                            "type": row[13],
                            "alias": row[14],
                            "grouping": row[15],
                            "timestamp": row[16],
                            "created_at": row[17],
                        }
                    )

                return result
        except Exception as e:
            logger.error(f"查询所有系统信息失败: {e}")
            raise DatabaseQueryError(f"查询所有系统信息失败: {e}") from e

    def get_device_info_paginated(self, limit: int, offset: int, ip_filter: str = None, device_type: str = None, os_name: str = None, grouping: str = None) -> List[Dict[str, Any]]:
        """
        分页获取设备信息，支持筛选条件
        
        Args:
            limit: 每页数量
            offset: 偏移量
            ip_filter: IP地址模糊查询
            device_type: 设备类型精确匹配
            os_name: 操作系统名称精确匹配
            grouping: 设备分组精确匹配
            
        Returns:
            设备信息列表
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                conditions = []
                params = []
                
                # IP模糊查询（networks字段是JSON数组，包含ip_address字段）
                if ip_filter:
                    conditions.append("networks LIKE ?")
                    params.append(f"%{ip_filter}%")
                
                # 设备类型精确匹配
                if device_type:
                    conditions.append("type = ?")
                    params.append(device_type)
                
                # 操作系统名称精确匹配
                if os_name:
                    conditions.append("os_name = ?")
                    params.append(os_name)
                
                # 设备分组精确匹配
                if grouping:
                    conditions.append("grouping = ?")
                    params.append(grouping)
                
                # 构建完整SQL查询
                base_query = """
                    SELECT id, client_id, hostname, os_name, os_version, os_architecture, machine_type,
                           services, processes, networks, cpu_info, memory_info, disk_info, type, alias, grouping, timestamp, created_at
                    FROM device_info
                """
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                    query = f"{base_query} {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
                else:
                    query = f"{base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?"
                
                # 添加分页参数
                params.extend([int(limit), int(offset)])
                cursor.execute(query, params)

                rows = cursor.fetchall()

                result = []
                for row in rows:
                    try:
                        services = json.loads(row[7]) if row[7] else []
                    except (json.JSONDecodeError, TypeError):
                        services = []

                    try:
                        processes = json.loads(row[8]) if row[8] else []
                    except (json.JSONDecodeError, TypeError):
                        processes = []

                    try:
                        networks = json.loads(row[9]) if row[9] else []
                    except (json.JSONDecodeError, TypeError):
                        networks = []

                    try:
                        cpu_info = json.loads(row[10]) if row[10] else {}
                    except (json.JSONDecodeError, TypeError):
                        cpu_info = {}

                    try:
                        memory_info = json.loads(row[11]) if row[11] else {}
                    except (json.JSONDecodeError, TypeError):
                        memory_info = {}

                    try:
                        disk_info = json.loads(row[12]) if row[12] else {}
                    except (json.JSONDecodeError, TypeError):
                        disk_info = {}

                    result.append(
                        {
                            "id": row[0],
                            "client_id": row[1],
                            "hostname": row[2],
                            "os_name": row[3],
                            "os_version": row[4],
                            "os_architecture": row[5],
                            "machine_type": row[6],
                            "services": services,
                            "processes": processes,
                            "networks": networks,
                            "cpu_info": cpu_info,
                            "memory_info": memory_info,
                            "disk_info": disk_info,
                            "type": row[13],
                            "alias": row[14],
                            "grouping": row[15],
                            "timestamp": row[16],
                            "created_at": row[17],
                        }
                    )

                return result
        except Exception as e:
            logger.error(f"分页查询系统信息失败: {e}")
            raise DatabaseQueryError(f"分页查询系统信息失败: {e}") from e

    def get_device_info_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        根据设备ID获取设备信息

        Args:
            device_id: 设备ID

        Returns:
            设备信息字典，如果未找到则返回None

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, client_id, hostname, os_name, os_version, os_architecture, machine_type, 
                           services, processes, networks, cpu_info, memory_info, disk_info, type, alias, grouping, timestamp, created_at
                    FROM device_info
                    WHERE id = ?
                """,
                    (device_id,),
                )

                row = cursor.fetchone()

                if row:
                    # 处理JSON字段
                    try:
                        services = json.loads(row[7]) if row[7] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析services数据，使用空列表: {row[7]}")
                        services = []

                    try:
                        processes = json.loads(row[8]) if row[8] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析processes数据，使用空列表: {row[8]}")
                        processes = []

                    try:
                        networks = json.loads(row[9]) if row[9] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析networks数据，使用空列表: {row[9]}")
                        networks = []

                    try:
                        cpu_info = json.loads(row[10]) if row[10] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析cpu_info数据，使用空字典: {row[10]}")
                        cpu_info = {}

                    try:
                        memory_info = json.loads(row[11]) if row[11] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(
                            f"无法解析memory_info数据，使用空字典: {row[11]}"
                        )
                        memory_info = {}

                    try:
                        disk_info = json.loads(row[12]) if row[12] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析disk_info数据，使用空字典: {row[12]}")
                        disk_info = {}

                    return {
                        "id": row[0],
                        "client_id": row[1],
                        "hostname": row[2],
                        "os_name": row[3],
                        "os_version": row[4],
                        "os_architecture": row[5],
                        "machine_type": row[6],
                        "services": services,
                        "processes": processes,
                        "networks": networks,
                        "cpu_info": cpu_info,
                        "memory_info": memory_info,
                        "disk_info": disk_info,
                        "type": row[13],
                        "alias": row[14],
                        "grouping": row[15],
                        "timestamp": row[16],
                        "created_at": row[17],
                    }
                return None
        except Exception as e:
            logger.error(f"根据设备ID查询系统信息失败: {e}")
            raise DatabaseQueryError(f"根据设备ID查询系统信息失败: {e}") from e

    def get_device_info_by_client_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        根据client_id获取设备信息

        Args:
            client_id: 客户端ID

        Returns:
            设备信息字典，如果未找到则返回None

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, client_id, hostname, os_name, os_version, os_architecture, machine_type, 
                           services, processes, networks, cpu_info, memory_info, disk_info, type, alias, grouping, timestamp, created_at
                    FROM device_info
                    WHERE client_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """,
                    (client_id,),
                )

                row = cursor.fetchone()

                if row:
                    # 处理JSON字段
                    try:
                        services = json.loads(row[7]) if row[7] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析services数据，使用空列表: {row[7]}")
                        services = []

                    try:
                        processes = json.loads(row[8]) if row[8] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析processes数据，使用空列表: {row[8]}")
                        processes = []

                    try:
                        networks = json.loads(row[9]) if row[9] else []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析networks数据，使用空列表: {row[9]}")
                        networks = []

                    try:
                        cpu_info = json.loads(row[10]) if row[10] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析cpu_info数据，使用空字典: {row[10]}")
                        cpu_info = {}

                    try:
                        memory_info = json.loads(row[11]) if row[11] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(
                            f"无法解析memory_info数据，使用空字典: {row[11]}"
                        )
                        memory_info = {}

                    try:
                        disk_info = json.loads(row[12]) if row[12] else {}
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"无法解析disk_info数据，使用空字典: {row[12]}")
                        disk_info = {}

                    return {
                        "id": row[0],
                        "client_id": row[1],
                        "hostname": row[2],
                        "os_name": row[3],
                        "os_version": row[4],
                        "os_architecture": row[5],
                        "machine_type": row[6],
                        "services": services,
                        "processes": processes,
                        "networks": networks,
                        "cpu_info": cpu_info,
                        "memory_info": memory_info,
                        "disk_info": disk_info,
                        "type": row[13],
                        "alias": row[14],
                        "grouping": row[15],
                        "timestamp": row[16],
                        "created_at": row[17],
                    }
                return None
        except Exception as e:
            logger.error(f"根据client_id查询设备信息失败: {e}")
            raise DatabaseQueryError(f"根据client_id查询设备信息失败: {e}") from e

    def update_device_type(self, device_id: str, device_type: str) -> bool:
        """
        更新设备类型

        Args:
            device_id: 设备ID
            device_type: 设备类型

        Returns:
            更新成功返回True，设备不存在返回False

        Raises:
            DatabaseQueryError: 更新失败时抛出
        """
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()

                # 检查系统是否存在
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM device_info WHERE id = ?
                """,
                    (device_id,),
                )

                count = cursor.fetchone()[0]
                if count == 0:
                    return False

                # 更新设备类型
                cursor.execute(
                    """
                    UPDATE device_info SET type = ? WHERE id = ?
                """,
                    (device_type, device_id),
                )

                # 事务会在退出时自动提交
                logger.info(
                    f"设备类型更新成功，设备ID: {device_id}, 类型: {device_type}"
                )
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
            with self.transaction() as conn:
                cursor = conn.cursor()

                # 检查设备是否已存在
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM device_info WHERE id = ?
                """,
                    (device_data["id"],),
                )

                count = cursor.fetchone()[0]
                if count > 0:
                    raise DeviceAlreadyExistsError(f"设备ID已存在: {device_data['id']}")

                # 插入新设备信息（使用本地时间）
                cursor.execute(
                    """
                    INSERT INTO device_info (
                        id, client_id, hostname, os_name, os_version, 
                        os_architecture, machine_type, services, processes, networks,
                        cpu_info, memory_info, disk_info, type, alias, grouping, timestamp, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', datetime('now', 'localtime'), datetime('now', 'localtime'))
                """,
                    (
                        device_data["id"],
                        device_data.get("client_id", ""),
                        device_data["hostname"],
                        device_data.get("os_name", ""),
                        device_data.get("os_version", ""),
                        device_data.get("os_architecture", ""),
                        device_data.get("machine_type", ""),
                        json.dumps(device_data.get("services", [])),
                        json.dumps(device_data.get("processes", [])),
                        json.dumps(device_data.get("networks", [])),
                        json.dumps(device_data.get("cpu_info", {})),
                        json.dumps(device_data.get("memory_info", {})),
                        json.dumps(device_data.get("disk_info", {})),
                        device_data.get("type", ""),
                    ),
                )

                # 事务会在退出时自动提交
                logger.info(f"设备创建成功，设备ID: {device_data['id']}")
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
            with self.transaction() as conn:
                cursor = conn.cursor()

                # 检查设备是否存在
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM device_info WHERE id = ?
                """,
                    (device_data["id"],),
                )

                count = cursor.fetchone()[0]
                if count == 0:
                    raise DeviceNotFoundError(f"设备不存在: {device_data['id']}")

                # 更新设备信息（注意：alias字段只能通过UpdateHandler修改）
                cursor.execute(
                    """
                    UPDATE device_info SET type = ?, alias = ?, grouping = ?
                    WHERE id = ?
                    """,
                    (
                        device_data.get("type", ""),
                        device_data.get("alias", ""),  # alias只能通过UpdateHandler修改
                        device_data.get("grouping", ""),
                        device_data["id"],
                    ),
                )

                # 事务会在退出时自动提交
                logger.info(f"设备更新成功，设备ID: {device_data['id']}")
                return True, "设备更新成功"
        except DeviceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新设备失败: {e}")
            raise DatabaseQueryError(f"更新设备失败: {e}") from e

    def delete_device(self, device_id: str) -> Tuple[bool, str]:
        """
        删除设备

        Args:
            device_id: 设备ID

        Returns:
            (成功标志, 消息) 的元组

        Raises:
            DatabaseQueryError: 删除失败时抛出
            DeviceNotFoundError: 设备不存在时抛出
        """
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()

                # 检查设备是否存在
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM device_info WHERE id = ?
                """,
                    (device_id,),
                )

                count = cursor.fetchone()[0]
                if count == 0:
                    raise DeviceNotFoundError(f"设备不存在: {device_id}")

                # 删除设备
                cursor.execute(
                    """
                    DELETE FROM device_info WHERE id = ?
                """,
                    (device_id,),
                )

                # 事务会在退出时自动提交
                logger.info(f"设备删除成功，设备ID: {device_id}")
                return True, "设备删除成功"
        except DeviceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除设备失败: {e}")
            raise DatabaseQueryError(f"删除设备失败: {e}") from e

    def get_device_count(self, ip_filter: str = None, device_type: str = None, os_name: str = None, grouping: str = None) -> int:
        """
        获取设备总数，支持筛选条件
        
        Args:
            ip_filter: IP地址模糊查询
            device_type: 设备类型精确匹配
            os_name: 操作系统名称精确匹配
            grouping: 设备分组精确匹配

        Returns:
            符合条件的设备总数

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                conditions = []
                params = []
                
                # IP模糊查询
                if ip_filter:
                    conditions.append("networks LIKE ?")
                    params.append(f"%{ip_filter}%")
                
                # 设备类型精确匹配
                if device_type:
                    conditions.append("type = ?")
                    params.append(device_type)
                
                # 操作系统名称精确匹配
                if os_name:
                    conditions.append("os_name = ?")
                    params.append(os_name)
                
                # 设备分组精确匹配
                if grouping:
                    conditions.append("grouping = ?")
                    params.append(grouping)
                
                # 构建完整SQL查询
                base_query = "SELECT COUNT(*) FROM device_info"
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                    query = f"{base_query} {where_clause}"
                else:
                    query = base_query
                
                cursor.execute(query, params)
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"查询设备总数失败: {e}")
            raise DatabaseQueryError(f"查询设备总数失败: {e}") from e

    def get_all_groupings(self) -> List[str]:
        """
        获取所有唯一的设备分组列表
        
        Returns:
            List[str]: 唯一分组名称列表
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 查询所有唯一的分组名称，排除空字符串
                cursor.execute(
                    """
                    SELECT DISTINCT grouping 
                    FROM device_info 
                    WHERE grouping IS NOT NULL AND grouping != '' 
                    ORDER BY grouping
                    """
                )
                
                rows = cursor.fetchall()
                
                # 转换结果为字符串列表
                groupings = [row[0] for row in rows]
                return groupings
        except Exception as e:
            logger.error(f"查询设备分组列表失败: {e}")
            raise DatabaseQueryError(f"查询设备分组列表失败: {e}") from e

    async def close_async_pool(self):
        """
        关闭异步连接池

        关闭所有异步数据库连接，释放资源。
        """
        if self.async_pool is not None:
            await self.async_pool.close_all_connections()
            self.async_pool = None
            logger.info("设备管理器异步连接池已关闭")
