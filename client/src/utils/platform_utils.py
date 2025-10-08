#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""
"""
处理Windows和Linux系统之间的差异
"""

import os
import sys
import platform
import signal
from src.utils.logger import logger

def get_platform():
    """获取当前操作系统平台"""
    return platform.system().lower()

def is_windows():
    """检查是否为Windows系统"""
    return get_platform() == 'windows'

def is_linux():
    """检查是否为Linux系统"""
    return get_platform() == 'linux'

def get_path_separator():
    """获取当前系统的路径分隔符"""
    return os.sep

def get_line_separator():
    """获取当前系统的行分隔符"""
    if is_windows():
        return '\r\n'
    else:
        return '\n'

def setup_signal_handlers(signal_handler):
    """设置信号处理器"""
    try:
        # 设置SIGINT信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        logger.info("SIGINT信号处理器设置成功")
        
        # 在非Windows系统上设置SIGTERM信号处理器
        if not is_windows():
            signal.signal(signal.SIGTERM, signal_handler)
            logger.info("SIGTERM信号处理器设置成功")
        
        logger.info("信号处理器设置成功")
    except ValueError as e:
        logger.error(f"信号处理器设置失败（可能在非主线程中）: {e}")
        # 在非主线程中设置信号处理器可能会失败，这是可以接受的
    except Exception as e:
        logger.error(f"设置信号处理器失败: {e}")
        raise

def get_appropriate_encoding():
    """获取适合当前平台的文本编码"""
    if is_windows():
        return 'gbk'  # Windows中文系统通常使用GBK编码
    else:
        return 'utf-8'  # Linux/macOS通常使用UTF-8编码

def normalize_path(path):
    """标准化路径，确保在不同平台上正确处理"""
    return os.path.normpath(path)

def get_executable_path():
    """获取可执行文件路径"""
    return os.path.dirname(os.path.abspath(sys.argv[0]))

def create_platform_specific_directory(dir_path):
    """创建平台特定的目录"""
    try:
        # 确保目录存在
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录 {dir_path} 失败: {e}")
        return False