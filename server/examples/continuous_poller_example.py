#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SNMP持续轮询器使用示例
"""

import sys
import os
import time

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from src.database.managers.switch_manager import SwitchManager
from src.snmp.continuous_poller import (
    SNMPContinuousPoller,
    start_snmp_poller,
    stop_snmp_poller,
)
from src.core.logger import logger


def example_with_class():
    """使用类的方式创建和管理轮询器"""
    print("=" * 50)
    print("示例1: 使用类方式创建轮询器")
    print("=" * 50)

    # 1. 创建交换机管理器实例
    switch_manager = SwitchManager()

    # 2. 创建轮询器实例
    poller = SNMPContinuousPoller(
        switch_manager=switch_manager,
        poll_interval=30,  # 每30秒轮询一次
        max_workers=5,  # 最多5个并发任务
    )

    # 3. 启动轮询器
    poller.start()

    try:
        # 4. 让轮询器运行一段时间
        print("轮询器正在运行，按Ctrl+C停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止轮询器...")
    finally:
        # 5. 停止轮询器
        poller.stop()
        print("轮询器已停止")


def example_with_global_functions():
    """使用全局函数的方式管理轮询器"""
    print("=" * 50)
    print("示例2: 使用全局函数方式管理轮询器")
    print("=" * 50)

    # 1. 创建交换机管理器实例
    switch_manager = SwitchManager()

    # 2. 启动全局轮询器
    poller = start_snmp_poller(
        switch_manager=switch_manager,
        poll_interval=60,  # 每60秒轮询一次
        max_workers=10,  # 最多10个并发任务
    )

    try:
        # 3. 让轮询器运行一段时间
        print("轮询器正在运行，按Ctrl+C停止...")
        print(f"轮询器状态: {'运行中' if poller.is_running else '已停止'}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止轮询器...")
    finally:
        # 4. 停止全局轮询器
        stop_snmp_poller()
        print("轮询器已停止")


def example_with_custom_callback():
    """使用自定义回调的示例"""
    print("=" * 50)
    print("示例3: 使用自定义回调")
    print("=" * 50)

    # 1. 创建自定义轮询器类
    class CustomSNMPPoller(SNMPContinuousPoller):
        """自定义SNMP轮询器，重写回调方法"""

        def _on_device_info_received(self, device_data):
            """自定义设备信息接收回调"""
            ip = device_data.get("ip")

            if "error" in device_data:
                # 处理错误情况
                logger.warning(f"设备 {ip} 轮询失败: {device_data['error']}")
            else:
                # 处理成功情况
                device_info = device_data.get("device_info", {})
                device_name = device_info.get("name", "未知")
                description = device_info.get("description", "")

                logger.info(f"设备 {ip} 信息更新:")
                logger.info(f"  名称: {device_name}")
                logger.info(f"  描述: {description[:50]}...")

                # 在这里可以添加更多自定义逻辑：
                # - 将数据发送到WebSocket
                # - 存储到缓存
                # - 检查告警条件
                # - 更新数据库等

    # 2. 创建交换机管理器实例
    switch_manager = SwitchManager()

    # 3. 创建自定义轮询器实例
    poller = CustomSNMPPoller(
        switch_manager=switch_manager,
        poll_interval=45,  # 每45秒轮询一次
        max_workers=8,
    )

    # 4. 启动轮询器
    poller.start()

    try:
        # 5. 让轮询器运行一段时间
        print("自定义轮询器正在运行，按Ctrl+C停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止轮询器...")
    finally:
        # 6. 停止轮询器
        poller.stop()
        print("轮询器已停止")


def main():
    """主函数"""
    print("\nSNMP持续轮询器使用示例")
    print("请选择运行的示例:")
    print("1. 使用类方式创建轮询器")
    print("2. 使用全局函数方式管理轮询器")
    print("3. 使用自定义回调")
    print("0. 退出")

    choice = input("\n请输入选项 (0-3): ").strip()

    if choice == "1":
        example_with_class()
    elif choice == "2":
        example_with_global_functions()
    elif choice == "3":
        example_with_custom_callback()
    elif choice == "0":
        print("退出示例程序")
    else:
        print("无效的选项")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"示例程序运行出错: {e}")
        import traceback

        traceback.print_exc()
