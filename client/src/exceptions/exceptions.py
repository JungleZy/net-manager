#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义异常类模块
用于统一处理NetManager客户端的异常
提供详细的错误信息和错误码，便于问题诊断和处理
"""

from typing import Optional, Any

class NetManagerError(Exception):
    """
    NetManager基础异常类
    
    Attributes:
        message (str): 错误信息
        error_code (int): 错误码
        details (Any): 详细信息
    """
    
    def __init__(self, message: str, error_code: int = 0, details: Any = None):
        """
        初始化NetManager基础异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码，默认为0
            details (Any): 详细信息，默认为None
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details
    
    def __str__(self) -> str:
        """返回异常的字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def __repr__(self) -> str:
        """返回异常的详细表示"""
        return f"{self.__class__.__name__}(message='{self.message}', error_code={self.error_code}, details={self.details})"

class NetworkDiscoveryError(NetManagerError):
    """网络发现异常"""
    
    def __init__(self, message: str = "网络发现失败", error_code: int = 1001, details: Any = None):
        """
        初始化网络发现异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class NetworkConnectionError(NetManagerError):
    """网络连接异常"""
    
    def __init__(self, message: str = "网络连接失败", error_code: int = 1002, details: Any = None):
        """
        初始化网络连接异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class SystemInfoCollectionError(NetManagerError):
    """系统信息收集异常"""
    
    def __init__(self, message: str = "系统信息收集失败", error_code: int = 2001, details: Any = None):
        """
        初始化系统信息收集异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class ConfigurationError(NetManagerError):
    """配置错误异常"""
    
    def __init__(self, message: str = "配置错误", error_code: int = 3001, details: Any = None):
        """
        初始化配置错误异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class StateManagerError(NetManagerError):
    """状态管理异常"""
    
    def __init__(self, message: str = "状态管理失败", error_code: int = 4001, details: Any = None):
        """
        初始化状态管理异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class SingletonManagerError(NetManagerError):
    """单例管理异常"""
    
    def __init__(self, message: str = "单例管理失败", error_code: int = 5001, details: Any = None):
        """
        初始化单例管理异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class AutoStartError(NetManagerError):
    """自启动设置异常"""
    
    def __init__(self, message: str = "自启动设置失败", error_code: int = 6001, details: Any = None):
        """
        初始化自启动设置异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)

class PlatformError(NetManagerError):
    """平台相关异常"""
    
    def __init__(self, message: str = "平台相关操作失败", error_code: int = 7001, details: Any = None):
        """
        初始化平台相关异常
        
        Args:
            message (str): 错误信息
            error_code (int): 错误码
            details (Any): 详细信息
        """
        super().__init__(message, error_code, details)