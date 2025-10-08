# -*- coding: utf-8 -*-

"""
工具模块
"""

# 导出工具模块
from src.utils.logger import setup_logger, get_logger
from src.utils.platform_utils import get_platform as get_platform_info, is_linux, is_windows, get_appropriate_encoding as get_system_encoding
from src.utils.singleton_manager import get_client_singleton_manager
from src.utils.unique_id import generate_unique_id

# 添加缺失的函数
def is_macos():
    """检查是否为macOS系统"""
    from src.utils.platform_utils import get_platform
    return get_platform() == 'darwin'

__all__ = [
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