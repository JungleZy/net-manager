import unittest
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.system_collector import SystemCollector
from src.models import SystemInfo

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
    
    def test_collect_system_info(self):
        """测试收集完整系统信息"""
        info = self.collector.collect_system_info()
        self.assertIsInstance(info, SystemInfo)
        
        # 检查所有属性是否存在且不为空
        self.assertIsInstance(info.hostname, str)
        self.assertGreater(len(info.hostname), 0)
        
        self.assertIsInstance(info.ip_address, str)
        self.assertGreater(len(info.ip_address), 0)
        
        self.assertIsInstance(info.mac_address, str)
        self.assertGreater(len(info.mac_address), 0)
        
        # 检查服务信息是否为字符串（JSON格式）
        self.assertIsInstance(info.services, str)
        # 尝试解析JSON
        services = json.loads(info.services)
        self.assertIsInstance(services, list)
        self.assertGreater(len(services), 0)
        
        # 检查时间戳
        self.assertIsNotNone(info.timestamp)
        
        print(f"完整系统信息对象创建成功")
        print(f"  主机名: {info.hostname}")
        print(f"  IP地址: {info.ip_address}")
        print(f"  MAC地址: {info.mac_address}")
        print(f"  服务数量: {len(services)}")
        print(f"  时间戳: {info.timestamp}")

if __name__ == '__main__':
    unittest.main()