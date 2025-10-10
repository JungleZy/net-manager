#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试SNMPManager类的导入
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

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

def main():
    """主测试函数"""
    print("开始测试SNMPManager类的导入...\n")
    
    # 测试SNMPManager导入
    success = test_snmp_manager_import()
    
    print("\n=== 测试结果 ===")
    if success:
        print("✓ SNMPManager类导入测试通过")
    else:
        print("✗ SNMPManager类导入测试失败")

if __name__ == "__main__":
    main()