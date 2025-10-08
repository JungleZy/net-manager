# -*- coding: utf-8 -*-

"""
异常模块
"""

# 导出异常模块
from .exceptions import (
    NetManagerError,
    NetworkDiscoveryError,
    NetworkConnectionError,
    SystemInfoCollectionError as DataCollectionError,
    ConfigurationError,
    StateManagerError as StateUpdateError,
    NetworkConnectionError as NetworkTimeoutError
)

# 添加缺失的异常类
class SystemCommandError(NetManagerError):
    """系统命令执行异常"""
    pass

__all__ = [
    'NetManagerError',
    'NetworkDiscoveryError',
    'NetworkConnectionError',
    'DataCollectionError',
    'SystemCommandError',
    'ConfigurationError',
    'StateUpdateError',
    'NetworkTimeoutError'
]