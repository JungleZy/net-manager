#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统信息模型 - 用于表示和存储系统信息数据
"""

from typing import List, Dict, Any, Optional


class DeviceInfo:
    """设备信息模型"""

    def __init__(
        self,
        client_id: str,
        hostname: str,
        os_name: str,
        os_version: str,
        os_architecture: str,
        machine_type: str,
        id: Optional[str] = None,
        services: Optional[str] = None,
        processes: Optional[str] = None,
        networks: Optional[str] = None,
        timestamp: Optional[str] = None,
        alias: Optional[str] = None,
        **kwargs
    ):
        """
        初始化系统信息对象

        Args:
            client_id: 客户端唯一标识符（必需）
            hostname: 主机名（必需）
            os_name: 操作系统名称（必需）
            os_version: 操作系统版本（必需）
            os_architecture: 操作系统架构（必需）
            machine_type: 机器类型（必需）
            id: 数据库主键（可选）
            services: 服务信息（JSON字符串，可选）
            processes: 进程信息（JSON字符串，可选）
            networks: 网络信息（JSON字符串，可选）
            timestamp: 时间戳（可选）
            **kwargs: 其他可选参数
                - cpu_info: CPU信息（JSON字符串）
                - memory_info: 内存信息（JSON字符串）
                - disk_info: 磁盘信息（JSON字符串）
                - type: 设备类型（计算机、交换机、服务器等）
                - alias: 设备别名（可选）
                - created_at: 创建时间
        """
        # 必需参数
        self.client_id = client_id
        self.hostname = hostname
        self.os_name = os_name
        self.os_version = os_version
        self.os_architecture = os_architecture
        self.machine_type = machine_type

        # 可选参数（有默认值）
        self.id = id if id is not None else ""
        self.services = services if services is not None else ""
        self.processes = processes if processes is not None else ""
        self.networks = networks if networks is not None else ""
        self.timestamp = timestamp if timestamp is not None else ""
        self.alias = alias if alias is not None else ""

        # 通过 kwargs 传入的其他可选参数
        self.cpu_info = kwargs.get("cpu_info", "")
        self.memory_info = kwargs.get("memory_info", "")
        self.disk_info = kwargs.get("disk_info", "")
        self.type = kwargs.get("type", "")
        self.created_at = kwargs.get("created_at", "")
        # 注意：alias 只能通过 UpdateHandler 修改，不从 kwargs 读取

    def to_dict(self) -> Dict[str, Any]:
        """
        将系统信息转换为字典格式

        Returns:
            包含所有系统信息的字典
        """
        return {
            "id": self.id,
            "client_id": self.client_id,
            "hostname": self.hostname,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "os_architecture": self.os_architecture,
            "machine_type": self.machine_type,
            "services": self.services,
            "processes": self.processes,
            "networks": self.networks,
            "timestamp": self.timestamp,
            "cpu_info": self.cpu_info,
            "memory_info": self.memory_info,
            "disk_info": self.disk_info,
            "type": self.type,
            "alias": self.alias,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceInfo":
        """
        从字典创建DeviceInfo实例

        Args:
            data: 包含系统信息的字典

        Returns:
            DeviceInfo实例
        """
        return cls(
            id=data.get("id", ""),
            client_id=data.get("client_id", ""),
            hostname=data.get("hostname", ""),
            os_name=data.get("os_name", ""),
            os_version=data.get("os_version", ""),
            os_architecture=data.get("os_architecture", ""),
            machine_type=data.get("machine_type", ""),
            services=data.get("services", ""),
            processes=data.get("processes", ""),
            networks=data.get("networks", ""),
            timestamp=data.get("timestamp", ""),
            cpu_info=data.get("cpu_info", ""),
            memory_info=data.get("memory_info", ""),
            disk_info=data.get("disk_info", ""),
            type=data.get("type", ""),
            alias=data.get("alias", ""),
            created_at=data.get("created_at", ""),
        )
