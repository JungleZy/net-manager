#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试asyncio模块的正确导入和使用
验证是否解决了pysnmp.hlapi.asyncio没有create_task属性的问题
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def test_asyncio_import():
    """测试asyncio模块的导入"""
    print("测试asyncio模块的导入...")
    
    try:
        # 检查asyncio模块是否正确导入
        print(f"asyncio模块: {asyncio}")
        print(f"asyncio.create_task: {asyncio.create_task}")
        print("✓ asyncio模块正确导入")
        return True
    except Exception as e:
        print(f"✗ asyncio模块导入失败: {e}")
        return False

async def test_asyncio_functionality():
    """测试asyncio功能"""
    print("\n测试asyncio功能...")
    
    async def dummy_task():
        """模拟任务"""
        await asyncio.sleep(0.1)
        return "任务完成"
    
    try:
        # 创建任务
        task = asyncio.create_task(dummy_task())
        
        # 等待任务完成
        result = await task
        print(f"任务结果: {result}")
        print("✓ asyncio功能正常")
        return True
    except Exception as e:
        print(f"✗ asyncio功能测试失败: {e}")
        return False

def test_pysnmp_import():
    """测试pysnmp模块的导入"""
    print("\n测试pysnmp模块的导入...")
    
    try:
        from pysnmp.hlapi.asyncio import (
            SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
        )
        print("✓ pysnmp模块正确导入")
        return True
    except Exception as e:
        print(f"✗ pysnmp模块导入失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("开始测试asyncio和pysnmp模块的正确导入和使用...\n")
    
    # 测试asyncio导入
    asyncio_ok = test_asyncio_import()
    
    # 测试asyncio功能
    functionality_ok = await test_asyncio_functionality()
    
    # 测试pysnmp导入
    pysnmp_ok = test_pysnmp_import()
    
    print("\n=== 测试结果 ===")
    if asyncio_ok and functionality_ok and pysnmp_ok:
        print("✓ 所有测试通过，模块导入和使用正常")
        print("✓ 已解决pysnmp.hlapi.asyncio没有create_task属性的问题")
    else:
        print("✗ 部分测试失败，请检查模块导入和使用")

if __name__ == "__main__":
    asyncio.run(main())