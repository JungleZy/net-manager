# -*- coding: utf-8 -*-

"""
系统模块
"""

# 导出系统模块
from .autostart import enable_autostart as add_to_autostart, disable_autostart as remove_from_autostart, is_autostart_enabled
from .system_collector import SystemCollector as SystemInfoCollector

__all__ = [
    'add_to_autostart',
    'remove_from_autostart',
    'is_autostart_enabled',
    'SystemInfoCollector',
]