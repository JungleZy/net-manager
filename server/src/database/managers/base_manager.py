#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础数据库管理器 - 提供数据库连接和基本操作功能
"""

import sqlite3
import threading
from pathlib import Path
from contextlib import contextmanager
from typing import Any

from src.core.logger import logger
from src.database.connection_pool import ConnectionPool, AsyncConnectionPool
from src.database.db_exceptions import (
    DatabaseError, 
    DatabaseConnectionError, 
    DatabaseInitializationError,
    DatabaseQueryError,
    DatabaseTransactionError
)


class BaseDatabaseManager:
    """基础数据库管理器类
    
    提供线程安全的数据库连接和基本操作接口。
    """
    
    def __init__(self, db_path: str = "net_manager_server.db", max_connections: int = 10,
                 cleanup_interval: int = 60, max_idle_time: int = 300):
        """
        初始化基础数据库管理器
        
        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            cleanup_interval: 连接池清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
            
        Raises:
            DatabaseInitializationError: 数据库初始化失败时抛出
        """
        self.db_path = Path(db_path)
        self.db_lock = threading.RLock()  # 使用可重入锁
        
        # 初始化连接池
        self.connection_pool = ConnectionPool(
            db_path=str(self.db_path),
            max_connections=max_connections,
            cleanup_interval=cleanup_interval,
            max_idle_time=max_idle_time
        )
        # 初始化异步连接池引用
        self.async_pool = None

    def init_async_pool(self, async_pool=None, max_connections: int = 10, min_connections: int = 2,
                       cleanup_interval: int = 60, max_idle_time: int = 300):
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
                max_idle_time=max_idle_time
            )

    @contextmanager
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

    @contextmanager
    def get_db_connection(self):
        """
        数据库连接上下文管理器
        
        从连接池获取数据库连接，使用完毕后自动归还到连接池。
        
        Yields:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseConnectionError: 数据库连接失败时抛出
        """
        with self.connection_pool.get_connection_context() as conn:
            try:
                yield conn
            except (DatabaseError, DatabaseConnectionError, DatabaseInitializationError, 
                    DatabaseQueryError):
                # 重新抛出特定的业务异常，不进行包装
                raise
            except sqlite3.Error as e:
                logger.error(f"数据库操作错误: {e}")
                raise DatabaseQueryError(f"数据库操作失败: {e}") from e
            except Exception as e:
                logger.error(f"未知数据库错误: {e}")
                raise DatabaseError(f"数据库操作失败: {e}") from e

    @contextmanager
    def transaction(self):
        """
        数据库事务上下文管理器
        
        提供事务支持，自动处理事务的提交和回滚。
        
        Yields:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseTransactionError: 事务操作失败时抛出
        """
        with self.get_db_connection() as conn:
            try:
                yield conn
                conn.commit()
                logger.debug("事务提交成功")
            except Exception as e:
                conn.rollback()
                logger.error(f"事务回滚: {e}")
                raise DatabaseTransactionError(f"事务操作失败: {e}") from e

    async def close_async_pool(self):
        """
        关闭异步连接池
        
        关闭所有异步数据库连接，释放资源。
        """
        if self.async_pool is not None:
            await self.async_pool.close_all_connections()
            self.async_pool = None
            logger.info("异步连接池已关闭")