#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试多CPU检测功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.monitor.server_monitor import ServerMonitor
import json


def test_cpu_detection():
    """测试CPU检测功能"""
    print("=" * 60)
    print("测试服务器CPU信息检测")
    print("=" * 60)

    monitor = ServerMonitor()
    cpu_info = monitor._get_cpu_info()

    print("\n📊 CPU详细信息：")
    print(json.dumps(cpu_info, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("关键信息摘要：")
    print("=" * 60)

    print(f"CPU使用率: {cpu_info.get('usage_percent', 0)}%")
    print(f"逻辑核心数（线程）: {cpu_info.get('cores', 0)}")
    print(f"物理核心数: {cpu_info.get('physical_cores', 0)}")

    if cpu_info.get("threads_per_core"):
        print(f"每核心线程数: {cpu_info['threads_per_core']}")
        has_ht = "是" if cpu_info["threads_per_core"] > 1 else "否"
        print(f"是否启用超线程: {has_ht}")

    if cpu_info.get("estimated_physical_cpus"):
        cpu_count = cpu_info["estimated_physical_cpus"]
        print(f"\n🖥️  估算的物理CPU数量: {cpu_count}")

        if cpu_count > 1:
            print(f"   这是一个 {cpu_count}路CPU 系统")
        else:
            print("   这是一个单CPU系统")

    if cpu_info.get("current_frequency"):
        print(f"\n⚡ 当前频率: {cpu_info['current_frequency']} MHz")
    if cpu_info.get("max_frequency"):
        print(f"   最大频率: {cpu_info['max_frequency']} MHz")

    if cpu_info.get("load_average"):
        load_avg = cpu_info["load_average"]
        print(
            f"\n📈 系统负载: {load_avg[0]} (1分钟), {load_avg[1]} (5分钟), {load_avg[2]} (15分钟)"
        )

    if cpu_info.get("per_cpu_percent"):
        per_cpu = cpu_info["per_cpu_percent"]
        print(f"\n🔢 各核心使用率 (共{len(per_cpu)}个逻辑核心):")

        # 每行显示8个核心
        for i in range(0, len(per_cpu), 8):
            cores = per_cpu[i : i + 8]
            core_str = ", ".join(
                [f"核心{i+j}: {usage:.1f}%" for j, usage in enumerate(cores)]
            )
            print(f"   {core_str}")

        avg_usage = sum(per_cpu) / len(per_cpu)
        max_usage = max(per_cpu)
        min_usage = min(per_cpu)
        print(f"\n   平均使用率: {avg_usage:.2f}%")
        print(f"   最高使用率: {max_usage:.2f}%")
        print(f"   最低使用率: {min_usage:.2f}%")

    if cpu_info.get("per_cpu_frequency"):
        per_freq = cpu_info["per_cpu_frequency"]
        print(f"\n🔄 各核心频率 (共{len(per_freq)}个):")
        for i in range(0, len(per_freq), 8):
            freqs = per_freq[i : i + 8]
            freq_str = ", ".join(
                [f"核心{i+j}: {freq:.0f}MHz" for j, freq in enumerate(freqs)]
            )
            print(f"   {freq_str}")

    print("\n" + "=" * 60)

    # 检测多CPU配置
    if cpu_info.get("estimated_physical_cpus", 1) > 1:
        print("\n✅ 检测到多物理CPU配置！")
        print(f"   物理CPU数量: {cpu_info['estimated_physical_cpus']}")
        print(f"   总物理核心: {cpu_info.get('physical_cores', 0)}")
        cores_per_cpu = cpu_info.get("physical_cores", 0) // cpu_info.get(
            "estimated_physical_cpus", 1
        )
        print(f"   每个CPU核心数: {cores_per_cpu}")
    else:
        print("\n✅ 这是单CPU系统")


def test_estimate_method():
    """测试物理CPU估算方法"""
    print("\n" + "=" * 60)
    print("测试物理CPU估算方法")
    print("=" * 60)

    monitor = ServerMonitor()
    estimated_cpus = monitor._estimate_physical_cpu_count()

    print(f"\n估算的物理CPU数量: {estimated_cpus}")

    import psutil

    logical_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)

    print(f"逻辑核心数: {logical_cores}")
    print(f"物理核心数: {physical_cores}")

    if physical_cores and logical_cores:
        threads_per_core = logical_cores // physical_cores
        print(f"每核心线程数: {threads_per_core}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        test_cpu_detection()
        test_estimate_method()

        print("\n✅ 测试完成！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
