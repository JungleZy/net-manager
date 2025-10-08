#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
统一管理NetManager客户端的所有配置项
"""

import os
import json
from pathlib import Path

class ConfigManager:
    """配置管理器"""
    
    # UDP配置
    UDP_HOST = "<broadcast>"  # 广播地址
    UDP_PORT = 12345  # UDP端口（用于服务发现）
    
    # TCP配置
    TCP_PORT = 12346  # TCP端口（用于数据传输）
    
    # 数据收集间隔（秒）
    COLLECT_INTERVAL = 10
    
    def __init__(self):
        """初始化配置管理器并从状态文件加载配置"""
        # 获取日志记录器
        self._load_config_from_state()
        print("状态控制器初始化完成11")
    
    def _load_config_from_state(self):
        """从状态文件加载配置"""
        try:
            # 获取状态文件路径
            state_file_path = self.get_state_file_path()
            
            # 检查状态文件是否存在
            if os.path.exists(state_file_path):
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    
                # 从状态文件读取配置，如果不存在则使用默认值
                udp_port = state_data.get('udp_port', self.UDP_PORT)
                self.UDP_PORT = int(udp_port) if isinstance(udp_port, str) else udp_port
                tcp_port = state_data.get('tcp_port', self.TCP_PORT)
                self.TCP_PORT = int(tcp_port) if isinstance(tcp_port, str) else tcp_port
                self.COLLECT_INTERVAL = state_data.get('collect_interval', self.COLLECT_INTERVAL)
            # 如果状态文件不存在，保持默认配置不变
        except Exception as e:
            # 出现异常时保持默认配置不变
            pass
    
    # 日志配置
    LOG_LEVEL = "INFO"
    
    # 默认配置值
    _default_config = {
        'logging': {
            'level': 'INFO',
            'file': 'logs/net_manager_client.log'
        },
        'client': {
            'autostart': False
        }
    }
    
    def get(self, section, key, default=None):
        """
        获取配置值
        
        Args:
            section (str): 配置节名称
            key (str): 配置项名称
            default (any): 默认值
            
        Returns:
            any: 配置值或默认值
        """
        # 首先检查是否有对应的类属性
        if section == 'logging':
            if key == 'level':
                return self.LOG_LEVEL
            elif key == 'file':
                return str(self.get_log_file_path())
        elif section == 'client':
            if key == 'autostart':
                # 从默认配置中获取
                return self._default_config.get(section, {}).get(key, default)
        
        # 如果没有对应的类属性，从默认配置中获取
        return self._default_config.get(section, {}).get(key, default)
    
    def get_server_broadcast_address(self):
        """
        获取服务端广播地址
        
        Returns:
            str: 服务端广播地址
        """
        return self.UDP_HOST
    
    def get_server_broadcast_port(self):
        """
        获取服务端广播端口
        
        Returns:
            int: 服务端广播端口
        """
        # 确保返回整数类型的端口
        return int(self.UDP_PORT)
    
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

# 重新导出配置值，确保它们反映实例的值
UDP_HOST = config.UDP_HOST
UDP_PORT = config.UDP_PORT
TCP_PORT = config.TCP_PORT
COLLECT_INTERVAL = config.COLLECT_INTERVAL