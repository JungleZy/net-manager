#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SNMP v3 SHA认证协议的脚本
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from snmp_monitor import SNMPMonitor

async def test_sha_auth():
    """测试SHA认证协议"""
    # 创建SNMP监控实例
    monitor = SNMPMonitor()
    
    # 设备信息（请根据实际情况修改）
    device_ip = "192.168.1.1"  # 设备IP地址
    username = "your_username"  # SNMP v3用户名
    auth_key = "your_auth_key"  # 认证密钥
    oid = "1.3.6.1.2.1.1.1.0"  # 系统描述OID
    
    print("测试SNMP v3 SHA认证协议...")
    
    # 使用SHA认证协议获取数据
    value, success = await monitor.get_data(
        ip=device_ip,
        version="v3",
        oid=oid,
        user=username,
        auth_key=auth_key,
        auth_protocol="sha"  # 指定使用SHA认证协议
    )
    
    if success:
        print(f"成功获取数据: {value}")
    else:
        print("获取数据失败")
        
    # 同时测试MD5认证协议进行对比
    print("\n测试SNMP v3 MD5认证协议...")
    
    value, success = await monitor.get_data(
        ip=device_ip,
        version="v3",
        oid=oid,
        user=username,
        auth_key=auth_key,
        auth_protocol="md5"  # 指定使用MD5认证协议
    )
    
    if success:
        print(f"成功获取数据: {value}")
    else:
        print("获取数据失败")

if __name__ == "__main__":
    asyncio.run(test_sha_auth())