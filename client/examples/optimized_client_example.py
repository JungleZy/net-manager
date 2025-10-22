#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化后的客户端使用示例
演示优化后的TCP和UDP客户端的使用方法
"""

import sys
import os
import time
import threading

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from src.network.udp_client import get_udp_client
from src.network.tcp_client import get_tcp_client


def main():
    """主函数"""
    print("NetManager优化客户端示例")
    print("=" * 50)

    # 获取UDP客户端实例
    udp_client = get_udp_client()

    # 获取TCP客户端实例
    tcp_client = get_tcp_client()

    try:
        # 1. 使用多播方式发现服务端
        print("\n1. 尝试通过多播方式发现服务端...")
        server_address = udp_client.discover_server_multicast()

        # 2. 如果多播方式失败，回退到广播方式
        if server_address is None:
            print("多播服务发现失败，回退到广播方式...")
            server_address = udp_client.discover_server_broadcast()

        # 3. 检查是否成功发现服务端
        if server_address is None:
            print("❌ 服务发现失败，无法连接到服务端")
            return False

        print(f"✅ 成功发现服务端: {server_address[0]}:{server_address[1]}")

        # 4. 使用发现的服务端地址连接TCP客户端
        print("\n2. 尝试连接到服务端...")
        if tcp_client.connect(server_address):
            print("✅ 成功连接到服务端")

            # 5. 发送系统信息
            print("\n3. 发送系统信息到服务端...")
            if tcp_client.send_system_info():
                print("✅ 系统信息发送成功")
            else:
                print("❌ 系统信息发送失败")

            # 6. 模拟持续通信
            print("\n4. 模拟持续通信30秒...")
            start_time = time.time()
            while time.time() - start_time < 30:
                # 每5秒发送一次系统信息
                if int(time.time() - start_time) % 5 == 0:
                    print(f"  发送心跳包... ({int(time.time() - start_time)}s)")
                    tcp_client.send_system_info()
                time.sleep(1)

            # 7. 断开连接
            print("\n5. 断开连接...")
            tcp_client.disconnect()
            print("✅ 连接已断开")

            return True
        else:
            print("❌ 连接到服务端失败")
            return False

    except KeyboardInterrupt:
        print("\n\n收到中断信号，正在清理...")
        tcp_client.disconnect()
        print("✅ 程序已退出")
    except Exception as e:
        print(f"\n❌ 运行过程中出现错误: {e}")
        tcp_client.disconnect()
        return False


if __name__ == "__main__":
    main()
