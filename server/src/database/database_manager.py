#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库管理器 - 用于管理Net Manager服务器的数据库操作

该模块已重构为更小的模块，此文件保持向后兼容性。
请使用 src.database.managers 中的具体管理器类。
"""

# 保持向后兼容性，导入新的数据库管理器
from src.database.managers.database_manager import DatabaseManager
from src.database.managers.base_manager import BaseDatabaseManager
from src.database.managers.device_manager import DeviceManager
from src.database.managers.switch_manager import SwitchManager

# 保持原有的异常导入
from src.database.db_exceptions import (
    DatabaseError, 
    DatabaseConnectionError, 
    DatabaseInitializationError,
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError
)

# 为了向后兼容，仍然导出原有的类名
__all__ = [
    'DatabaseManager',
    'DatabaseError',
    'DatabaseConnectionError', 
    'DatabaseInitializationError',
    'DatabaseQueryError',
    'DeviceNotFoundError',
    'DeviceAlreadyExistsError'
]