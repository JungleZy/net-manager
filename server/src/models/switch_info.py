#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交换机信息模型 - 用于表示和存储交换机SNMP配置信息
"""

from typing import Dict, Any, Optional
from datetime import datetime


class SwitchInfo:
    """交换机信息模型"""

    def __init__(
        self,
        ip: str,
        snmp_version: str,
        community: str = "",
        user: str = "",
        auth_key: str = "",
        auth_protocol: str = "",
        priv_key: str = "",
        priv_protocol: str = "",
        description: str = "",
        device_name: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[int] = None,
    ):
        """
        初始化交换机信息对象

        Args:
            id: 数据库ID（可选）
            ip: 交换机IP地址
            snmp_version: SNMP版本（如'1', '2c', '3'）
            community: SNMP community字符串（用于v1/v2c）
            user: SNMPv3用户名
            auth_key: SNMPv3认证密钥
            auth_protocol: SNMPv3认证协议（如'MD5', 'SHA'）
            priv_key: SNMPv3隐私密钥
            priv_protocol: SNMPv3隐私协议（如'DES', 'AES'）
            description: 交换机描述信息
            device_name: 设备名称
            created_at: 创建时间（可选）
            updated_at: 更新时间（可选）
        """
        self.id = id
        self.ip = ip
        self.snmp_version = snmp_version
        self.community = community
        self.user = user
        self.auth_key = auth_key
        self.auth_protocol = auth_protocol
        self.priv_key = priv_key
        self.priv_protocol = priv_protocol
        self.description = description
        self.device_name = device_name
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        将交换机信息转换为字典格式

        Returns:
            包含所有交换机信息的字典
        """
        return {
            "id": self.id,
            "ip": self.ip,
            "snmp_version": self.snmp_version,
            "community": self.community,
            "user": self.user,
            "auth_key": self.auth_key,
            "auth_protocol": self.auth_protocol,
            "priv_key": self.priv_key,
            "priv_protocol": self.priv_protocol,
            "description": self.description,
            "device_name": self.device_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SwitchInfo":
        """
        从字典创建SwitchInfo实例

        Args:
            data: 包含交换机信息的字典

        Returns:
            SwitchInfo实例
        """
        return cls(
            id=data.get("id"),
            ip=data.get("ip", ""),
            snmp_version=data.get("snmp_version", ""),
            community=data.get("community", ""),
            user=data.get("user", ""),
            auth_key=data.get("auth_key", ""),
            auth_protocol=data.get("auth_protocol", ""),
            priv_key=data.get("priv_key", ""),
            priv_protocol=data.get("priv_protocol", ""),
            description=data.get("description", ""),
            device_name=data.get("device_name", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __str__(self) -> str:
        """返回交换机信息的字符串表示"""
        return f"SwitchInfo(ip={self.ip}, snmp_version={self.snmp_version}, description={self.description}, device_name={self.device_name})"

    def __repr__(self) -> str:
        """返回交换机信息的详细字符串表示"""
        return self.__str__()
