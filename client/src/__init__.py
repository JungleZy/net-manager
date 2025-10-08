#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
客户端主模块
提供客户端核心功能的统一接口
"""

# 系统模块导入
# 无

# 第三方库导入
# 无

# 本地应用/库导入
# 系统相关模块
from .system.autostart import (
    enable_autostart,
    disable_autostart,
    is_autostart_enabled,
    create_daemon_script
)

# 工具模块
from .utils.platform_utils import (
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

from .utils.logger import (
    get_logger,
    setup_logger
)

from .network import TCPClient

# 异常模块
from .exceptions.exceptions import (
    NetManagerError,
    ConfigurationError,
    PlatformError,
    AutoStartError
)

# 定义模块的公共接口
__all__ = [
    # 系统相关功能
    "enable_autostart",
    "disable_autostart",
    "is_autostart_enabled",
    "create_daemon_script",
    
    # 工具函数
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
    "get_logger",
    "setup_logger",
    
    # 网络功能
    "TCPClient",
    
    # 异常类
    "NetManagerError",
    "ConfigurationError",
    "PlatformError",
    "AutoStartError"
]