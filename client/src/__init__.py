# -*- coding: utf-8 -*-

"""
客户端源代码包
"""

# 导出主要模块
from .singleton_manager import get_client_singleton_manager
from .state_manager import get_state_manager

__all__ = [
    'get_client_singleton_manager',
    'get_state_manager',
]