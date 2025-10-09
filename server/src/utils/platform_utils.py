#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器端跨平台系统差异处理工具模块
提供处理不同操作系统间差异的工具函数
支持Windows、Linux
"""

import os
import platform
import signal
from typing import Optional, Callable, Any

# 第三方库导入
# 无

# 本地应用/库导入
# 无


def get_platform() -> str:
    """
    获取当前操作系统平台
    
    Returns:
        str: 操作系统平台名称 (windows, linux)
    """
    return platform.system().lower()


def is_windows() -> bool:
    """
    检查当前是否为Windows系统
    
    Returns:
        bool: 是否为Windows系统
    """
    return get_platform() == "windows"


def is_linux() -> bool:
    """
    检查当前是否为Linux系统
    
    Returns:
        bool: 是否为Linux系统
    """
    return get_platform() == "linux"


def get_path_separator() -> str:
    """
    获取路径分隔符
    
    Returns:
        str: 路径分隔符
    """
    return os.sep


def get_line_separator() -> str:
    """
    获取行分隔符
    
    Returns:
        str: 行分隔符
    """
    return os.linesep


def get_appropriate_encoding() -> str:
    """
    获取适合当前平台的编码
    
    Returns:
        str: 适合当前平台的编码
    """
    if is_windows():
        return "gbk"
    else:
        return "utf-8"


def setup_signal_handlers(handler: Callable[[int, Any], None]) -> None:
    """
    设置信号处理器
    
    Args:
        handler: 信号处理函数
    """
    try:
        # SIGINT (Ctrl+C) 在所有平台都支持
        signal.signal(signal.SIGINT, handler)
        
        # SIGTERM 在非Windows平台支持
        if not is_windows():
            signal.signal(signal.SIGTERM, handler)
    except Exception:
        # 在某些平台上可能不支持信号处理，忽略错误
        pass