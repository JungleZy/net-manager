# -*- coding: utf-8 -*-
"""
Models module package initialization.

This package contains data models for the network management server.
"""

# Import model classes for easier access
from src.models.device_info import DeviceInfo
from src.models.switch_info import SwitchInfo

__all__ = [
    'DeviceInfo',  
    'SwitchInfo'
]

__version__ = '1.0.0'