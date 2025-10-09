#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库异常处理模块 - 定义专门的数据库异常类
"""

class DatabaseError(Exception):
    """数据库操作基础异常类"""
    pass

class DatabaseConnectionError(DatabaseError):
    """数据库连接异常"""
    pass

class DatabaseInitializationError(DatabaseError):
    """数据库初始化异常"""
    pass

class DatabaseQueryError(DatabaseError):
    """数据库查询异常"""
    pass

class DatabaseTransactionError(DatabaseError):
    """数据库事务异常"""
    pass

class DeviceNotFoundError(DatabaseError):
    """设备未找到异常"""
    pass

class DeviceAlreadyExistsError(DatabaseError):
    """设备已存在异常"""
    pass