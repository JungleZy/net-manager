#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
常驻进程信息管理器 - 用于管理常驻进程信息的数据库操作
"""

from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from src.core.logger import logger
from src.models.resident_process_info import ResidentProcessInfo
from src.database.connection_pool import AsyncConnectionPool
from src.database.db_exceptions import (
    DatabaseError,
    DatabaseQueryError,
    DatabaseConnectionError,
)
from src.database.managers.base_manager import BaseDatabaseManager


class ResidentProcessManager(BaseDatabaseManager):
    """常驻进程信息管理器类

    提供常驻进程信息的增删改查操作。
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
        初始化常驻进程信息管理器

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
            )

    def init_tables(self) -> None:
        """初始化常驻进程信息表结构

        创建常驻进程信息表（如果不存在），启用外键约束和优化设置。
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

                # 创建常驻进程信息表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS resident_process_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # 为进程名称创建索引，方便查询和保证唯一性
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_resident_process_name 
                    ON resident_process_info(name)
                """
                )

                conn.commit()
                logger.info("常驻进程信息表初始化成功，已启用外键约束和优化设置")
        except Exception as e:
            logger.error(f"常驻进程信息表初始化失败: {e}")
            raise DatabaseError(f"常驻进程信息表初始化失败: {e}") from e

    def add_resident_process(self, process_info: ResidentProcessInfo) -> int:
        """
        添加常驻进程信息到数据库

        Args:
            process_info: ResidentProcessInfo对象

        Returns:
            新插入记录的ID

        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        try:
            with self.db_lock:  # 使用锁保护数据库访问
                with self.transaction() as conn:
                    cursor = conn.cursor()

                    # 插入新记录（如果进程名已存在则忽略）
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO resident_process_info (name)
                        VALUES (?)
                    """,
                        (process_info.name,),
                    )

                    # 获取新插入记录的ID或已存在记录的ID
                    new_id = cursor.lastrowid
                    if new_id == 0 or new_id is None:
                        # 记录已存在，获取现有记录的ID
                        cursor.execute(
                            "SELECT id FROM resident_process_info WHERE name = ?",
                            (process_info.name,),
                        )
                        result = cursor.fetchone()
                        if result:
                            new_id = result[0]
                            logger.info(
                                f"常驻进程已存在: {process_info.name}, ID: {new_id}"
                            )
                        else:
                            raise DatabaseQueryError("无法获取记录ID")
                    else:
                        logger.info(
                            f"常驻进程信息添加成功，进程名: {process_info.name}, ID: {new_id}"
                        )

                    return int(new_id)
        except Exception as e:
            logger.error(f"添加常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"添加常驻进程信息失败: {e}") from e

    def get_all_resident_processes(self) -> List[Dict[str, Any]]:
        """
        获取所有常驻进程信息

        Returns:
            包含所有常驻进程信息的字典列表，按创建时间降序排列

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, name, created_at
                    FROM resident_process_info
                    ORDER BY created_at
                """
                )

                rows = cursor.fetchall()

                processes = []
                for row in rows:
                    process_dict = {
                        "id": row[0],
                        "name": row[1],
                        "created_at": row[2],
                    }
                    processes.append(process_dict)

                logger.info(f"获取所有常驻进程信息成功，共 {len(processes)} 条记录")
                return processes
        except Exception as e:
            logger.error(f"获取所有常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"获取所有常驻进程信息失败: {e}") from e

    def get_resident_process_by_id(self, process_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取常驻进程信息

        Args:
            process_id: 进程记录ID

        Returns:
            包含常驻进程信息的字典，如果未找到则返回None

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, name, created_at
                    FROM resident_process_info
                    WHERE id = ?
                """,
                    (process_id,),
                )

                row = cursor.fetchone()
                if row:
                    process_dict = {
                        "id": row[0],
                        "name": row[1],
                        "created_at": row[2],
                    }
                    logger.info(f"获取常驻进程信息成功，ID: {process_id}")
                    return process_dict
                else:
                    logger.warning(f"未找到常驻进程信息，ID: {process_id}")
                    return None
        except Exception as e:
            logger.error(f"获取常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"获取常驻进程信息失败: {e}") from e

    def get_resident_process_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根据进程名称获取常驻进程信息

        Args:
            name: 进程名称

        Returns:
            包含常驻进程信息的字典，如果未找到则返回None

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, name, created_at
                    FROM resident_process_info
                    WHERE name = ?
                """,
                    (name,),
                )

                row = cursor.fetchone()
                if row:
                    process_dict = {
                        "id": row[0],
                        "name": row[1],
                        "created_at": row[2],
                    }
                    logger.info(f"获取常驻进程信息成功，进程名: {name}")
                    return process_dict
                else:
                    logger.warning(f"未找到常驻进程信息，进程名: {name}")
                    return None
        except Exception as e:
            logger.error(f"获取常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"获取常驻进程信息失败: {e}") from e

    def delete_resident_process(self, process_id: int) -> bool:
        """
        删除常驻进程信息

        Args:
            process_id: 进程记录ID

        Returns:
            删除成功返回True，记录不存在返回False

        Raises:
            DatabaseQueryError: 删除失败时抛出
        """
        try:
            with self.db_lock:
                with self.transaction() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM resident_process_info WHERE id = ?",
                        (process_id,),
                    )

                    if cursor.rowcount > 0:
                        logger.info(f"删除常驻进程信息成功，ID: {process_id}")
                        return True
                    else:
                        logger.warning(f"未找到要删除的常驻进程信息，ID: {process_id}")
                        return False
        except Exception as e:
            logger.error(f"删除常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"删除常驻进程信息失败: {e}") from e

    def delete_resident_process_by_name(self, name: str) -> bool:
        """
        根据进程名称删除常驻进程信息

        Args:
            name: 进程名称

        Returns:
            删除成功返回True，记录不存在返回False

        Raises:
            DatabaseQueryError: 删除失败时抛出
        """
        try:
            with self.db_lock:
                with self.transaction() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM resident_process_info WHERE name = ?",
                        (name,),
                    )

                    if cursor.rowcount > 0:
                        logger.info(f"删除常驻进程信息成功，进程名: {name}")
                        return True
                    else:
                        logger.warning(f"未找到要删除的常驻进程信息，进程名: {name}")
                        return False
        except Exception as e:
            logger.error(f"删除常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"删除常驻进程信息失败: {e}") from e

    def clear_all_resident_processes(self) -> int:
        """
        清空所有常驻进程信息

        Returns:
            删除的记录数量

        Raises:
            DatabaseQueryError: 删除失败时抛出
        """
        try:
            with self.db_lock:
                with self.transaction() as conn:
                    cursor = conn.cursor()

                    cursor.execute("DELETE FROM resident_process_info")
                    deleted_count = cursor.rowcount

                    logger.info(
                        f"清空所有常驻进程信息成功，共删除 {deleted_count} 条记录"
                    )
                    return deleted_count
        except Exception as e:
            logger.error(f"清空所有常驻进程信息失败: {e}")
            raise DatabaseQueryError(f"清空所有常驻进程信息失败: {e}") from e

    def batch_add_resident_processes(self, process_names: List[str]) -> Dict[str, Any]:
        """
        批量添加常驻进程信息（自动去重，已存在的进程不会重复添加，不在列表中的进程将被删除）

        Args:
            process_names: 进程名称列表

        Returns:
            包含新增、跳过、删除、失败等详细统计信息的字典

        Raises:
            DatabaseQueryError: 批量添加失败时抛出
        """
        success_count = 0
        failed_count = 0
        skipped_count = 0
        deleted_count = 0
        details = []

        try:
            # 1. 先获取所有已存在的进程名称
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM resident_process_info")
                existing_names = {row[0] for row in cursor.fetchall()}

            logger.info(f"当前数据库中已存在 {len(existing_names)} 个常驻进程")

            # 2. 转换为集合以便高效查找
            new_names_set = set(process_names)

            # 3. 找出需要删除的进程（数据库中有但提交列表中没有的）
            names_to_delete = existing_names - new_names_set
            if names_to_delete:
                logger.info(
                    f"需要删除 {len(names_to_delete)} 个进程: {names_to_delete}"
                )
                for name in names_to_delete:
                    try:
                        if self.delete_resident_process_by_name(name):
                            deleted_count += 1
                            details.append(
                                {
                                    "name": name,
                                    "status": "deleted",
                                    "reason": "不在提交列表中",
                                }
                            )
                            logger.info(f"删除进程 '{name}' 成功")
                    except Exception as e:
                        logger.error(f"删除进程 '{name}' 失败: {e}")

            # 4. 处理提交的进程列表
            for name in process_names:
                if name in existing_names:
                    # 进程已存在，跳过
                    skipped_count += 1
                    details.append(
                        {"name": name, "status": "skipped", "reason": "已存在"}
                    )
                    logger.info(f"进程 '{name}' 已存在，跳过添加")
                else:
                    # 进程不存在，添加到数据库
                    try:
                        process_info = ResidentProcessInfo(name=name)
                        process_id = self.add_resident_process(process_info)
                        success_count += 1
                        details.append(
                            {"name": name, "id": process_id, "status": "success"}
                        )
                        # 将新添加的进程加入已存在集合，避免同一批次中的重复
                        existing_names.add(name)
                        logger.info(f"新增进程 '{name}' 成功")
                    except Exception as e:
                        failed_count += 1
                        details.append(
                            {"name": name, "status": "failed", "error": str(e)}
                        )
                        logger.error(f"添加常驻进程 {name} 失败: {e}")

        except Exception as e:
            logger.error(f"批量添加常驻进程时发生错误: {e}")
            raise DatabaseQueryError(f"批量添加常驻进程失败: {e}") from e

        result = {
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "deleted_count": deleted_count,
            "total": len(process_names),
            "details": details,
        }

        logger.info(
            f"批量处理常驻进程完成，新增: {success_count}, 跳过: {skipped_count}, 删除: {deleted_count}, 失败: {failed_count}"
        )
        return result
