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
from src.database.db_exceptions import (
    DatabaseError, 
    DatabaseConnectionError, 
    DatabaseInitializationError,
    DatabaseQueryError
)


class BaseDatabaseManager:
    """基础数据库管理器类
    
    提供线程安全的数据库连接和基本操作接口。
    """
    
    def __init__(self, db_path: str = "net_manager_server.db"):
        """
        初始化基础数据库管理器
        
        Args:
            db_path: 数据库文件路径
            
        Raises:
            DatabaseInitializationError: 数据库初始化失败时抛出
        """
        self.db_path = Path(db_path)
        self.db_lock = threading.RLock()  # 使用可重入锁

    @contextmanager
    def get_db_connection(self):
        """
        数据库连接上下文管理器
        
        自动管理数据库连接的创建和关闭，确保资源正确释放。
        
        Yields:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            DatabaseConnectionError: 数据库连接失败时抛出
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            yield conn
        except (DatabaseError, DatabaseConnectionError, DatabaseInitializationError, 
                DatabaseQueryError):
            # 重新抛出特定的业务异常，不进行包装
            raise
        except sqlite3.Error as e:
            logger.error(f"数据库连接错误: {e}")
            raise DatabaseConnectionError(f"数据库连接失败: {e}") from e
        except Exception as e:
            logger.error(f"未知数据库错误: {e}")
            raise DatabaseError(f"数据库操作失败: {e}") from e
        finally:
            if conn:
                try:
                    conn.close()
                except sqlite3.Error as e:
                    logger.warning(f"关闭数据库连接时出错: {e}")