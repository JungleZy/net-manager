import unittest
import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

from src.system.system_collector import SystemCollector, SystemInfo

class TestSystemCollector(unittest.TestCase):
    
    def setUp(self):
        """测试前准备"""
        self.collector = SystemCollector()
    
    def test_get_hostname(self):
        """测试获取主机名"""
        hostname = self.collector.get_hostname()
        self.assertIsInstance(hostname, str)
        self.assertGreater(len(hostname), 0)
        print(f"主机名: {hostname}")
    
    def test_get_ip_address(self):
        """测试获取IP地址"""
        ip = self.collector.get_ip_address()
        self.assertIsInstance(ip, str)
        self.assertGreater(len(ip), 0)
        print(f"IP地址: {ip}")
    
    def test_get_mac_address(self):
        """测试获取MAC地址"""
        mac = self.collector.get_mac_address()
        self.assertIsInstance(mac, str)
        self.assertGreater(len(mac), 0)
        # MAC地址格式应该是xx:xx:xx:xx:xx:xx
        self.assertEqual(len(mac), 17)  # 6组2位十六进制数 + 5个冒号
        print(f"MAC地址: {mac}")
    
    def test_get_services(self):
        """测试获取服务信息"""
        services = self.collector.get_services()
        self.assertIsInstance(services, list)
        # 应该至少有一些服务在运行
        self.assertGreater(len(services), 0)
        # 检查第一个服务的结构
        if services:
            service = services[0]
            self.assertIn('protocol', service)
            self.assertIn('local_address', service)
            self.assertIn('status', service)
        print(f"服务数量: {len(services)}")
    
    def test_get_os_info(self):
        """测试获取操作系统信息"""
        os_name, os_version, os_architecture, machine_type = self.collector.get_os_info()
        
        self.assertIsInstance(os_name, str)
        self.assertGreater(len(os_name), 0)
        
        self.assertIsInstance(os_version, str)
        self.assertIsInstance(os_architecture, str)
        self.assertIsInstance(machine_type, str)
        
        print(f"操作系统信息:")
        print(f"  系统名称: {os_name}")
        print(f"  系统版本: {os_version}")
        print(f"  系统架构: {os_architecture}")
        print(f"  机器类型: {machine_type}")
    
    def test_collect_system_info(self):
        """测试收集完整系统信息"""
        info = self.collector.collect_system_info()
        self.assertIsInstance(info, SystemInfo)
        
        # 检查所有属性是否存在且不为空
        self.assertIsInstance(info.hostname, str)
        self.assertGreater(len(info.hostname), 0)
        
        self.assertIsInstance(info.network_interfaces, list)
        self.assertGreater(len(info.network_interfaces), 0)
        
        self.assertIsInstance(info.processes, list)
        self.assertGreater(len(info.processes), 0)
        
        # 检查服务信息是否为列表类型
        self.assertIsInstance(info.services, list)
        # 应该至少有一些服务在运行
        self.assertGreater(len(info.services), 0)
        
        # 检查时间戳
        self.assertIsNotNone(info.timestamp)
        
        # 检查新添加的操作系统信息
        self.assertIsInstance(info.os_name, str)
        self.assertGreater(len(info.os_name), 0)
        self.assertIsInstance(info.os_version, str)
        self.assertIsInstance(info.os_architecture, str)
        self.assertIsInstance(info.machine_type, str)
        
        print(f"完整系统信息对象创建成功")
        print(f"  主机名: {info.hostname}")
        print(f"  网络接口数量: {len(info.network_interfaces)}")
        print(f"  进程数量: {len(info.processes)}")
        print(f"  服务数量: {len(info.services)}")
        print(f"  时间戳: {info.timestamp}")
        print(f"  操作系统名称: {info.os_name}")
        print(f"  操作系统版本: {info.os_version}")
        print(f"  操作系统架构: {info.os_architecture}")
        print(f"  机器类型: {info.machine_type}")

if __name__ == '__main__':
    unittest.main()