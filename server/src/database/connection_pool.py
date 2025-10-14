#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库连接池模块 - 提供SQLite数据库连接池功能
"""

import sqlite3
import threading
import time
import queue
from contextlib import contextmanager
from typing import Optional
import asyncio

from src.core.logger import logger
from src.database.db_exceptions import DatabaseConnectionError


class ConnectionPool:
    """SQLite数据库连接池类
    
    提供线程安全的数据库连接池管理功能，支持连接复用、
    定期清理空闲连接等功能。
    """
    
    def __init__(self, db_path: str, max_connections: int = 10, min_connections: int = 2, 
                 cleanup_interval: int = 60, max_idle_time: int = 300):
        """
        初始化连接池
        
        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            min_connections: 最小连接数
            cleanup_interval: 清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.cleanup_interval = cleanup_interval
        self.max_idle_time = max_idle_time
        self.connections = queue.Queue(maxsize=max_connections)
        self.lock = threading.RLock()
        self.active_connections = 0
        self.is_closed = False
        self.connection_timestamps = {}  # 记录连接获取时间
        
        # 初始化最小连接数
        self._initialize_min_connections()
        
        # 启动空闲连接清理线程
        self._start_cleanup_thread()
    
    def _initialize_min_connections(self) -> None:
        """初始化最小连接数"""
        for _ in range(self.min_connections):
            try:
                conn = self._create_connection()
                self.connections.put(conn)
                self.active_connections += 1
            except Exception as e:
                logger.warning(f"初始化连接池时创建连接失败: {e}")
    
    def _create_connection(self) -> sqlite3.Connection:
        """
        创建新的数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseConnectionError: 连接创建失败时抛出
        """
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # 允许跨线程使用
                timeout=30.0  # 设置连接超时
            )
            
            # 启用外键约束
            conn.execute("PRAGMA foreign_keys = ON")
            
            # 设置优化参数
            conn.execute("PRAGMA journal_mode = WAL")  # 使用WAL模式提高并发性能
            conn.execute("PRAGMA synchronous = NORMAL")  # 平衡性能和数据安全
            conn.execute("PRAGMA cache_size = 10000")  # 增加缓存大小
            conn.execute("PRAGMA temp_store = MEMORY")  # 临时表存储在内存中
            
            logger.debug(f"创建新的数据库连接: {self.db_path}")
            return conn
        except Exception as e:
            logger.error(f"创建数据库连接失败: {e}")
            raise DatabaseConnectionError(f"创建数据库连接失败: {e}") from e
    
    def get_connection(self) -> sqlite3.Connection:
        """
        从连接池获取数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseConnectionError: 获取连接失败时抛出
        """
        if self.is_closed:
            raise DatabaseConnectionError("连接池已关闭")
        
        try:
            # 尝试从连接池获取现有连接
            conn = self.connections.get_nowait()
            logger.debug("从连接池获取现有连接")
        except queue.Empty:
            # 连接池为空，检查是否可以创建新连接
            with self.lock:
                if self.active_connections < self.max_connections:
                    conn = self._create_connection()
                    self.active_connections += 1
                    logger.debug("创建新的数据库连接")
                else:
                    # 达到最大连接数，等待可用连接
                    try:
                        conn = self.connections.get(timeout=30.0)
                        logger.debug("等待并获取到连接")
                    except queue.Empty:
                        raise DatabaseConnectionError("获取数据库连接超时")
        
        # 检查连接是否有效
        try:
            conn.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"数据库连接已失效，重新创建: {e}")
            with self.lock:
                self.active_connections -= 1
            conn = self._create_connection()
            with self.lock:
                self.active_connections += 1
        
        # 记录连接获取时间
        with self.lock:
            self.connection_timestamps[id(conn)] = time.time()
        
        return conn
    
    def release_connection(self, conn: sqlite3.Connection) -> None:
        """
        将数据库连接归还到连接池
        
        Args:
            conn: 要归还的数据库连接
        """
        if self.is_closed:
            try:
                conn.close()
            except:
                pass
            return
        
        try:
            # 清理连接状态
            conn.rollback()  # 回滚未提交的事务
        except:
            pass
        
        try:
            # 尝试将连接放回连接池
            self.connections.put_nowait(conn)
            logger.debug("连接已归还到连接池")
        except queue.Full:
            # 连接池已满，关闭连接
            try:
                conn.close()
                with self.lock:
                    self.active_connections -= 1
                    # 清理时间戳记录
                    if id(conn) in self.connection_timestamps:
                        del self.connection_timestamps[id(conn)]
                logger.debug("连接池已满，关闭连接")
            except:
                pass
        else:
            # 成功放回连接池，清理时间戳记录
            with self.lock:
                if id(conn) in self.connection_timestamps:
                    del self.connection_timestamps[id(conn)]
    
    @contextmanager
    def get_connection_context(self):
        """
        数据库连接上下文管理器
        
        自动管理数据库连接的获取和归还。
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                self.release_connection(conn)
    
    def _cleanup_idle_connections(self) -> None:
        """定期清理空闲连接的后台线程函数"""
        while not self.is_closed:
            try:
                time.sleep(self.cleanup_interval)  # 使用配置的清理间隔
                
                # 检查是否需要清理连接
                with self.lock:
                    current_connections = self.connections.qsize()
                    if current_connections > self.min_connections:
                        # 获取当前时间
                        current_time = time.time()
                        
                        # 计算需要保留的连接数
                        keep_count = self.min_connections
                        available_count = current_connections
                        
                        # 检查连接池中的连接，清理超时的连接
                        temp_connections = []
                        cleaned_count = 0
                        
                        # 取出所有连接进行检查
                        while available_count > 0:
                            try:
                                conn = self.connections.get_nowait()
                                available_count -= 1
                                
                                # 检查连接是否超时
                                conn_id = id(conn)
                                if (conn_id in self.connection_timestamps and 
                                    current_time - self.connection_timestamps[conn_id] > self.max_idle_time):
                                    # 连接超时，关闭它
                                    try:
                                        conn.close()
                                        self.active_connections -= 1
                                        if conn_id in self.connection_timestamps:
                                            del self.connection_timestamps[conn_id]
                                        cleaned_count += 1
                                        logger.debug("清理超时连接")
                                    except:
                                        pass
                                else:
                                    # 连接未超时，放回临时列表
                                    temp_connections.append(conn)
                            except queue.Empty:
                                break
                        
                        # 将未超时的连接放回连接池
                        for conn in temp_connections:
                            try:
                                self.connections.put_nowait(conn)
                            except queue.Full:
                                # 连接池已满，关闭连接
                                try:
                                    conn.close()
                                    self.active_connections -= 1
                                    conn_id = id(conn)
                                    if conn_id in self.connection_timestamps:
                                        del self.connection_timestamps[conn_id]
                                    logger.debug("连接池已满，关闭连接")
                                except:
                                    pass
                        
                        if cleaned_count > 0:
                            logger.info(f"清理了 {cleaned_count} 个超时连接")
            except Exception as e:
                logger.warning(f"清理空闲连接时出错: {e}")
    
    def _start_cleanup_thread(self) -> None:
        """启动空闲连接清理线程"""
        cleanup_thread = threading.Thread(
            target=self._cleanup_idle_connections,
            daemon=True,
            name="DatabaseConnectionCleanupThread"
        )
        cleanup_thread.start()
        logger.info("启动数据库连接池清理线程")
    
    def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        self.is_closed = True
        
        # 关闭连接池中的所有连接
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                conn.close()
            except queue.Empty:
                break
            except Exception as e:
                logger.warning(f"关闭连接时出错: {e}")
        
        logger.info("已关闭所有数据库连接")


class AsyncConnectionPool:
    """异步数据库连接池类
    
    提供异步数据库连接池管理功能。
    """
    
    def __init__(self, db_path: str, max_connections: int = 10, min_connections: int = 2,
                 cleanup_interval: int = 60, max_idle_time: int = 300):
        """
        初始化异步连接池
        
        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
            min_connections: 最小连接数
            cleanup_interval: 清理间隔（秒）
            max_idle_time: 连接最大空闲时间（秒）
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.cleanup_interval = cleanup_interval
        self.max_idle_time = max_idle_time
        self.connections = asyncio.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.is_closed = False
        self.lock = asyncio.Lock()
        self.connection_timestamps = {}  # 记录连接获取时间
        self.cleanup_task = None  # 清理任务
        
        # 初始化最小连接数
        self._initialize_min_connections()
        
        # 启动清理任务
        self._start_cleanup_thread()
    
    def _initialize_min_connections(self) -> None:
        """初始化最小连接数"""
        for _ in range(self.min_connections):
            try:
                conn = self._create_connection()
                self.connections.put_nowait(conn)
                self.active_connections += 1
            except Exception as e:
                logger.warning(f"初始化异步连接池时创建连接失败: {e}")
    
    def _create_connection(self) -> sqlite3.Connection:
        """
        创建新的数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseConnectionError: 连接创建失败时抛出
        """
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            
            # 启用外键约束
            conn.execute("PRAGMA foreign_keys = ON")
            
            # 设置优化参数
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")
            conn.execute("PRAGMA temp_store = MEMORY")
            
            logger.debug(f"创建新的异步数据库连接: {self.db_path}")
            return conn
        except Exception as e:
            logger.error(f"创建异步数据库连接失败: {e}")
            raise DatabaseConnectionError(f"创建异步数据库连接失败: {e}") from e
    
    async def get_connection(self) -> sqlite3.Connection:
        """
        从连接池获取数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseConnectionError: 获取连接失败时抛出
        """
        if self.is_closed:
            raise DatabaseConnectionError("连接池已关闭")
        
        try:
            # 尝试从连接池获取现有连接
            conn = self.connections.get_nowait()
            logger.debug("从异步连接池获取现有连接")
        except asyncio.QueueEmpty:
            # 连接池为空，检查是否可以创建新连接
            async with self.lock:
                if self.active_connections < self.max_connections:
                    conn = self._create_connection()
                    self.active_connections += 1
                    logger.debug("创建新的异步数据库连接")
                else:
                    # 达到最大连接数，等待可用连接
                    try:
                        conn = await asyncio.wait_for(self.connections.get(), timeout=30.0)
                        logger.debug("等待并获取到异步连接")
                    except asyncio.TimeoutError:
                        raise DatabaseConnectionError("获取异步数据库连接超时")
        
        # 检查连接是否有效
        try:
            conn.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"异步数据库连接已失效，重新创建: {e}")
            async with self.lock:
                self.active_connections -= 1
            conn = self._create_connection()
            async with self.lock:
                self.active_connections += 1
        
        # 记录连接获取时间
        async with self.lock:
            self.connection_timestamps[id(conn)] = time.time()
        
        return conn
    
    async def release_connection(self, conn: sqlite3.Connection) -> None:
        """
        将数据库连接归还到连接池
        
        Args:
            conn: 要归还的数据库连接
        """
        # 清理连接时间戳
        conn_id = id(conn)
        async with self.lock:
            if conn_id in self.connection_timestamps:
                del self.connection_timestamps[conn_id]
        
        if self.is_closed:
            try:
                conn.close()
            except:
                pass
            return
        
        try:
            # 清理连接状态
            conn.rollback()
        except:
            pass
        
        try:
            # 尝试将连接放回连接池
            self.connections.put_nowait(conn)
            logger.debug("异步连接已归还到连接池")
        except asyncio.QueueFull:
            # 连接池已满，关闭连接
            try:
                conn.close()
                async with self.lock:
                    self.active_connections -= 1
                logger.debug("异步连接池已满，关闭连接")
            except:
                pass
    
    @contextmanager
    async def get_connection_context(self):
        """
        异步数据库连接上下文管理器
        
        自动管理数据库连接的获取和归还。
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = await self.get_connection()
            yield conn
        finally:
            if conn:
                await self.release_connection(conn)
    
    def _start_cleanup_thread(self) -> None:
        """启动清理线程"""
        # 检查是否有运行中的事件循环
        try:
            loop = asyncio.get_running_loop()
            if self.cleanup_task is None or self.cleanup_task.done():
                self.cleanup_task = loop.create_task(self._cleanup_idle_connections())
                logger.info("已启动异步连接池清理任务")
        except RuntimeError:
            # 没有运行中的事件循环，延迟启动清理任务
            logger.info("未检测到运行中的事件循环，将延迟启动异步连接池清理任务")
            # 可以选择在这里不启动清理任务，或者使用其他机制
            pass

    async def _cleanup_idle_connections(self) -> None:
        """定期清理空闲连接"""
        while not self.is_closed:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # 获取当前时间
                current_time = time.time()
                
                # 收集需要关闭的连接
                connections_to_close = []
                
                # 使用锁保护访问连接队列
                async with self.lock:
                    # 创建临时列表存储连接
                    temp_connections = []
                    
                    # 检查队列中的连接
                    while not self.connections.empty():
                        try:
                            conn = self.connections.get_nowait()
                            conn_id = id(conn)
                            
                            # 检查连接是否超时
                            if (conn_id in self.connection_timestamps and 
                                current_time - self.connection_timestamps[conn_id] > self.max_idle_time):
                                # 连接超时，需要关闭
                                connections_to_close.append(conn)
                                self.active_connections -= 1
                                # 清理时间戳
                                if conn_id in self.connection_timestamps:
                                    del self.connection_timestamps[conn_id]
                            else:
                                # 连接未超时，放回临时列表
                                temp_connections.append(conn)
                        except asyncio.QueueEmpty:
                            break
                    
                    # 将未超时的连接放回队列
                    for conn in temp_connections:
                        try:
                            self.connections.put_nowait(conn)
                        except asyncio.QueueFull:
                            # 队列满了就关闭连接
                            conn.close()
                            self.active_connections -= 1
                
                # 关闭超时的连接
                for conn in connections_to_close:
                    try:
                        conn.close()
                        logger.debug(f"已关闭超时的异步数据库连接")
                    except Exception as e:
                        logger.warning(f"关闭异步数据库连接时出错: {e}")
                        
            except Exception as e:
                logger.error(f"清理异步连接池时出错: {e}")
                # 继续下一次循环

    async def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        self.is_closed = True
        
        # 取消清理任务
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 关闭连接池中的所有连接
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                conn.close()
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                logger.warning(f"关闭异步连接时出错: {e}")
        
        logger.info("已关闭所有异步数据库连接")