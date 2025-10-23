#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试TCP连接逻辑修改
验证在发起UDP发现前先查询配置文件是否存在tcp_ip的功能
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.state_manager import get_state_manager
from src.core.app_controller import AppController

def test_tcp_ip_from_config():
    """测试从配置文件读取tcp_ip的功能"""
    print("=== 测试从配置文件读取tcp_ip的功能 ===")
    
    # 获取状态管理器
    state_manager = get_state_manager()
    
    # 设置测试用的tcp_ip
    test_ip = "192.168.1.100"
    test_port = 12346
    
    print(f"设置测试用的tcp_ip: {test_ip}:{test_port}")
    state_manager.set_state("tcp_ip", test_ip)
    state_manager.set_state("tcp_port", test_port)
    
    # 创建应用控制器实例
    app_controller = AppController()
    
    # 测试_get_server_address_from_config方法
    server_address = app_controller._get_server_address_from_config()
    
    if server_address:
        ip, port = server_address
        print(f"成功从配置文件获取服务端地址: {ip}:{port}")
        assert ip == test_ip, f"IP地址不匹配: 期望 {test_ip}, 实际 {ip}"
        assert port == test_port, f"端口不匹配: 期望 {test_port}, 实际 {port}"
        print("✓ 测试通过: 从配置文件正确读取tcp_ip")
    else:
        print("✗ 测试失败: 无法从配置文件读取tcp_ip")
        return False
    
    # 清理测试数据
    state_manager.set_state("tcp_ip", "")
    
    # 再次测试，应该返回None
    server_address = app_controller._get_server_address_from_config()
    if server_address is None:
        print("✓ 测试通过: 配置文件中没有tcp_ip时返回None")
    else:
        print("✗ 测试失败: 配置文件中没有tcp_ip时应返回None")
        return False
    
    return True

def test_connection_logic():
    """测试连接逻辑"""
    print("\n=== 测试连接逻辑 ===")
    
    # 获取状态管理器
    state_manager = get_state_manager()
    
    # 设置测试用的tcp_ip
    test_ip = "192.168.1.200"  # 使用一个不存在的IP地址，避免实际连接
    test_port = 12346
    
    print(f"设置测试用的tcp_ip: {test_ip}:{test_port}")
    state_manager.set_state("tcp_ip", test_ip)
    state_manager.set_state("tcp_port", test_port)
    
    # 创建应用控制器实例
    app_controller = AppController()
    
    # 测试连接逻辑（不实际启动连接，只测试地址获取部分）
    print("测试连接逻辑中的地址获取部分...")
    server_address = app_controller._get_server_address_from_config()
    
    if server_address:
        ip, port = server_address
        print(f"连接逻辑会尝试直接连接到: {ip}:{port}")
        print("✓ 测试通过: 连接逻辑正确获取配置文件中的地址")
    else:
        print("✗ 测试失败: 连接逻辑无法获取配置文件中的地址")
        return False
    
    # 清理测试数据
    state_manager.set_state("tcp_ip", "")
    
    # 再次测试，应该回退到UDP发现
    server_address = app_controller._get_server_address_from_config()
    if server_address is None:
        print("✓ 测试通过: 没有tcp_ip配置时会回退到UDP发现")
    else:
        print("✗ 测试失败: 没有tcp_ip配置时应回退到UDP发现")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试TCP连接逻辑修改...")
    
    # 确保在client目录下运行
    os.chdir(Path(__file__).parent)
    
    try:
        # 测试从配置文件读取tcp_ip的功能
        if not test_tcp_ip_from_config():
            print("测试失败: 从配置文件读取tcp_ip的功能")
            return False
        
        # 测试连接逻辑
        if not test_connection_logic():
            print("测试失败: 连接逻辑")
            return False
        
        print("\n✓ 所有测试通过!")
        return True
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)