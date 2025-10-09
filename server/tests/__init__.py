# -*- coding: utf-8 -*-
"""
Tests module package initialization.

This package contains all test modules for the network management server.
"""

# Import test classes for easier access
from tests.test_database_manager import TestDatabaseManager
from tests.test_switch_info import TestSwitchInfoModel, TestSwitchDatabaseOperations

__all__ = [
    'TestDatabaseManager',
    'TestSwitchInfoModel',
    'TestSwitchDatabaseOperations'
]

__version__ = '1.0.0'