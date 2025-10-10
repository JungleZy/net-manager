# -*- coding: utf-8 -*-
"""
Core module package initialization.

This package contains core functionality for the network management server,
including configuration, logging, and singleton management.
"""

# Import core components for easier access
from src.core.config import VERSION, UDP_HOST, UDP_PORT, TCP_PORT, API_PORT, LOG_LEVEL, LOG_FILE
from src.core.logger import logger, setup_logger, get_log_level
from src.core.singleton_manager import SingletonManager, get_server_singleton_manager
from src.core.state_manager import StateManager, state_manager

__all__ = [
    'VERSION',
    'UDP_HOST',
    'UDP_PORT',
    'TCP_PORT',
    'API_PORT',
    'LOG_LEVEL',
    'LOG_FILE',
    'logger',
    'setup_logger',
    'get_log_level',
    'SingletonManager',
    'get_server_singleton_manager',
    'StateManager',
    'state_manager',
]

__version__ = '1.0.0'