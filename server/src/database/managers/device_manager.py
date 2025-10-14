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
    ):
        """
        初始化设备信息管理器

        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            cleanup_interval: 连接池清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
        """
        super().__init__(db_path, max_connections, cleanup_interval, max_idle_time)
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
            )

    def init_tables(self) -> None:
        """初始化设备信息表结构

        创建设备信息表（如果不存在），启用外键约束和优化设置。
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

                # 创建设备信息表，使用id作为主键
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
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # 为常用查询字段创建索引
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_device_info_client_id 
                    ON device_info(client_id)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_device_info_timestamp 
                    ON device_info(timestamp)
                """
                )

                conn.commit()
                logger.info("设备信息表初始化成功，已启用外键约束和优化设置")
        except Exception as e:
            logger.error(f"设备信息表初始化失败: {e}")
            raise DatabaseError(f"设备信息表初始化失败: {e}") from e

    def save_device_info(self, device_info: DeviceInfo) -> None:
        """
        保存设备信息到数据库

        使用id作为主键进行更新或插入操作。
        注意：通过TCP更新数据时不更新type字段，type字段只能通过API手动设置。

        Args:
            device_info: DeviceInfo对象

        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        try:
            with self.db_lock:  # 使用锁保护数据库访问
                with self.transaction() as conn:
                    cursor = conn.cursor()

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
                    # 注意：通过TCP更新数据时不更新type字段，type字段只能通过API手动设置，同时确保created_at字段在创建后不会被更新
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO device_info 
                        (id, client_id, hostname, os_name, os_version, os_architecture, machine_type, 
                        services, processes, networks, cpu_info, memory_info, disk_info, type, timestamp, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT type FROM device_info WHERE id = ?), ''), 
                            ?, COALESCE((SELECT created_at FROM device_info WHERE id = ?), ?))
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
                            device_info.id,  # 用于COALESCE子查询的参数
                            device_info.timestamp,
                            device_info.id,  # 用于created_at COALESCE子查询的参数
                            device_info.created_at,
                        ),
                    )

                    # 事务会在退出时自动提交
                    # logger.info(f"设备信息保存成功，ID: {device_info.id}")
        except Exception as e:
            logger.error(f"保存设备信息失败: {e}")
            raise DatabaseQueryError(f"保存设备信息失败: {e}") from e

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
                           services, processes, networks, cpu_info, memory_info, disk_info, type, timestamp, created_at
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
                            "timestamp": row[14],
                            "created_at": row[15],
                        }
                    )

                return result
        except Exception as e:
            logger.error(f"查询所有系统信息失败: {e}")
            raise DatabaseQueryError(f"查询所有系统信息失败: {e}") from e

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
                           services, processes, networks, cpu_info, memory_info, disk_info, type, timestamp, created_at
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
                        "timestamp": row[14],
                        "created_at": row[15],
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
                           services, processes, networks, cpu_info, memory_info, disk_info, type, timestamp, created_at
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
                        "timestamp": row[14],
                        "created_at": row[15],
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

                # 插入新设备信息
                cursor.execute(
                    """
                    INSERT INTO device_info (
                        id, client_id, hostname, os_name, os_version, 
                        os_architecture, machine_type, services, processes, networks,
                        cpu_info, memory_info, disk_info, type, timestamp, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
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

                # 更新设备信息
                cursor.execute(
                    """
                    UPDATE device_info SET 
                        hostname = ?, client_id = ?, os_name = ?, os_version = ?, 
                        os_architecture = ?, machine_type = ?, type = ?,
                        services = ?, processes = ?, networks = ?,
                        cpu_info = ?, memory_info = ?, disk_info = ?
                    WHERE id = ?
                """,
                    (
                        device_data["hostname"],
                        device_data.get("client_id", ""),
                        device_data.get("os_name", ""),
                        device_data.get("os_version", ""),
                        device_data.get("os_architecture", ""),
                        device_data.get("machine_type", ""),
                        device_data.get("type", ""),
                        json.dumps(device_data.get("services", [])),
                        json.dumps(device_data.get("processes", [])),
                        json.dumps(device_data.get("networks", [])),
                        json.dumps(device_data.get("cpu_info", {})),
                        json.dumps(device_data.get("memory_info", {})),
                        json.dumps(device_data.get("disk_info", {})),
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

                cursor.execute("SELECT COUNT(*) FROM device_info")
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"查询设备总数失败: {e}")
            raise DatabaseQueryError(f"查询设备总数失败: {e}") from e

    async def close_async_pool(self):
        """
        关闭异步连接池

        关闭所有异步数据库连接，释放资源。
        """
        if self.async_pool is not None:
            await self.async_pool.close_all_connections()
            self.async_pool = None
            logger.info("设备管理器异步连接池已关闭")
