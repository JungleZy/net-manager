#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑图信息模型 - 用于表示和存储拓扑图数据
"""

from typing import Dict, Any, Optional


class TopologyInfo:
    """拓扑图信息模型"""

    def __init__(
        self,
        content: str,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        """
        初始化拓扑图信息对象

        Args:
            content: 拓扑图内容（JSON字符串，包含节点和连接信息）
            id: 数据库主键（可选）
            created_at: 创建时间（可选）
        """
        self.content = content
        self.id = id if id is not None else ""
        self.created_at = created_at if created_at is not None else ""

    def to_dict(self) -> Dict[str, Any]:
        """
        将拓扑图信息转换为字典格式

        Returns:
            包含所有拓扑图信息的字典
        """
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopologyInfo":
        """
        从字典创建TopologyInfo实例

        Args:
            data: 包含拓扑图信息的字典

        Returns:
            TopologyInfo实例
        """
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            created_at=data.get("created_at", ""),
        )
