#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一数据库管理器 - 整合设备和交换机管理功能
"""

from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager, asynccontextmanager

from src.core.logger import logger
from src.models.device_info import DeviceInfo
from src.models.switch_info import SwitchInfo
from src.database.db_exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseInitializationError,
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError,
)
from src.database.managers.base_manager import BaseDatabaseManager
from src.database.managers.device_manager import DeviceManager
from src.database.managers.switch_manager import SwitchManager


class DatabaseManager:
    """统一数据库管理器类

    整合设备和交换机管理功能，提供统一的数据库操作接口。
    """

    def __init__(
        self,
        db_path: str = "net_manager_server.db",
        max_connections: int = 10,
        cleanup_interval: int = 60,
        max_idle_time: int = 300,
    ):
        """
        初始化统一数据库管理器

        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            cleanup_interval: 连接池清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）

        Raises:
            DatabaseInitializationError: 数据库初始化失败时抛出
        """
        try:
            self.base_manager = BaseDatabaseManager(
                db_path, max_connections, cleanup_interval, max_idle_time
            )
            self.device_manager = DeviceManager(
                db_path, max_connections, cleanup_interval, max_idle_time
            )
            self.switch_manager = SwitchManager(
                db_path, max_connections, cleanup_interval, max_idle_time
            )
            # 初始化异步连接池
            self.async_pool = None
            logger.info("数据库管理器初始化成功")
        except Exception as e:
            logger.error(f"数据库管理器初始化失败: {e}")
            raise DatabaseInitializationError(f"数据库管理器初始化失败: {e}") from e

    # ==================== 数据库健康检查 ====================

    def health_check(self) -> bool:
        """
        数据库健康检查

        Returns:
            数据库连接正常返回True，否则返回False
        """
        try:
            with self.base_manager.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

    def init_async_pool(
        self,
        max_connections: Optional[int] = None,
        min_connections: Optional[int] = None,
        cleanup_interval: int = 60,
        max_idle_time: int = 300,
        auto_adjust: bool = True,
    ):
        """
        初始化异步连接池

        Args:
            max_connections: 最大连接数，默认为None时根据CPU核心数动态计算
            min_connections: 最小连接数，默认为None时根据CPU核心数动态计算
            cleanup_interval: 清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
            auto_adjust: 是否根据CPU核心数自动调整连接池大小
        """
        from src.database.connection_pool import AsyncConnectionPool

        # 如果启用自动调整且未指定连接数，则根据CPU核心数动态计算
        if auto_adjust and (max_connections is None or min_connections is None):
            max_conn, min_conn = self._calculate_optimal_pool_size()
            if max_connections is None:
                max_connections = max_conn
            if min_connections is None:
                min_connections = min_conn

        # 设置默认值
        if max_connections is None:
            max_connections = 10
        if min_connections is None:
            min_connections = 2

        if self.async_pool is None:
            self.async_pool = AsyncConnectionPool(
                db_path=str(self.base_manager.db_path),
                max_connections=max_connections,
                min_connections=min_connections,
                cleanup_interval=cleanup_interval,
                max_idle_time=max_idle_time,
            )
            # 为DeviceManager和SwitchManager初始化异步连接池引用
            self.device_manager.init_async_pool(self.async_pool)
            self.switch_manager.init_async_pool(self.async_pool)
            logger.info(
                f"异步连接池初始化成功，最大连接数: {max_connections}, 最小连接数: {min_connections}"
            )

    def _calculate_optimal_pool_size(self) -> tuple:
        """
        根据CPU核心数计算最优连接池大小

        Returns:
            tuple: (max_connections, min_connections)
        """
        try:
            import multiprocessing

            cpu_count = multiprocessing.cpu_count()

            # 基于CPU核心数的连接池大小计算
            # 混合型工作负载推荐配置
            max_connections = cpu_count * 2 + 1
            min_connections = max(2, cpu_count // 2)

            # 限制最大连接数不超过100（避免过度消耗资源）
            max_connections = min(max_connections, 100)

            return max_connections, min_connections
        except Exception as e:
            logger.warning(f"计算最优连接池大小时出错，使用默认值: {e}")
            return 10, 2

    @asynccontextmanager
    async def get_async_connection(self):
        """
        获取异步数据库连接的上下文管理器

        Yields:
            Connection: 数据库连接对象

        Raises:
            DatabaseConnectionError: 连接失败时抛出
        """
        if self.async_pool is None:
            raise DatabaseConnectionError("异步连接池未初始化")

        try:
            async with self.async_pool.get_connection_context() as conn:
                yield conn
        except Exception as e:
            logger.error(f"获取异步数据库连接失败: {e}")
            raise DatabaseConnectionError(f"获取异步数据库连接失败: {e}") from e

    async def close_async_pool(self):
        """
        关闭异步连接池
        """
        # 关闭DeviceManager的异步连接池
        if hasattr(self.device_manager, "close_async_pool"):
            await self.device_manager.close_async_pool()

        # 关闭SwitchManager的异步连接池
        if hasattr(self.switch_manager, "close_async_pool"):
            await self.switch_manager.close_async_pool()

        # 关闭主异步连接池
        if self.async_pool is not None:
            await self.async_pool.close_all_connections()
            self.async_pool = None
            logger.info("异步连接池已关闭")
