# -*- coding: utf-8 -*-
"""
Database module package initialization.

This package contains database management functionality for the network management server,
including database operations and exception handling.
"""

# Import database components for easier access
from .database_manager import DatabaseManager
from .db_exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseInitializationError,
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError
)

__all__ = [
    'DatabaseManager',
    'DatabaseError',
    'DatabaseConnectionError',
    'DatabaseInitializationError',
    'DatabaseQueryError',
    'DeviceNotFoundError',
    'DeviceAlreadyExistsError'
]

__version__ = '1.0.0'