#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为拓扑图添加大量测试节点（优化版）

网络架构：三层结构
- 核心层：防火墙 -> 核心交换机 -> 服务器
- 汇聚层：接入交换机连接到核心交换机
- 接入层：终端设备连接到接入交换机
"""

import json
import random
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime


def generate_core_infrastructure(start_id):
    """
    生成核心网络基础设施（防火墙、核心交换机、服务器）

    Args:
        start_id: 起始ID

    Returns:
        核心设备节点列表, 防火墙ID, 核心交换机ID
    """
    nodes = []

    # 网络架构布局（从上到下）：防火墙 -> 核心交换机 -> 服务器
    center_x = 1300  # 屏幕中心位置

    # 1. 防火墙（最上层，网络边界）
    firewall_node = {
        "id": str(start_id),
        "type": "firewall",
        "x": center_x,
        "y": 100,
        "properties": {"width": 80, "height": 80, "status": "online"},
        "text": {"x": center_x, "y": 100, "value": "核心防火墙"},
    }
    nodes.append(firewall_node)

    # 2. 核心交换机（中间层）
    core_switch_node = {
        "id": str(start_id + 1),
        "type": "switch",
        "x": center_x,
        "y": 300,
        "properties": {"width": 80, "height": 80, "status": "online"},
        "text": {"x": center_x, "y": 300, "value": "核心交换机"},
    }
    nodes.append(core_switch_node)

    # 3. 服务器（5台，排列在核心交换机附近）
    server_types = ["Web服务器", "DB服务器", "文件服务器", "邮件服务器", "应用服务器"]
    server_x_positions = [
        center_x - 400,
        center_x - 200,
        center_x,
        center_x + 200,
        center_x + 400,
    ]

    for i, (server_name, x_pos) in enumerate(zip(server_types, server_x_positions)):
        server_node = {
            "id": str(start_id + 2 + i),
            "type": "server",
            "x": x_pos,
            "y": 450,
            "properties": {
                "width": 60,
                "height": 60,
                "status": random.choice(["online", "offline"]),
            },
            "text": {"x": x_pos, "y": 450, "value": server_name},
        }
        nodes.append(server_node)

    return nodes, firewall_node["id"], core_switch_node["id"]


def generate_device_nodes(start_id, count):
    """
    生成终端设备节点（台式机、笔记本、打印机）

    Args:
        start_id: 起始ID
        count: 生成数量

    Returns:
        设备节点列表
    """
    nodes = []
    # 只包含终端设备类型（不包括服务器、防火墙、路由器）
    device_types = ["pc", "laptop", "printer"]
    device_names = {"pc": "台式机", "laptop": "笔记本", "printer": "打印机"}

    # 使用网格布局，便于查看
    cols = 20  # 每行20个节点
    x_offset = 150
    y_offset = 800  # 放在接入交换机下方
    x_spacing = 120
    y_spacing = 120

    for i in range(count):
        device_type = random.choice(device_types)
        node_id = str(start_id + i)

        # 计算网格位置
        row = i // cols
        col = i % cols
        x = x_offset + col * x_spacing
        y = y_offset + row * y_spacing

        # 随机状态
        status = random.choice(["online", "offline"])

        node = {
            "id": node_id,
            "type": device_type,
            "x": x,
            "y": y,
            "properties": {"width": 60, "height": 60, "status": status},
            "text": {"x": x, "y": y, "value": f"{device_names[device_type]}-{i+1}"},
        }
        nodes.append(node)

    return nodes


def generate_switch_nodes(start_id, count):
    """
    生成接入交换机节点

    Args:
        start_id: 起始ID
        count: 生成数量

    Returns:
        交换机节点列表
    """
    nodes = []

    # 接入交换机使用网格布局
    x_offset = 300
    y_offset = 600  # 放在核心交换机下方
    x_spacing = 200
    y_spacing = 150

    cols = 10  # 每行10个交换机

    for i in range(count):
        node_id = str(start_id + i)

        # 计算网格位置
        row = i // cols
        col = i % cols
        x = x_offset + col * x_spacing
        y = y_offset + row * y_spacing

        # 随机状态
        status = random.choice(["online", "offline"])

        node = {
            "id": node_id,
            "type": "switch",
            "x": x,
            "y": y,
            "properties": {"width": 60, "height": 60, "status": status},
            "text": {"x": x, "y": y, "value": f"接入交换机-{i+1}"},
        }
        nodes.append(node)

    return nodes


def generate_edges(device_nodes, switch_nodes, core_nodes, firewall_id, core_switch_id):
    """
    生成网络拓扑连接

    网络架构：
    - 防火墙 -> 核心交换机
    - 核心交换机 -> 所有服务器
    - 核心交换机 -> 所有接入交换机
    - 接入交换机 -> 终端设备

    Args:
        device_nodes: 终端设备节点列表
        switch_nodes: 接入交换机节点列表
        core_nodes: 核心设备节点列表
        firewall_id: 防火墙节点ID
        core_switch_id: 核心交换机节点ID

    Returns:
        边列表
    """
    edges = []
    import uuid

    # 1. 防火墙 -> 核心交换机
    firewall_node = next(n for n in core_nodes if n["id"] == firewall_id)
    core_switch_node = next(n for n in core_nodes if n["id"] == core_switch_id)

    edge = {
        "id": str(uuid.uuid4()),
        "type": "polyline",
        "properties": {},
        "sourceNodeId": firewall_id,
        "targetNodeId": core_switch_id,
        "sourceAnchorId": f"{firewall_id}_2",  # 底部锚点
        "targetAnchorId": f"{core_switch_id}_0",  # 顶部锚点
        "startPoint": {"x": firewall_node["x"], "y": firewall_node["y"]},
        "endPoint": {"x": core_switch_node["x"], "y": core_switch_node["y"]},
    }
    edges.append(edge)

    # 2. 核心交换机 -> 所有服务器
    server_nodes = [n for n in core_nodes if n["type"] == "server"]
    for server in server_nodes:
        edge = {
            "id": str(uuid.uuid4()),
            "type": "polyline",
            "properties": {},
            "sourceNodeId": core_switch_id,
            "targetNodeId": server["id"],
            "sourceAnchorId": f"{core_switch_id}_2",  # 底部锚点
            "targetAnchorId": f"{server['id']}_0",  # 顶部锚点
            "startPoint": {"x": core_switch_node["x"], "y": core_switch_node["y"]},
            "endPoint": {"x": server["x"], "y": server["y"]},
        }
        edges.append(edge)

    # 3. 核心交换机 -> 所有接入交换机
    for switch in switch_nodes:
        edge = {
            "id": str(uuid.uuid4()),
            "type": "polyline",
            "properties": {},
            "sourceNodeId": core_switch_id,
            "targetNodeId": switch["id"],
            "sourceAnchorId": f"{core_switch_id}_2",  # 底部锚点
            "targetAnchorId": f"{switch['id']}_0",  # 顶部锚点
            "startPoint": {"x": core_switch_node["x"], "y": core_switch_node["y"]},
            "endPoint": {"x": switch["x"], "y": switch["y"]},
        }
        edges.append(edge)

    # 4. 接入交换机 -> 终端设备（将设备平均分配到各个接入交换机）
    devices_per_switch = len(device_nodes) // len(switch_nodes)

    for i, device in enumerate(device_nodes):
        # 确定该设备连接到哪个接入交换机
        switch_index = min(i // devices_per_switch, len(switch_nodes) - 1)
        switch = switch_nodes[switch_index]

        # 随机选择锚点
        source_anchor = random.randint(0, 3)
        target_anchor = random.randint(0, 3)

        edge = {
            "id": str(uuid.uuid4()),
            "type": "polyline",
            "properties": {},
            "sourceNodeId": device["id"],
            "targetNodeId": switch["id"],
            "sourceAnchorId": f"{device['id']}_{source_anchor}",
            "targetAnchorId": f"{switch['id']}_{target_anchor}",
            "startPoint": {"x": device["x"], "y": device["y"]},
            "endPoint": {"x": switch["x"], "y": switch["y"]},
        }
        edges.append(edge)

    return edges


def main():
    """主函数"""
    print("=" * 80)
    print("为拓扑图添加测试节点（优化版 - 三层网络架构）")
    print("=" * 80)

    # 直接连接数据库
    db_path = "net_manager_server.db"

    if not os.path.exists(db_path):
        print(f"\n   ❌ 数据库文件不存在: {db_path}")
        return

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 获取最新的拓扑图
        print("\n1. 获取最新的拓扑图...")
        cursor.execute(
            """
            SELECT id, content, created_at
            FROM topology_info
            ORDER BY created_at DESC
            LIMIT 1
        """
        )

        row = cursor.fetchone()

        if not row:
            print("   ❌ 未找到拓扑图数据，请先创建一个拓扑图")
            return

        topology_id, content, created_at = row
        print(f"   ✓ 找到拓扑图 ID: {topology_id}")
        print(f"   ✓ 创建时间: {created_at}")

        # 解析现有内容
        try:
            existing_content = json.loads(content)
            existing_nodes = existing_content.get("nodes", [])
            existing_edges = existing_content.get("edges", [])
            print(f"   ✓ 现有节点数量: {len(existing_nodes)}")
            print(f"   ✓ 现有边数量: {len(existing_edges)}")
        except json.JSONDecodeError:
            print("   ❌ 拓扑图内容解析失败，使用空数据")
            existing_nodes = []
            existing_edges = []

        # 计算新节点的起始ID
        if existing_nodes:
            max_id = max(
                [int(node["id"]) for node in existing_nodes if node["id"].isdigit()]
                + [0]
            )
            start_id = max_id + 1
        else:
            start_id = 1

        print(f"\n2. 生成新节点（起始ID: {start_id}）...")

        # 生成核心网络基础设施（防火墙、核心交换机、服务器）
        print("   - 生成核心网络设施（防火墙、核心交换机、服务器）...")
        core_nodes, firewall_id, core_switch_id = generate_core_infrastructure(start_id)
        print(
            f"   ✓ 核心设施生成完成（{len(core_nodes)} 个：1个防火墙 + 1个核心交换机 + 5个服务器）"
        )

        # 更新起始ID
        current_id = start_id + len(core_nodes)

        # 生成终端设备节点（台式机、笔记本、打印机）
        print(f"   - 生成 300 个终端设备节点（台式机、笔记本、打印机）...")
        device_nodes = generate_device_nodes(current_id, 300)
        print(f"   ✓ 终端设备节点生成完成")

        # 更新起始ID
        current_id += 300

        # 生成20个接入交换机节点
        print("   - 生成 20 个接入交换机节点...")
        switch_nodes = generate_switch_nodes(current_id, 20)
        print(f"   ✓ 接入交换机节点生成完成")

        # 生成网络连接
        print("   - 生成网络拓扑连接...")
        new_edges = generate_edges(
            device_nodes, switch_nodes, core_nodes, firewall_id, core_switch_id
        )
        print(f"   ✓ 网络连接生成完成（共 {len(new_edges)} 条）")
        print(f"     - 防火墙 -> 核心交换机: 1 条")
        print(f"     - 核心交换机 -> 服务器: 5 条")
        print(f"     - 核心交换机 -> 接入交换机: 20 条")
        print(f"     - 接入交换机 -> 终端设备: {len(device_nodes)} 条")

        # 合并节点和边
        print("\n3. 合并数据...")
        all_nodes = existing_nodes + core_nodes + device_nodes + switch_nodes
        all_edges = existing_edges + new_edges

        print(
            f"   ✓ 总节点数: {len(all_nodes)} (原有: {len(existing_nodes)}, 新增: {len(core_nodes) + len(device_nodes) + len(switch_nodes)})"
        )
        print(f"     - 核心设施: {len(core_nodes)} 个 (防火墙 + 核心交换机 + 服务器)")
        print(f"     - 接入交换机: {len(switch_nodes)} 个")
        print(f"     - 终端设备: {len(device_nodes)} 个")
        print(
            f"   ✓ 总边数: {len(all_edges)} (原有: {len(existing_edges)}, 新增: {len(new_edges)})"
        )

        # 构建新的拓扑图数据
        new_topology_data = {"nodes": all_nodes, "edges": all_edges}

        # 转换为JSON字符串
        new_content = json.dumps(new_topology_data, ensure_ascii=False)

        # 更新数据库
        print(f"\n4. 更新数据库...")
        cursor.execute(
            """
            UPDATE topology_info SET content = ? WHERE id = ?
        """,
            (new_content, topology_id),
        )

        conn.commit()

        print(f"   ✓ 拓扑图更新成功！")
        print(f"\n统计信息:")
        print(f"   - 拓扑图ID: {topology_id}")
        print(f"\n网络架构（三层结构）:")
        print(f"   【核心层】")
        print(f"   - 防火墙: 1 个")
        print(f"   - 核心交换机: 1 个")
        print(f"   - 服务器: 5 个")
        print(f"   【汇聚层】")
        print(
            f"   - 接入交换机: {len([n for n in all_nodes if n['type'] == 'switch' and '接入' in n.get('text', {}).get('value', '')])} 个"
        )
        print(f"   【接入层】")
        print(
            f"   - 终端设备: {len([n for n in all_nodes if n['type'] in ['pc', 'laptop', 'printer']])} 个"
        )
        print(f"\n汇总:")
        print(f"   - 总节点数: {len(all_nodes)} 个")
        print(f"   - 总连接数: {len(all_edges)} 条")

    except Exception as e:
        print(f"\n   ❌ 错误: {e}")
        import traceback

        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

    print("\n" + "=" * 80)
    print("操作完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
