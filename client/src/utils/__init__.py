#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
客户端工具模块
提供各种工具函数的统一接口
"""

# 从各个子模块导入功能
from .platform_utils import (
    get_platform,
    is_windows,
    is_linux,
    get_appropriate_encoding,
    normalize_path,
    get_executable_path,
    setup_signal_handlers,
    get_temp_directory,
    get_home_directory,
    create_platform_specific_directory
)

from .logger import (
    get_logger,
    setup_logger
)

# 定义模块的公共接口
__all__ = [
    # 平台工具函数
    "get_platform",
    "is_windows",
    "is_linux",
    "get_appropriate_encoding",
    "normalize_path",
    "get_executable_path",
    "setup_signal_handlers",
    "get_temp_directory",
    "get_home_directory",
    "create_platform_specific_directory",
    
    # 日志工具函数
    "get_logger",
    "setup_logger"
]