#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统信息模型 - 用于表示和存储系统信息数据
"""

from typing import List, Dict, Any

class SystemInfo:
    """系统信息模型"""
    
    def __init__(self, hostname: str, ip_address: str, mac_address: str, 
                 gateway: str, netmask: str, services: str, processes: str, 
                 timestamp: str, client_id: str = "", os_name: str = "", 
                 os_version: str = "", os_architecture: str = "", 
                 machine_type: str = "", type: str = ""):
        """
        初始化系统信息对象
        
        Args:
            hostname: 主机名
            ip_address: IP地址
            mac_address: MAC地址
            gateway: 网关地址
            netmask: 子网掩码
            services: 服务信息（JSON字符串）
            processes: 进程信息（JSON字符串）
            timestamp: 时间戳
            client_id: 客户端唯一标识符
            os_name: 操作系统名称
            os_version: 操作系统版本
            os_architecture: 操作系统架构
            machine_type: 机器类型
            type: 设备类型（计算机、交换机、服务器等）
        """
        self.hostname = hostname
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.gateway = gateway
        self.netmask = netmask
        self.services = services  # 存储为JSON字符串
        self.processes = processes  # 存储为JSON字符串
        self.timestamp = timestamp
        self.client_id = client_id  # 客户端唯一标识符
        self.os_name = os_name  # 操作系统名称
        self.os_version = os_version  # 操作系统版本
        self.os_architecture = os_architecture  # 操作系统架构
        self.machine_type = machine_type  # 机器类型
        self.type = type  # 设备类型（计算机、交换机、服务器等）

    def to_dict(self) -> Dict[str, Any]:
        """
        将系统信息转换为字典格式
        
        Returns:
            包含所有系统信息的字典
        """
        return {
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'gateway': self.gateway,
            'netmask': self.netmask,
            'services': self.services,
            'processes': self.processes,
            'timestamp': self.timestamp,
            'client_id': self.client_id,
            'os_name': self.os_name,
            'os_version': self.os_version,
            'os_architecture': self.os_architecture,
            'machine_type': self.machine_type,
            'type': self.type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemInfo':
        """
        从字典创建SystemInfo实例
        
        Args:
            data: 包含系统信息的字典
            
        Returns:
            SystemInfo实例
        """
        return cls(
            hostname=data.get('hostname', ''),
            ip_address=data.get('ip_address', ''),
            mac_address=data.get('mac_address', ''),
            gateway=data.get('gateway', ''),
            netmask=data.get('netmask', ''),
            services=data.get('services', ''),
            processes=data.get('processes', ''),
            timestamp=data.get('timestamp', ''),
            client_id=data.get('client_id', ''),
            os_name=data.get('os_name', ''),
            os_version=data.get('os_version', ''),
            os_architecture=data.get('os_architecture', ''),
            machine_type=data.get('machine_type', ''),
            type=data.get('type', '')
        )