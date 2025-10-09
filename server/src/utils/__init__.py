# -*- coding: utf-8 -*-
"""
Utils module package initialization.

This package contains utility functions for the network management server.
"""

# Import utility functions for easier access
from src.utils.platform_utils import (
    get_platform,
    is_windows,
    is_linux,
    get_path_separator,
    get_line_separator,
    get_appropriate_encoding,
    setup_signal_handlers
)

__all__ = [
    'get_platform',
    'is_windows',
    'is_linux',
    'get_path_separator',
    'get_line_separator',
    'get_appropriate_encoding',
    'setup_signal_handlers'
]

__version__ = '1.0.0'