#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑图信息管理器 - 用于管理拓扑图信息的数据库操作
"""

from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager

from src.core.logger import logger
from src.models.topology_info import TopologyInfo
from src.database.connection_pool import AsyncConnectionPool
from src.database.db_exceptions import (
    DatabaseError,
    DatabaseQueryError,
    DatabaseConnectionError,
)
from src.database.managers.base_manager import BaseDatabaseManager


class TopologyManager(BaseDatabaseManager):
    """拓扑图信息管理器类

    提供拓扑图信息的增删改查操作。
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
        初始化拓扑图信息管理器

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
        """初始化拓扑图信息表结构

        创建拓扑图信息表（如果不存在），启用外键约束和优化设置。
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

                # 创建拓扑图信息表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS topology_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # 为创建时间创建索引，方便按时间查询
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_topology_info_created_at 
                    ON topology_info(created_at)
                """
                )

                conn.commit()
                logger.info("拓扑图信息表初始化成功，已启用外键约束和优化设置")
        except Exception as e:
            logger.error(f"拓扑图信息表初始化失败: {e}")
            raise DatabaseError(f"拓扑图信息表初始化失败: {e}") from e

    def save_topology(self, topology_info: TopologyInfo) -> int:
        """
        保存拓扑图信息到数据库

        Args:
            topology_info: TopologyInfo对象

        Returns:
            新插入记录的ID

        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        try:
            with self.db_lock:  # 使用锁保护数据库访问
                with self.transaction() as conn:
                    cursor = conn.cursor()

                    # 插入新记录
                    cursor.execute(
                        """
                        INSERT INTO topology_info (content)
                        VALUES (?)
                    """,
                        (topology_info.content,),
                    )

                    # 获取新插入记录的ID
                    new_id = cursor.lastrowid
                    if new_id is None:
                        raise DatabaseQueryError("无法获取新插入记录的ID")

                    logger.info(f"拓扑图信息保存成功，ID: {new_id}")
                    return new_id
        except Exception as e:
            logger.error(f"保存拓扑图信息失败: {e}")
            raise DatabaseQueryError(f"保存拓扑图信息失败: {e}") from e

    def get_all_topologies(self) -> List[Dict[str, Any]]:
        """
        获取所有拓扑图信息

        Returns:
            包含所有拓扑图信息的字典列表，按创建时间降序排列

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, content, created_at
                    FROM topology_info
                    ORDER BY created_at DESC
                """
                )

                rows = cursor.fetchall()

                # 转换为字典列表
                result = []
                for row in rows:
                    result.append(
                        {
                            "id": row[0],
                            "content": row[1],
                            "created_at": row[2],
                        }
                    )

                return result
        except Exception as e:
            logger.error(f"查询所有拓扑图信息失败: {e}")
            raise DatabaseQueryError(f"查询所有拓扑图信息失败: {e}") from e

    def get_topology_by_id(self, topology_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取拓扑图信息

        Args:
            topology_id: 拓扑图ID

        Returns:
            拓扑图信息字典，如果未找到则返回None

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, content, created_at
                    FROM topology_info
                    WHERE id = ?
                """,
                    (topology_id,),
                )

                row = cursor.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "content": row[1],
                        "created_at": row[2],
                    }
                return None
        except Exception as e:
            logger.error(f"根据ID查询拓扑图信息失败: {e}")
            raise DatabaseQueryError(f"根据ID查询拓扑图信息失败: {e}") from e

    def get_latest_topology(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的拓扑图信息

        Returns:
            最新的拓扑图信息字典，如果没有记录则返回None

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, content, created_at
                    FROM topology_info
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                )

                row = cursor.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "content": row[1],
                        "created_at": row[2],
                    }
                return None
        except Exception as e:
            logger.error(f"查询最新拓扑图信息失败: {e}")
            raise DatabaseQueryError(f"查询最新拓扑图信息失败: {e}") from e

    def update_topology(self, topology_id: int, content: str) -> bool:
        """
        更新拓扑图内容

        Args:
            topology_id: 拓扑图ID
            content: 新的拓扑图内容

        Returns:
            更新成功返回True，拓扑图不存在返回False

        Raises:
            DatabaseQueryError: 更新失败时抛出
        """
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()

                # 检查拓扑图是否存在
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM topology_info WHERE id = ?
                """,
                    (topology_id,),
                )

                count = cursor.fetchone()[0]
                if count == 0:
                    return False

                # 更新拓扑图内容
                cursor.execute(
                    """
                    UPDATE topology_info SET content = ? WHERE id = ?
                """,
                    (content, topology_id),
                )

                logger.info(f"拓扑图信息更新成功，ID: {topology_id}")
                return True
        except Exception as e:
            logger.error(f"更新拓扑图信息失败: {e}")
            raise DatabaseQueryError(f"更新拓扑图信息失败: {e}") from e

    def delete_topology(self, topology_id: int) -> bool:
        """
        删除拓扑图

        Args:
            topology_id: 拓扑图ID

        Returns:
            删除成功返回True，拓扑图不存在返回False

        Raises:
            DatabaseQueryError: 删除失败时抛出
        """
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()

                # 检查拓扑图是否存在
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM topology_info WHERE id = ?
                """,
                    (topology_id,),
                )

                count = cursor.fetchone()[0]
                if count == 0:
                    return False

                # 删除拓扑图
                cursor.execute(
                    """
                    DELETE FROM topology_info WHERE id = ?
                """,
                    (topology_id,),
                )

                logger.info(f"拓扑图删除成功，ID: {topology_id}")
                return True
        except Exception as e:
            logger.error(f"删除拓扑图失败: {e}")
            raise DatabaseQueryError(f"删除拓扑图失败: {e}") from e

    def get_topology_count(self) -> int:
        """
        获取拓扑图总数

        Returns:
            拓扑图总数

        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM topology_info")
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"查询拓扑图总数失败: {e}")
            raise DatabaseQueryError(f"查询拓扑图总数失败: {e}") from e

    async def close_async_pool(self):
        """
        关闭异步连接池

        关闭所有异步数据库连接，释放资源。
        """
        if self.async_pool is not None:
            await self.async_pool.close_all_connections()
            self.async_pool = None
            logger.info("拓扑图管理器异步连接池已关闭")
