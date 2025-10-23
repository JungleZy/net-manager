#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置TCP IP配置示例
演示如何在状态文件中设置tcp_ip，以便客户端直接连接到指定的服务器
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.state_manager import get_state_manager

def set_tcp_ip_config(ip, port=12346):
    """
    设置TCP IP配置
    
    Args:
        ip (str): 服务器IP地址
        port (int): 服务器端口号，默认为12346
    """
    # 获取状态管理器
    state_manager = get_state_manager()
    
    # 设置tcp_ip和tcp_port
    success = state_manager.set_state("tcp_ip", ip)
    success = success and state_manager.set_state("tcp_port", port)
    
    if success:
        print(f"✓ 成功设置TCP服务器配置: {ip}:{port}")
        print("下次启动客户端时，将直接连接到此服务器，跳过UDP发现过程")
    else:
        print("✗ 设置TCP服务器配置失败")
    
    return success

def clear_tcp_ip_config():
    """清除TCP IP配置，恢复使用UDP发现"""
    # 获取状态管理器
    state_manager = get_state_manager()
    
    # 清除tcp_ip配置
    success = state_manager.set_state("tcp_ip", "")
    
    if success:
        print("✓ 成功清除TCP服务器配置")
        print("下次启动客户端时，将使用UDP发现过程")
    else:
        print("✗ 清除TCP服务器配置失败")
    
    return success

def show_current_config():
    """显示当前配置"""
    # 获取状态管理器
    state_manager = get_state_manager()
    
    # 获取当前配置
    tcp_ip = state_manager.get_state("tcp_ip")
    tcp_port = state_manager.get_state("tcp_port", 12346)
    
    print("当前TCP服务器配置:")
    if tcp_ip and tcp_ip.strip():
        print(f"  IP地址: {tcp_ip}")
        print(f"  端口号: {tcp_port}")
        print("  状态: 已配置，将直接连接到此服务器")
    else:
        print("  IP地址: 未配置")
        print("  端口号: 默认(12346)")
        print("  状态: 将使用UDP发现过程")

def main():
    """主函数"""
    print("=== TCP IP配置工具 ===\n")
    
    # 显示当前配置
    show_current_config()
    
    print("\n请选择操作:")
    print("1. 设置TCP IP配置")
    print("2. 清除TCP IP配置")
    print("3. 显示当前配置")
    print("0. 退出")
    
    try:
        choice = input("\n请输入选项(0-3): ").strip()
        
        if choice == "1":
            ip = input("请输入服务器IP地址: ").strip()
            if not ip:
                print("IP地址不能为空")
                return
            
            port_str = input("请输入服务器端口号(默认12346): ").strip()
            port = int(port_str) if port_str else 12346
            
            set_tcp_ip_config(ip, port)
            
        elif choice == "2":
            clear_tcp_ip_config()
            
        elif choice == "3":
            show_current_config()
            
        elif choice == "0":
            print("退出")
            
        else:
            print("无效选项")
            
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except ValueError:
        print("端口号必须是数字")
    except Exception as e:
        print(f"操作失败: {e}")

if __name__ == "__main__":
    main()