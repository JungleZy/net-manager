#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交换机API测试脚本
用于测试交换机增删改查API功能
"""

import requests
import json

# API服务器地址
API_BASE_URL = "http://localhost:12344/api"

def test_create_switch():
    """测试创建交换机"""
    print("=== 测试创建交换机 ===")
    
    # 准备测试数据
    switch_data = {
        "ip": "192.168.1.10",
        "snmp_version": "2c",
        "community": "public",
        "description": "测试交换机"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/switches/create", json=switch_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.json().get("status") == "success"
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_get_all_switches():
    """测试获取所有交换机"""
    print("\n=== 测试获取所有交换机 ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/switches")
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {result}")
        return result.get("status") == "success"
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_get_switch_by_id(switch_id):
    """测试根据ID获取交换机"""
    print(f"\n=== 测试根据ID获取交换机 (ID: {switch_id}) ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/switches/{switch_id}")
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {result}")
        return result.get("status") == "success"
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_update_switch(switch_id):
    """测试更新交换机"""
    print(f"\n=== 测试更新交换机 (ID: {switch_id}) ===")
    
    # 准备更新数据
    switch_data = {
        "id": switch_id,
        "ip": "192.168.1.10",
        "snmp_version": "3",
        "user": "admin",
        "auth_key": "authkey123",
        "auth_protocol": "SHA",
        "priv_key": "privkey123",
        "priv_protocol": "AES",
        "description": "更新后的测试交换机"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/switches/update", json=switch_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.json().get("status") == "success"
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_delete_switch(switch_id):
    """测试删除交换机"""
    print(f"\n=== 测试删除交换机 (ID: {switch_id}) ===")
    
    # 准备删除数据
    delete_data = {
        "id": switch_id
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/switches/delete", json=delete_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.json().get("status") == "success"
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试交换机API...")
    
    # 测试创建交换机
    if test_create_switch():
        print("✓ 创建交换机测试通过")
    else:
        print("✗ 创建交换机测试失败")
        return
    
    # 测试获取所有交换机
    if test_get_all_switches():
        print("✓ 获取所有交换机测试通过")
    else:
        print("✗ 获取所有交换机测试失败")
        return
    
    # 获取一个交换机ID用于后续测试
    try:
        response = requests.get(f"{API_BASE_URL}/switches")
        switches = response.json().get("data", [])
        if switches:
            switch_id = switches[0]["id"]
            
            # 测试根据ID获取交换机
            if test_get_switch_by_id(switch_id):
                print("✓ 根据ID获取交换机测试通过")
            else:
                print("✗ 根据ID获取交换机测试失败")
            
            # 测试更新交换机
            if test_update_switch(switch_id):
                print("✓ 更新交换机测试通过")
            else:
                print("✗ 更新交换机测试失败")
            
            # 测试删除交换机
            if test_delete_switch(switch_id):
                print("✓ 删除交换机测试通过")
            else:
                print("✗ 删除交换机测试失败")
        else:
            print("没有找到交换机用于测试")
    except Exception as e:
        print(f"获取交换机列表失败: {e}")

    print("\n交换机API测试完成!")

if __name__ == "__main__":
    main()