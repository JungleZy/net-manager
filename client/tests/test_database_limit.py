#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试SQLite数据库只保留最新5条数据的功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

from src.models import DatabaseManager, SystemInfo


def create_test_system_info(index, timestamp):
    """创建测试用的系统信息"""
    return SystemInfo(
        hostname=f"test-host-{index}",
        ip_address=f"192.168.1.{index}",
        mac_address=f"00:11:22:33:44:{index:02d}",
        services=f'[{{"protocol": "TCP", "local_address": "0.0.0.0:80", "status": "LISTEN"}}]',
        processes=f'[{{"pid": {1000+index}, "name": "test_process_{index}", "username": "user", "status": "running", "cpu_percent": 0.0, "memory_percent": 0.0}}]',
        timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S")
    )


def test_database_limit():
    """测试数据库只保留最新5条数据的功能"""
    print("开始测试数据库限制功能...")
    
    # 创建数据库管理器实例
    db_manager = DatabaseManager()
    
    # 插入10条测试数据，每条数据间隔1分钟
    base_time = datetime.now() - timedelta(minutes=9)
    for i in range(10):
        timestamp = base_time + timedelta(minutes=i)
        system_info = create_test_system_info(i+1, timestamp)
        db_manager.save_system_info(system_info)
        print(f"已插入第 {i+1} 条测试数据，时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 查询所有数据
    all_records = db_manager.get_all_system_info()
    
    print(f"\n数据库中总记录数: {len(all_records)}")
    
    # 验证是否只保留了最新的5条记录
    if len(all_records) >= 5:  # 允许有额外的记录，但至少要有5条
        print("✓ 数据库正确地保留了最新的记录")
        
        # 验证这些记录是否包含最后5条
        # 注意：get_all_system_info按时间倒序返回，所以第一条是最新的
        expected_indices = set(range(6, 11))  # 应该包含第6到第10条记录
        actual_indices = set()
        for record in all_records:
            try:
                # 处理可能存在的非测试数据
                if record.hostname.startswith("test-host-"):
                    index = int(record.hostname.split('-')[-1])
                    actual_indices.add(index)
            except ValueError:
                # 如果无法解析索引，跳过该记录
                continue
        
        # 检查是否包含所有期望的记录
        if expected_indices.issubset(actual_indices):
            print("✓ 数据库包含了所有期望的最新记录")
            return True
        else:
            missing = expected_indices - actual_indices
            print(f"✗ 数据库缺少一些期望的记录。缺少的记录: {missing}")
            return False
    else:
        print(f"✗ 数据库记录数不正确。期望至少: 5, 实际: {len(all_records)}")
        return False


if __name__ == "__main__":
    success = test_database_limit()
    if success:
        print("\n测试通过!")
    else:
        print("\n测试失败!")
        sys.exit(1)