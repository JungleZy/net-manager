#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑图管理器使用示例

演示如何使用TopologyManager进行拓扑图信息的增删改查操作。
"""

import json
from src.database.managers.topology_manager import TopologyManager
from src.models.topology_info import TopologyInfo


def main():
    """主函数"""
    # 创建拓扑图管理器实例
    topology_manager = TopologyManager(db_path="net_manager_server.db")

    print("=" * 60)
    print("拓扑图管理器使用示例")
    print("=" * 60)

    # 1. 创建示例拓扑图数据
    print("\n1. 保存拓扑图信息")
    topology_data = {
        "nodes": [
            {"id": "1", "type": "router", "label": "核心路由器", "x": 100, "y": 100},
            {"id": "2", "type": "switch", "label": "交换机1", "x": 200, "y": 200},
            {"id": "3", "type": "pc", "label": "电脑1", "x": 300, "y": 300},
        ],
        "edges": [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
        ],
    }

    # 转换为JSON字符串
    content = json.dumps(topology_data, ensure_ascii=False)

    # 创建TopologyInfo对象
    topology_info = TopologyInfo(content=content)

    # 保存到数据库
    topology_id = topology_manager.save_topology(topology_info)
    print(f"   保存成功，拓扑图ID: {topology_id}")

    # 2. 查询拓扑图总数
    print("\n2. 查询拓扑图总数")
    count = topology_manager.get_topology_count()
    print(f"   拓扑图总数: {count}")

    # 3. 根据ID查询拓扑图
    print(f"\n3. 根据ID查询拓扑图 (ID: {topology_id})")
    topology = topology_manager.get_topology_by_id(topology_id)
    if topology:
        print(f"   ID: {topology['id']}")
        print(f"   创建时间: {topology['created_at']}")
        print(f"   内容: {topology['content'][:100]}...")

    # 4. 查询最新的拓扑图
    print("\n4. 查询最新的拓扑图")
    latest_topology = topology_manager.get_latest_topology()
    if latest_topology:
        print(f"   ID: {latest_topology['id']}")
        print(f"   创建时间: {latest_topology['created_at']}")

    # 5. 更新拓扑图内容
    print(f"\n5. 更新拓扑图内容 (ID: {topology_id})")
    updated_data = {
        "nodes": [
            {"id": "1", "type": "router", "label": "核心路由器", "x": 100, "y": 100},
            {"id": "2", "type": "switch", "label": "交换机1", "x": 200, "y": 200},
            {"id": "3", "type": "pc", "label": "电脑1", "x": 300, "y": 300},
            {"id": "4", "type": "server", "label": "服务器1", "x": 400, "y": 400},
        ],
        "edges": [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "2", "target": "4"},
        ],
    }
    updated_content = json.dumps(updated_data, ensure_ascii=False)

    success = topology_manager.update_topology(topology_id, updated_content)
    print(f"   更新{'成功' if success else '失败'}")

    # 6. 查询所有拓扑图
    print("\n6. 查询所有拓扑图")
    all_topologies = topology_manager.get_all_topologies()
    print(f"   共有 {len(all_topologies)} 个拓扑图:")
    for topo in all_topologies:
        print(f"   - ID: {topo['id']}, 创建时间: {topo['created_at']}")

    # 7. 删除拓扑图（可选，注释掉以保留数据）
    # print(f"\n7. 删除拓扑图 (ID: {topology_id})")
    # success = topology_manager.delete_topology(topology_id)
    # print(f"   删除{'成功' if success else '失败'}")

    print("\n" + "=" * 60)
    print("示例执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
