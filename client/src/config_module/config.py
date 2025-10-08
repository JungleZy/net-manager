#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
统一管理NetManager客户端的所有配置项
"""

import os
from pathlib import Path

class ConfigManager:
    """配置管理器"""
    
    # UDP配置
    UDP_HOST = "<broadcast>"  # 广播地址
    UDP_PORT = 12345  # UDP端口（用于服务发现）
    
    # TCP配置
    TCP_PORT = 12346  # TCP端口（用于数据传输）
    
    # 数据收集间隔（秒）
    COLLECT_INTERVAL = 30
    
    # 日志配置
    LOG_LEVEL = "INFO"
    
    @staticmethod
    def get_log_file_path():
        """获取日志文件路径"""
        # 使用pathlib处理跨平台路径
        return Path(__file__).parent.parent.parent / "logs" / "net_manager_client.log"
    
    @staticmethod
    def get_state_file_path():
        """获取状态文件路径"""
        return "client_state.json"

# 创建全局配置管理器实例
config = ConfigManager()