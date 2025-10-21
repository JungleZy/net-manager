#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
常驻进程信息模型 - 用于表示和存储常驻进程数据
"""

from typing import Dict, Any, Optional


class ResidentProcessInfo:
    """常驻进程信息模型"""

    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        """
        初始化常驻进程信息对象

        Args:
            name: 进程名称
            id: 数据库主键（可选）
            created_at: 创建时间（可选）
        """
        self.name = name
        self.id = id if id is not None else ""
        self.created_at = created_at if created_at is not None else ""

    def to_dict(self) -> Dict[str, Any]:
        """
        将常驻进程信息转换为字典格式

        Returns:
            包含所有常驻进程信息的字典
        """
        return {
            "id": self.id,
            "content": self.name,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResidentProcessInfo":
        """
        从字典创建ResidentProcessInfo实例

        Args:
            data: 包含常驻进程信息的字典

        Returns:
            ResidentProcessInfo实例
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            created_at=data.get("created_at", ""),
        )
