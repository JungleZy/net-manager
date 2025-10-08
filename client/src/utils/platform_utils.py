#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
处理跨平台系统差异的工具模块
提供统一接口来处理Windows、Linux等不同操作系统的差异性
"""

import platform
import os
import sys
import signal
import locale
from typing import Optional, Callable, Any
from ..exceptions.exceptions import ConfigurationError
# from ..config import config
# from ..utils.logger import get_logger

# logger = get_logger()

def get_platform() -> str:
    """
    获取当前操作系统平台
    
    Returns:
        str: 操作系统平台名称（小写）
    """
    return platform.system().lower()

def is_windows() -> bool:
    """
    检查是否为Windows系统
    
    Returns:
        bool: 是Windows系统返回True，否则返回False
    """
    return get_platform() == "windows"

def is_linux() -> bool:
    """
    检查是否为Linux系统
    
    Returns:
        bool: 是Linux系统返回True，否则返回False
    """
    return get_platform() == "linux"

def is_macos() -> bool:
    """
    检查是否为macOS系统
    
    Returns:
        bool: 是macOS系统返回True，否则返回False
    """
    return get_platform() == "darwin"

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

def setup_signal_handlers(handler: Callable[[int, Any], None]) -> None:
    """
    设置信号处理器
    
    Args:
        handler: 信号处理函数
        
    Raises:
        ConfigurationError: 信号处理设置失败
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        # SIGINT (Ctrl+C) 在所有平台都支持
        signal.signal(signal.SIGINT, handler)
        
        # SIGTERM 在非Windows平台支持
        if not is_windows():
            signal.signal(signal.SIGTERM, handler)
            
        logger.debug("信号处理器设置成功")
    except Exception as e:
        logger.error(f"设置信号处理器失败: {e}")
        raise ConfigurationError(f"设置信号处理器失败: {e}")

def get_appropriate_encoding() -> str:
    """
    获取适合当前平台的编码
    
    Returns:
        str: 适合当前平台的编码
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        if is_windows():
            # 尝试获取控制台编码
            try:
                encoding = sys.stdout.encoding or locale.getpreferredencoding()
                if encoding:
                    return encoding
            except:
                pass
            return 'gbk'  # Windows中文系统通常使用gbk编码
        else:
            # Unix-like系统通常使用utf-8编码
            try:
                encoding = locale.getpreferredencoding() or 'utf-8'
                return encoding
            except:
                return 'utf-8'
    except Exception as e:
        logger.warning(f"获取平台编码失败，使用默认编码: {e}")
        return 'utf-8' if not is_windows() else 'gbk'

def normalize_path(path: str) -> str:
    """
    标准化路径
    
    Args:
        path (str): 原始路径
        
    Returns:
        str: 标准化后的路径
        
    Raises:
        ConfigurationError: 路径标准化失败
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        # 处理None或空路径
        if not path:
            return ""
        
        # 展开用户目录
        path = os.path.expanduser(path)
        
        # 标准化路径
        normalized = os.path.normpath(path)
        
        # 在Windows上处理路径大小写
        if is_windows():
            normalized = normalized.lower()
            
        return normalized
    except Exception as e:
        logger.error(f"路径标准化失败: {e}")
        raise ConfigurationError(f"路径标准化失败: {e}")

def get_executable_path() -> str:
    """
    获取可执行文件路径
    
    Returns:
        str: 可执行文件路径
        
    Raises:
        ConfigurationError: 获取可执行文件路径失败
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        is_frozen = hasattr(sys, 'frozen') and sys.frozen
        is_nuitka = '__compiled__' in globals()
        if is_frozen or is_nuitka:
            # 打包后的可执行文件 (PyInstaller)
            executable_path = sys.executable
        elif '__compiled__' in globals():
            # Nuitka编译后的程序
            executable_path = os.path.abspath(sys.argv[0])
        else:
            # Python脚本
            executable_path = os.path.abspath(sys.argv[0])  # 使用argv[0]更准确
            
        # 标准化路径
        executable_path = normalize_path(executable_path)
        logger.debug(f"获取到可执行文件路径: {executable_path}")
        return executable_path
    except Exception as e:
        logger.error(f"获取可执行文件路径失败: {e}")
        raise ConfigurationError(f"获取可执行文件路径失败: {e}")

def create_platform_specific_directory(dir_path: str) -> bool:
    """
    创建平台特定目录
    
    Args:
        dir_path (str): 目录路径
        
    Returns:
        bool: 创建成功返回True，否则返回False
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        # 标准化路径
        dir_path = normalize_path(dir_path)
        
        # 检查路径是否为空
        if not dir_path:
            logger.warning("目录路径为空，无法创建")
            return False
            
        # 检查父目录权限
        parent_dir = os.path.dirname(dir_path)
        if parent_dir and not os.path.exists(parent_dir):
            logger.debug(f"父目录不存在，先创建父目录: {parent_dir}")
            os.makedirs(parent_dir, exist_ok=True)
            
        # 创建目录
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"成功创建目录: {dir_path}")
        return True
    except PermissionError as e:
        logger.error(f"权限不足，无法创建目录 {dir_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"创建目录失败 {dir_path}: {e}")
        return False

def get_temp_directory() -> str:
    """
    获取临时目录路径
    
    Returns:
        str: 临时目录路径
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        # 获取系统临时目录
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        # 标准化路径
        temp_dir = normalize_path(temp_dir)
        
        # 确保临时目录存在
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
            
        return temp_dir
    except Exception as e:
        logger.warning(f"获取临时目录失败，使用当前目录: {e}")
        return os.getcwd()

def get_home_directory() -> str:
    """
    获取用户主目录路径
    
    Returns:
        str: 用户主目录路径
    """
    # 延迟导入logger以避免循环依赖
    from ..utils.logger import get_logger
    logger = get_logger()
    
    try:
        # 获取用户主目录
        home_dir = os.path.expanduser("~")
        
        # 标准化路径
        home_dir = normalize_path(home_dir)
        
        # 确保主目录存在
        if not os.path.exists(home_dir):
            os.makedirs(home_dir, exist_ok=True)
            
        return home_dir
    except Exception as e:
        logger.warning(f"获取用户主目录失败，使用当前目录: {e}")
        return os.getcwd()