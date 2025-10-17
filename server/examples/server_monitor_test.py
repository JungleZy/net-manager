#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器性能监控测试示例
演示如何使用ServerMonitor类
"""

import sys
import os
import time

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.monitor import get_server_monitor
from src.core.logger import logger
from src.core.state_manager import state_manager


def test_server_monitor():
    """测试服务器性能监控器"""

    print("=" * 50)
    print("服务器性能监控测试")
    print("=" * 50)

    # 获取监控器实例（5秒采集一次，便于测试）
    monitor = get_server_monitor(interval=5)

    # 模拟添加一个WebSocket客户端（用于测试消息发送）
    class MockWebSocketClient:
        def write_message(self, message):
            print(f"\n[模拟WebSocket客户端收到消息]")
            import json

            data = json.loads(message)

            if data.get("type") == "server_performance":
                perf_data = data.get("data", {})
                print(f"时间戳: {perf_data.get('timestamp')}")
                print(f"CPU使用率: {perf_data.get('cpu', {}).get('usage_percent')}%")
                print(
                    f"内存使用率: {perf_data.get('memory', {}).get('usage_percent')}%"
                )
                print(f"磁盘使用率: {perf_data.get('disk', {}).get('usage_percent')}%")
                print(f"网络接口数量: {len(perf_data.get('network', []))}")

                # 显示网络接口详情
                for interface in perf_data.get("network", []):
                    print(
                        f"  - {interface.get('name')}: "
                        f"上传 {interface.get('upload_rate', 0):.2f} B/s, "
                        f"下载 {interface.get('download_rate', 0):.2f} B/s"
                    )

    # 添加模拟客户端到状态管理器
    mock_client = MockWebSocketClient()
    state_manager.add_client(mock_client)

    # 启动监控器
    monitor.start()

    try:
        # 运行30秒（会采集6次数据）
        print("\n监控器已启动，将运行30秒...")
        print("按 Ctrl+C 可提前停止\n")
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    finally:
        # 停止监控器
        monitor.stop()
        state_manager.remove_client(mock_client)
        print("\n监控器已停止")
        print("=" * 50)


if __name__ == "__main__":
    test_server_monitor()
