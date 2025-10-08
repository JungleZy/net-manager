# -*- coding: utf-8 -*-

"""
客户端源代码包
"""

# 从各个子模块导入功能
from .config_module import config, ConfigManager
from .core import get_state_manager, start_net_manager
from .exceptions import (
    NetManagerError,
    NetworkDiscoveryError,
    NetworkConnectionError,
    DataCollectionError,
    SystemCommandError,
    ConfigurationError,
    StateUpdateError,
    NetworkTimeoutError
)
from .network import TCPClient
from .system import (
    add_to_autostart,
    remove_from_autostart,
    is_autostart_enabled,
    SystemInfoCollector
)
from .utils import (
    setup_logger,
    get_logger,
    get_platform_info,
    is_linux,
    is_windows,
    is_macos,
    get_system_encoding,
    get_client_singleton_manager,
    generate_unique_id,
)

__all__ = [
    # 配置模块
    'config',
    'ConfigManager',
    
    # 核心模块
    'get_state_manager',
    'start_net_manager',
    
    # 异常模块
    'NetManagerError',
    'NetworkDiscoveryError',
    'NetworkConnectionError',
    'DataCollectionError',
    'SystemCommandError',
    'ConfigurationError',
    'StateUpdateError',
    'NetworkTimeoutError',
    
    # 网络模块
    'TCPClient',
    
    # 系统模块
    'add_to_autostart',
    'remove_from_autostart',
    'is_autostart_enabled',
    'SystemInfoCollector',
    
    # 工具模块
    'setup_logger',
    'get_logger',
    'get_platform_info',
    'is_linux',
    'is_windows',
    'is_macos',
    'get_system_encoding',
    'get_client_singleton_manager',
    'generate_unique_id',
]