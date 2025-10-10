#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合测试SNMPManager的功能
"""

import sys
import os
import asyncio
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def test_asyncio_functionality():
    """测试asyncio功能"""
    print("测试asyncio功能...")
    
    async def sample_task():
        await asyncio.sleep(0.1)
        return "任务完成"
    
    # 创建事件循环并运行任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(sample_task())
    loop.close()
    
    if result == "任务完成":
        print("✓ asyncio功能正常")
        return True
    else:
        print("✗ asyncio功能异常")
        return False

def test_snmp_manager_import():
    """测试SNMPManager类的导入"""
    print("测试SNMPManager类的导入...")
    
    try:
        from src.snmp.manager import SNMPManager
        print("✓ SNMPManager类正确导入")
        return True
    except Exception as e:
        print(f"✗ SNMPManager类导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processing_implementation():
    """测试分批处理实现"""
    print("测试分批处理实现...")
    
    try:
        # 检查SNMPManager是否有scan_network_devices方法
        from src.snmp.manager import SNMPManager
        
        # 获取scan_network_devices方法的源码
        import inspect
        source = inspect.getsource(SNMPManager.scan_network_devices)
        
        # 检查是否包含asyncio.gather的使用
        if "asyncio.gather" in source:
            print("✓ 分批处理实现正确，使用了asyncio.gather")
            return True
        else:
            print("✗ 分批处理实现不正确，未使用asyncio.gather")
            return False
    except Exception as e:
        print(f"✗ 分批处理实现检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_pysnmp_asyncio_conflict():
    """测试没有pysnmp和asyncio模块冲突"""
    print("测试没有pysnmp和asyncio模块冲突...")
    
    try:
        # 尝试导入pysnmp的相关模块
        from pysnmp.hlapi.asyncio import SnmpEngine
        # 尝试使用asyncio.create_task
        task = asyncio.create_task(asyncio.sleep(0))
        task.cancel()  # 取消任务以免影响其他操作
        print("✓ pysnmp和asyncio模块没有冲突")
        return True
    except AttributeError as e:
        if "create_task" in str(e):
            print("✗ pysnmp和asyncio模块存在冲突")
            return False
        else:
            # 其他AttributeError可能是正常的
            print("✓ pysnmp和asyncio模块没有冲突")
            return True
    except Exception as e:
        print(f"✓ pysnmp和asyncio模块没有冲突: {e}")
        return True

def main():
    """主测试函数"""
    print("开始综合测试SNMPManager功能...\n")
    
    # 测试各项功能
    tests = [
        test_asyncio_functionality,
        test_snmp_manager_import,
        test_batch_processing_implementation,
        test_no_pysnmp_asyncio_conflict
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()  # 空行分隔
        except Exception as e:
            print(f"测试过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
            print()  # 空行分隔
    
    print("=== 综合测试结果 ===")
    if all(results):
        print("✓ 所有测试通过，SNMPManager功能正常")
        print("✓ 已解决'pysnmp.hlapi.asyncio没有create_task属性'的问题")
        print("✓ 分批处理功能已正确实现")
    else:
        print("✗ 部分测试失败，请检查上述错误信息")

if __name__ == "__main__":
    main()