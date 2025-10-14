#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
拓扑图API接口测试脚本

测试所有拓扑图相关的API接口：
- POST /api/topologies/create - 创建拓扑图
- POST /api/topologies/update - 更新拓扑图
- POST /api/topologies/delete - 删除拓扑图
- GET /api/topologies - 获取所有拓扑图
- GET /api/topologies/latest - 获取最新拓扑图
- GET /api/topologies/{id} - 根据ID获取拓扑图
"""

import requests
import json


# API基础URL
BASE_URL = "http://localhost:8080"


def print_response(title, response):
    """格式化打印响应"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")


def test_create_topology():
    """测试创建拓扑图"""
    url = f"{BASE_URL}/api/topologies/create"

    # 测试数据
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

    # 方式1: 直接传递字典（会自动转换为JSON字符串）
    data = {"content": topology_data}

    response = requests.post(url, json=data)
    print_response("1. 创建拓扑图", response)

    # 返回创建的ID
    if response.status_code == 200:
        return response.json().get("data", {}).get("id")
    return None


def test_get_all_topologies():
    """测试获取所有拓扑图"""
    url = f"{BASE_URL}/api/topologies"
    response = requests.get(url)
    print_response("2. 获取所有拓扑图", response)


def test_get_latest_topology():
    """测试获取最新拓扑图"""
    url = f"{BASE_URL}/api/topologies/latest"
    response = requests.get(url)
    print_response("3. 获取最新拓扑图", response)


def test_get_topology_by_id(topology_id):
    """测试根据ID获取拓扑图"""
    url = f"{BASE_URL}/api/topologies/{topology_id}"
    response = requests.get(url)
    print_response(f"4. 根据ID获取拓扑图 (ID: {topology_id})", response)


def test_update_topology(topology_id):
    """测试更新拓扑图"""
    url = f"{BASE_URL}/api/topologies/update"

    # 更新后的数据
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

    data = {"id": topology_id, "content": updated_data}

    response = requests.post(url, json=data)
    print_response(f"5. 更新拓扑图 (ID: {topology_id})", response)


def test_delete_topology(topology_id):
    """测试删除拓扑图"""
    url = f"{BASE_URL}/api/topologies/delete"
    data = {"id": topology_id}

    response = requests.post(url, json=data)
    print_response(f"6. 删除拓扑图 (ID: {topology_id})", response)


def test_error_cases():
    """测试错误情况"""
    print(f"\n{'=' * 60}")
    print("7. 测试错误情况")
    print(f"{'=' * 60}")

    # 测试缺少必需字段
    url = f"{BASE_URL}/api/topologies/create"
    response = requests.post(url, json={})
    print_response("7.1 创建拓扑图 - 缺少content字段", response)

    # 测试无效的ID
    url = f"{BASE_URL}/api/topologies/999999"
    response = requests.get(url)
    print_response("7.2 获取不存在的拓扑图", response)

    # 测试无效的JSON
    url = f"{BASE_URL}/api/topologies/create"
    response = requests.post(url, json={"content": "invalid json {"})
    print_response("7.3 创建拓扑图 - 无效的JSON", response)


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("拓扑图API接口测试")
    print("=" * 60)
    print(f"API地址: {BASE_URL}")
    print("=" * 60)

    try:
        # 1. 创建拓扑图
        topology_id = test_create_topology()

        if topology_id:
            # 2. 获取所有拓扑图
            test_get_all_topologies()

            # 3. 获取最新拓扑图
            test_get_latest_topology()

            # 4. 根据ID获取拓扑图
            test_get_topology_by_id(topology_id)

            # 5. 更新拓扑图
            test_update_topology(topology_id)

            # 6. 再次获取以验证更新
            test_get_topology_by_id(topology_id)

            # 7. 测试错误情况
            test_error_cases()

            # 8. 删除拓扑图（可选，注释掉以保留测试数据）
            # test_delete_topology(topology_id)

            print(f"\n{'=' * 60}")
            print("测试完成！")
            print(f"{'=' * 60}")
            print(f"提示: 拓扑图ID {topology_id} 已保留，可用于后续测试")
        else:
            print("\n创建拓扑图失败，无法继续测试")

    except requests.exceptions.ConnectionError:
        print(f"\n错误: 无法连接到API服务器 ({BASE_URL})")
        print("请确保API服务器正在运行")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
