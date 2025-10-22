# -*- coding: utf-8 -*-
"""
Core module package initialization.

This package contains core functionality for the network management server,
including configuration, logging, and state management.
"""

# Import core components for easier access
from .config import (
    VERSION,
    UDP_HOST,
    UDP_PORT,
    TCP_PORT,
    API_HOST,
    API_PORT,
    LOG_LEVEL,
    LOG_FILE,
    SERVER_MONITOR_INTERVAL,
)
from .logger import logger
from .state_manager import state_manager
from .singleton_manager import get_server_singleton_manager


def get_state_manager():
    """获取全局状态管理器实例"""
    return state_manager


__all__ = [
    "VERSION",
    "UDP_HOST",
    "UDP_PORT",
    "TCP_PORT",
    "API_HOST",
    "API_PORT",
    "LOG_LEVEL",
    "LOG_FILE",
    "SERVER_MONITOR_INTERVAL",
    "logger",
    "get_state_manager",
    "get_server_singleton_manager",
]

__version__ = "1.0.0"
