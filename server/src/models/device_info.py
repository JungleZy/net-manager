#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统信息模型 - 用于表示和存储系统信息数据
"""

from typing import List, Dict, Any

class DeviceInfo:
    """设备信息模型"""
    
    def __init__(self,id: str,
                 client_id: str,
                 hostname: str,
                 os_name: str, 
                 os_version: str, 
                 os_architecture: str, 
                 machine_type: str, 
                 services: str, 
                 processes: str, 
                 networks: str, 
                 timestamp: str = "", 
                 cpu_info: str = "", 
                 memory_info: str = "", 
                 disk_info: str = "", 
                 type: str = "",
                 created_at: str = ""):
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
            created_at: 创建时间
        """
        self.id = id # 数据库主键
        self.client_id = client_id # 客户端唯一标识符
        self.hostname = hostname # 主机名
        self.os_name = os_name # 操作系统名称
        self.os_version = os_version # 操作系统版本
        self.os_architecture = os_architecture # 操作系统架构
        self.machine_type = machine_type # 机器类型
        self.services = services # 服务信息（JSON字符串）
        self.processes = processes # 进程信息（JSON字符串）
        self.networks = networks # 网络信息（JSON字符串）
        self.timestamp = timestamp # 时间戳
        self.cpu_info = cpu_info # CPU信息（JSON字符串）
        self.memory_info = memory_info # 内存信息（JSON字符串）
        self.disk_info = disk_info # 磁盘信息（JSON字符串）
        self.type = type # 设备类型（计算机、交换机、服务器等）
        self.created_at = created_at # 创建时间

    def to_dict(self) -> Dict[str, Any]:
        """
        将系统信息转换为字典格式
        
        Returns:
            包含所有系统信息的字典
        """
        return {
            'id': self.id,
            'client_id': self.client_id,
            'hostname': self.hostname,
            'os_name': self.os_name,
            'os_version': self.os_version,
            'os_architecture': self.os_architecture,
            'machine_type': self.machine_type,
            'services': self.services,
            'processes': self.processes,
            'networks': self.networks,
            'timestamp': self.timestamp,
            'cpu_info': self.cpu_info,
            'memory_info': self.memory_info,
            'disk_info': self.disk_info,
            'type': self.type,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceInfo':
        """
        从字典创建DeviceInfo实例
        
        Args:
            data: 包含系统信息的字典
            
        Returns:
            DeviceInfo实例
        """
        return cls(
            id=data.get('id', ''),
            client_id=data.get('client_id', ''),
            hostname=data.get('hostname', ''),
            os_name=data.get('os_name', ''),
            os_version=data.get('os_version', ''),
            os_architecture=data.get('os_architecture', ''),
            machine_type=data.get('machine_type', ''),
            services=data.get('services', ''),
            processes=data.get('processes', ''),
            networks=data.get('networks', ''),
            timestamp=data.get('timestamp', ''),
            cpu_info=data.get('cpu_info', ''),
            memory_info=data.get('memory_info', ''),
            disk_info=data.get('disk_info', ''),
            type=data.get('type', ''),
            created_at=data.get('created_at', '')
        )