#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试性能监控API接口
"""

import requests
import json


def test_performance_api():
    """测试性能监控API接口"""
    try:
        # 请求性能数据
        response = requests.get("http://localhost:5000/api/performance")

        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers.get('Content-Type')}")
        print("\n性能数据:")

        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 验证数据结构
        if data.get("code") == 0:
            perf_data = data.get("data", {})
            print("\n=== 数据摘要 ===")
            print(f"CPU使用率: {perf_data.get('cpu', {}).get('usage_percent')}%")
            print(f"内存使用率: {perf_data.get('memory', {}).get('usage_percent')}%")
            print(f"磁盘使用率: {perf_data.get('disk', {}).get('usage_percent')}%")
            print(f"网络接口数: {len(perf_data.get('network', []))}")

    except requests.exceptions.ConnectionError:
        print("连接失败，请确保服务器正在运行（端口5000）")
    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_performance_api()
