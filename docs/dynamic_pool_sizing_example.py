#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态调整数据库连接池大小的示例实现
展示了如何根据CPU核心数动态计算连接池大小
"""

import os
import multiprocessing
from typing import Tuple


def get_cpu_info() -> Tuple[int, int]:
    """
    获取CPU信息
    
    Returns:
        Tuple[int, int]: (物理核心数, 逻辑核心数)
    """
    # 物理核心数
    physical_cores = multiprocessing.cpu_count()
    
    # 在Windows上获取更准确的CPU信息
    try:
        # 使用wmic命令获取更详细的信息
        import subprocess
        result = subprocess.run(
            ['wmic', 'cpu', 'get', 'NumberOfCores,NumberOfLogicalProcessors'],
            capture_output=True, text=True, shell=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            # 解析输出
            values = lines[1].strip().split()
            if len(values) >= 2:
                physical_cores = int(values[0])
                logical_cores = int(values[1])
                return physical_cores, logical_cores
    except Exception as e:
        print(f"获取详细CPU信息时出错: {e}")
    
    # 回退到multiprocessing获取逻辑核心数
    logical_cores = multiprocessing.cpu_count()
    return physical_cores, logical_cores


def calculate_optimal_pool_size(
    cpu_cores: int,
    memory_gb: float = None,
    workload_type: str = "mixed"
) -> dict:
    """
    根据CPU核心数计算最优连接池大小
    
    Args:
        cpu_cores: CPU核心数
        memory_gb: 系统内存大小(GB)，可选
        workload_type: 工作负载类型 ("io_bound", "cpu_bound", "mixed")
        
    Returns:
        dict: 包含推荐连接池配置的字典
    """
    # 基于CPU核心数的连接池大小计算公式
    # 这是一个经验公式，来源于业界最佳实践
    if workload_type == "io_bound":
        # I/O密集型应用通常可以使用更多连接
        max_connections = cpu_cores * 4 + 1
        min_connections = max(2, cpu_cores // 2)
    elif workload_type == "cpu_bound":
        # CPU密集型应用应该使用较少连接
        max_connections = cpu_cores * 2 + 1
        min_connections = max(2, cpu_cores // 4)
    else:  # mixed
        # 混合型应用使用中等连接数
        max_connections = cpu_cores * 2 + 1
        min_connections = max(2, cpu_cores // 2)
    
    # 根据内存大小进行调整（如果提供了内存信息）
    if memory_gb:
        # 假设每个连接大约占用10MB内存
        memory_based_limit = int(memory_gb * 1024 / 10)  # 转换为MB并除以每个连接的内存占用
        max_connections = min(max_connections, memory_based_limit)
    
    # 确保最小值不小于1，最大值不小于最小值
    min_connections = max(1, min_connections)
    max_connections = max(min_connections, max_connections)
    
    # 清理间隔和最大空闲时间
    cleanup_interval = 60  # 60秒
    max_idle_time = 300    # 5分钟
    
    return {
        "max_connections": max_connections,
        "min_connections": min_connections,
        "cleanup_interval": cleanup_interval,
        "max_idle_time": max_idle_time
    }


def dynamic_pool_initializer():
    """
    动态连接池初始化器
    展示如何在实际应用中使用动态计算的连接池大小
    """
    # 获取CPU信息
    physical_cores, logical_cores = get_cpu_info()
    print(f"CPU信息: 物理核心数={physical_cores}, 逻辑核心数={logical_cores}")
    
    # 估算系统内存（简化版本）
    try:
        # 获取系统内存信息（以字节为单位）
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"系统内存: {memory_gb:.2f} GB")
    except ImportError:
        memory_gb = None
        print("未安装psutil库，无法获取内存信息")
    
    # 计算不同工作负载类型的连接池大小
    workloads = ["io_bound", "cpu_bound", "mixed"]
    
    for workload in workloads:
        pool_config = calculate_optimal_pool_size(
            cpu_cores=logical_cores,
            memory_gb=memory_gb,
            workload_type=workload
        )
        
        print(f"\n{workload.upper()} 工作负载推荐配置:")
        print(f"  最大连接数: {pool_config['max_connections']}")
        print(f"  最小连接数: {pool_config['min_connections']}")
        print(f"  清理间隔: {pool_config['cleanup_interval']} 秒")
        print(f"  最大空闲时间: {pool_config['max_idle_time']} 秒")
    
    # 推荐的实际应用配置
    print("\n" + "="*50)
    print("推荐在实际应用中使用的配置:")
    recommended_config = calculate_optimal_pool_size(
        cpu_cores=logical_cores,
        memory_gb=memory_gb,
        workload_type="mixed"
    )
    
    print(f"最大连接数: {recommended_config['max_connections']}")
    print(f"最小连接数: {recommended_config['min_connections']}")
    
    return recommended_config


# 使用示例
if __name__ == "__main__":
    # 动态计算并显示推荐的连接池配置
    config = dynamic_pool_initializer()
    
    # 在实际应用中，您可以这样使用:
    """
    # 在DatabaseManager初始化时使用动态配置
    db_manager = DatabaseManager("net_manager_server.db")
    db_manager.init_async_pool(
        max_connections=config['max_connections'],
        min_connections=config['min_connections'],
        cleanup_interval=config['cleanup_interval'],
        max_idle_time=config['max_idle_time']
    )
    """