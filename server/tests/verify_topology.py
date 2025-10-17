#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

# 连接数据库
conn = sqlite3.connect("net_manager_server.db")
cursor = conn.cursor()

# 查询最新的拓扑图
cursor.execute(
    """
    SELECT id, created_at, length(content)
    FROM topology_info
    ORDER BY created_at DESC
    LIMIT 1
"""
)

row = cursor.fetchone()
if row:
    topology_id, created_at, content_size = row
    print(f"拓扑图ID: {topology_id}")
    print(f"创建时间: {created_at}")
    print(f"内容大小: {content_size} 字节")

    # 获取内容
    cursor.execute("SELECT content FROM topology_info WHERE id = ?", (topology_id,))
    content_str = cursor.fetchone()[0]
    content = json.loads(content_str)

    nodes = content.get("nodes", [])
    edges = content.get("edges", [])

    print(f"\n节点数量: {len(nodes)}")
    print(f"边数量: {len(edges)}")

    # 统计设备类型
    device_types = {}
    for node in nodes:
        node_type = node.get("type", "unknown")
        device_types[node_type] = device_types.get(node_type, 0) + 1

    print(f"\n设备类型统计:")
    for device_type, count in sorted(device_types.items()):
        print(f"  - {device_type}: {count} 个")
else:
    print("未找到拓扑图数据")

conn.close()
