#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义异常类模块
用于统一处理NetManager客户端的异常
"""

class NetManagerError(Exception):
    """NetManager基础异常类"""
    pass

class NetworkDiscoveryError(NetManagerError):
    """网络发现异常"""
    pass

class NetworkConnectionError(NetManagerError):
    """网络连接异常"""
    pass

class SystemInfoCollectionError(NetManagerError):
    """系统信息收集异常"""
    pass

class ConfigurationError(NetManagerError):
    """配置错误异常"""
    pass

class StateManagerError(NetManagerError):
    """状态管理异常"""
    pass

class SingletonManagerError(NetManagerError):
    """单例管理异常"""
    pass