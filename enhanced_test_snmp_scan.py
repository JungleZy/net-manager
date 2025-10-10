#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版测试SNMP设备扫描性能的脚本
验证分批并发处理是否生效
"""

import asyncio
import time
import sys
import os
from unittest.mock import patch, AsyncMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from src.snmp.manager import SNMPManager

async def mock_snmp_scan_device(self, ip):
    """
    模拟SNMP设备扫描，用于测试
    
    Args:
        ip: 设备IP地址
        
    Returns:
        str or None: 如果设备响应则返回IP，否则返回None
    """
    # 模拟网络延迟
    await asyncio.sleep(0.1)
    
    # 模拟部分设备有响应
    if int(ip.split('.')[-1]) % 5 == 0:  # 每第5个IP有响应
        return ip
    return None

async def test_batch_processing_performance():
    """测试批量处理性能"""
    print("开始测试SNMP设备扫描批量处理性能...")
    
    # 创建SNMP管理器实例
    manager = SNMPManager()
    
    # 模拟一批IP地址用于测试
    test_ips = [f"192.168.1.{i}" for i in range(1, 101)]  # 100个IP地址
    print(f"测试设备数量: {len(test_ips)}")
    
    # 使用mock替换实际的SNMP扫描方法
    with patch.object(SNMPManager, 'snmp_scan_device', mock_snmp_scan_device):
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 执行设备扫描
            devices = await manager._scan_device_list(test_ips, "v2c", "public")
            
            # 记录结束时间
            end_time = time.time()
            
            print(f"\n扫描完成!")
            print(f"发现设备数量: {len(devices)}")
            print(f"耗时: {end_time - start_time:.2f} 秒")
            
            if devices:
                print("发现的设备:")
                for device in devices[:10]:  # 只显示前10个
                    print(f"  - {device}")
                if len(devices) > 10:
                    print(f"  ... 还有 {len(devices) - 10} 个设备")
                    
        except Exception as e:
            print(f"扫描过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

def analyze_batch_processing():
    """分析批量处理机制"""
    print("\n=== 批量处理机制分析 ===")
    print("1. 原始实现问题:")
    print("   - 虽然将设备分批处理，但每批内仍是顺序扫描")
    print("   - 每个设备扫描需要等待前一个设备完成")
    print("   - 导致总耗时 = 设备数量 × 单个设备平均扫描时间")
    
    print("\n2. 改进后实现:")
    print("   - 将每批内的设备扫描任务并发执行")
    print("   - 使用 asyncio.gather 同时启动所有任务")
    print("   - 总耗时 ≈ 批次数 × 单批最大扫描时间")
    
    print("\n3. 预期性能提升:")
    print("   - 对于100个设备，每批30个，每个设备0.1秒:")
    print("     原始实现: 100 × 0.1 = 10秒")
    print("     改进实现: 4批 × 0.1秒 = 0.4秒 (理论值)")

if __name__ == "__main__":
    # 分析批量处理机制
    analyze_batch_processing()
    
    print("\n" + "="*50)
    
    # 测试批量处理性能
    asyncio.run(test_batch_processing_performance())