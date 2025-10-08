#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
跨平台系统差异处理工具模块
提供处理不同操作系统间差异的工具函数
支持Windows、Linux
"""

import os
import platform
import signal
import sys
from pathlib import Path
from typing import Optional

# 第三方库导入
# 无

# 本地应用/库导入
from src.utils.logger import get_logger


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


def get_appropriate_encoding() -> str:
    """
    获取适合当前平台的文本编码
    
    Returns:
        str: 文本编码 (Windows: gbk, 其他: utf-8)
    """
    if is_windows():
        return "gbk"
    else:
        return "utf-8"


def normalize_path(path: str) -> str:
    """
    标准化路径，处理不同平台间的路径分隔符差异
    
    Args:
        path (str): 原始路径
        
    Returns:
        str: 标准化后的路径
    """
    return str(Path(path))


def get_executable_path() -> str:
    """
    获取当前可执行文件的路径
    
    Returns:
        str: 可执行文件路径
        
    Raises:
        RuntimeError: 获取可执行文件路径失败
    """
    logger = get_logger()
    try:
        # 尝试获取sys.executable路径
        if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的环境
            executable_path = sys.executable
        else:
            # 开发环境
            executable_path = os.path.abspath(sys.argv[0])
        
        # 标准化路径
        normalized_path = normalize_path(executable_path)
        logger.debug(f"获取到可执行文件路径: {normalized_path}")
        return normalized_path
    except Exception as e:
        logger.error(f"获取可执行文件路径失败: {e}")
        raise RuntimeError(f"获取可执行文件路径失败: {e}")


def setup_signal_handlers(signal_handler) -> None:
    """
    设置信号处理器
    
    Args:
        signal_handler: 信号处理函数
    """
    logger = get_logger()
    try:
        # Windows平台信号处理
        if is_windows():
            # Windows支持的信号有限
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        else:
            # Unix/Linux平台信号处理
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGQUIT, signal_handler)
            signal.signal(signal.SIGHUP, signal_handler)
        
        logger.info("信号处理器设置完成")
    except Exception as e:
        logger.error(f"设置信号处理器失败: {e}")


def get_temp_directory() -> str:
    """
    获取平台适当的临时目录路径
    
    Returns:
        str: 临时目录路径
    """
    if is_windows():
        return os.environ.get('TEMP', '/tmp')
    else:
        return '/tmp'


def get_home_directory() -> str:
    """
    获取用户主目录路径
    
    Returns:
        str: 用户主目录路径
    """
    return str(Path.home())


def create_platform_specific_directory(directory_path: str) -> bool:
    """
    创建平台特定的目录
    
    Args:
        directory_path (str): 目录路径
        
    Returns:
        bool: 是否成功创建目录
    """
    logger = get_logger()
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {e}")
        return False


# 测试代码
if __name__ == "__main__":
    # 这里可以添加一些测试代码
    pass