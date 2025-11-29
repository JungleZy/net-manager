#!/usr/bin/env python3
"""
测试IP地址获取功能的脚本
用于验证修改后的system_collector.py在Linux系统上的兼容性
"""

import sys
import os
import platform
import socket

# 添加项目路径到sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.system.system_collector import SystemCollector
from src.utils.logger import get_logger

def test_ip_address_methods():
    """测试各种IP地址获取方法"""
    logger = get_logger()
    system_collector = SystemCollector()
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print("=" * 50)
    methods = [
        ("方法1: 连接外部地址", lambda: system_collector._test_method_1()),
        ("方法2: 使用psutil", lambda: system_collector._get_ip_via_psutil()),
        ("方法3: 通过网关", lambda: system_collector._get_ip_via_gateway()),
        ("方法4: 使用hostname", lambda: system_collector._test_method_4()),
        ("综合方法", lambda: system_collector.get_ip_address()),
    ]
    for method_name, method_func in methods:
        try:
            result = method_func()
            print(f"{method_name}: {result}")
        except Exception as e:
            print(f"{method_name}: 失败 - {e}")
    print("=" * 50)
    print("网络接口信息:")
    try:
        import psutil
        net_if_addrs = psutil.net_if_addrs()
        for interface, addrs in net_if_addrs.items():
            print(f"\n接口: {interface}")
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    print(f"  IPv4: {addr.address} / {addr.netmask}")
                elif addr.family == socket.AF_INET6:
                    print(f"  IPv6: {addr.address}")
                elif hasattr(psutil, "AF_LINK") and addr.family == psutil.AF_LINK:
                    print(f"  MAC: {addr.address}")
    except Exception as e:
        print(f"获取网络接口信息失败: {e}")
    print("=" * 50)
    print("路由信息:")
    try:
        if platform.system() in ("Linux", "Darwin"):
            import subprocess
            result = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split("\n")[:10]:
                    if line.strip():
                        print(f"  {line}")
        elif platform.system() == "Windows":
            import subprocess
            result = subprocess.run(["route", "print"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                in_ipv4_section = False
                for line in lines:
                    if "IPv4 路由表" in line or "IPv4 Route Table" in line:
                        in_ipv4_section = True
                    if in_ipv4_section and line.strip():
                        print(f"  {line}")
                        if "====" in line:
                            break
    except Exception as e:
        print(f"获取路由信息失败: {e}")

def _test_method_1(self):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        if self._is_valid_ip(ip_address):
            return ip_address
        return "invalid"
    except Exception as e:
        return f"error: {e}"

def _test_method_4(self):
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        if self._is_valid_ip(ip_address):
            return ip_address
        return "invalid"
    except Exception as e:
        return f"error: {e}"

SystemCollector._test_method_1 = _test_method_1
SystemCollector._test_method_4 = _test_method_4

if __name__ == "__main__":
    test_ip_address_methods()
