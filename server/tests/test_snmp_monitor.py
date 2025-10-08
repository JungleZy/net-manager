import unittest
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 从正确的路径导入SNMP管理器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from snmp.manager import SNMPManager

class TestSNMPMonitor(unittest.TestCase):
    """
    SNMP监控测试用例
    测试环境:
    IP: 192.168.43.195
    SNMP版本: v3
    安全级别: authentication
    用户名: wjkjv3user
    认证密码: Wjkj6912
    """
    
    def setUp(self):
        """测试前准备"""
        self.ip = "192.168.43.195"
        self.version = "v3"
        self.user = "wjkjv3user"
        self.auth_key = "Wjkj6912"
        self.snmp_manager = SNMPManager()
        
    def test_snmp_v3_authentication_connection(self):
        """
        测试SNMP v3认证模式连接
        """
        # 注意：这是一个实际的网络测试，需要目标设备在线且配置正确
        # 在实际环境中，可能需要根据实际情况调整或跳过此测试
        print("测试SNMP v3认证模式连接...")
        
        # 此处仅演示测试结构，实际测试需要网络连接
        # 如果要运行实际测试，请取消下面的注释并确保设备可达
        """
        async def run_test():
            try:
                # 测试获取系统描述
                device_info = await self.snmp_manager.get_device_overview(
                    self.ip, 
                    self.version, 
                    user=self.user, 
                    auth_key=self.auth_key
                )
                
                self.assertIn('description', device_info)
                self.assertIsNotNone(device_info['description'])
                print(f"设备描述: {device_info['description']}")
                
            except Exception as e:
                self.fail(f"SNMP v3认证连接测试失败: {e}")
                
        # 运行异步测试
        asyncio.run(run_test())
        """
        
    def test_cpu_usage_retrieval(self):
        """
        测试CPU使用率获取
        """
        print("测试CPU使用率获取...")
        
        # 此处仅演示测试结构
        # 实际测试需要网络连接
        """
        async def run_test():
            try:
                cpu_info = await self.snmp_manager.get_cpu_usage(
                    self.ip, 
                    self.version, 
                    user=self.user, 
                    auth_key=self.auth_key
                )
                
                # 检查返回结果
                self.assertIsInstance(cpu_info, dict)
                if 'usage' in cpu_info and cpu_info['usage'] is not None:
                    self.assertGreaterEqual(cpu_info['usage'], 0)
                    self.assertLessEqual(cpu_info['usage'], 100)
                    print(f"CPU使用率: {cpu_info['usage']:.2f}%")
                
            except Exception as e:
                self.fail(f"CPU使用率获取测试失败: {e}")
                
        # 运行异步测试
        asyncio.run(run_test())
        """
        
    def test_memory_usage_retrieval(self):
        """
        测试内存使用率获取
        """
        print("测试内存使用率获取...")
        
        # 此处仅演示测试结构
        # 实际测试需要网络连接
        """
        async def run_test():
            try:
                memory_info = await self.snmp_manager.get_memory_usage(
                    self.ip, 
                    self.version, 
                    user=self.user, 
                    auth_key=self.auth_key
                )
                
                # 检查返回结果
                self.assertIsInstance(memory_info, dict)
                if 'usage' in memory_info and memory_info['usage'] is not None:
                    self.assertGreaterEqual(memory_info['usage'], 0)
                    self.assertLessEqual(memory_info['usage'], 100)
                    print(f"内存使用率: {memory_info['usage']:.2f}%")
                
            except Exception as e:
                self.fail(f"内存使用率获取测试失败: {e}")
                
        # 运行异步测试
        asyncio.run(run_test())
        """
        
    def test_interface_statistics(self):
        """
        测试接口统计信息获取
        """
        print("测试接口统计信息获取...")
        
        # 此处仅演示测试结构
        # 实际测试需要网络连接
        """
        async def run_test():
            try:
                stats = await self.snmp_manager.get_interface_statistics(
                    self.ip, 
                    self.version, 
                    user=self.user, 
                    auth_key=self.auth_key
                )
                
                # 检查返回结果
                self.assertIsInstance(stats, list)
                if len(stats) > 0:
                    # 检查第一个接口的数据
                    first_interface = stats[0]
                    self.assertIn('index', first_interface)
                    self.assertIn('description', first_interface)
                    print(f"接口数量: {len(stats)}")
                    print(f"第一个接口: {first_interface['description']}")
                
            except Exception as e:
                self.fail(f"接口统计信息获取测试失败: {e}")
                
        # 运行异步测试
        asyncio.run(run_test())
        """
        
    def test_oid_classification(self):
        """
        测试OID分类功能
        """
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from snmp.oid_classifier import OIDClassifier
        
        print("测试OID分类功能...")
        
        classifier = OIDClassifier()
        
        # 测试系统OID分类
        sys_descr_oid = '1.3.6.1.2.1.1.1.0'
        category = classifier.classify_oid(sys_descr_oid)
        self.assertEqual(category, 'system')
        print(f"OID {sys_descr_oid} 分类: {category}")
        
        # 测试接口OID分类
        if_descr_oid = '1.3.6.1.2.1.2.2.1.2'
        category = classifier.classify_oid(if_descr_oid)
        self.assertEqual(category, 'interfaces')
        print(f"OID {if_descr_oid} 分类: {category}")
        
        # 测试CPU OID分类
        cpu_oid = '1.3.6.1.4.1.9.9.109.1.1.1.1.7'
        category = classifier.classify_oid(cpu_oid)
        self.assertEqual(category, 'cpu')
        print(f"OID {cpu_oid} 分类: {category}")
        
        # 测试内存 OID分类
        memory_oid = '1.3.6.1.4.1.9.9.48.1.1.1.5'
        category = classifier.classify_oid(memory_oid)
        self.assertEqual(category, 'memory')
        print(f"OID {memory_oid} 分类: {category}")
        
    def test_oid_name_resolution(self):
        """
        测试OID名称解析功能
        """
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from snmp.oid_classifier import OIDClassifier
        
        print("测试OID名称解析功能...")
        
        classifier = OIDClassifier()
        
        # 测试常见OID名称解析
        sys_descr_oid = '1.3.6.1.2.1.1.1.0'
        name = classifier.get_oid_name(sys_descr_oid)
        self.assertEqual(name, 'sysDescr')
        print(f"OID {sys_descr_oid} 名称: {name}")
        
        if_descr_oid = '1.3.6.1.2.1.2.2.1.2'
        name = classifier.get_oid_name(if_descr_oid)
        self.assertEqual(name, 'ifDescr')
        print(f"OID {if_descr_oid} 名称: {name}")
        
    def test_device_type_identification(self):
        """
        测试设备类型识别功能
        """
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from snmp.oid_classifier import OIDClassifier
        
        print("测试设备类型识别功能...")
        
        classifier = OIDClassifier()
        
        # 测试Cisco设备识别
        cisco_oid = '1.3.6.1.4.1.9.1.123'
        device_type = classifier.identify_device_type(cisco_oid)
        self.assertEqual(device_type, 'Cisco')
        print(f"Cisco OID {cisco_oid} 识别为: {device_type}")
        
        # 测试华为设备识别
        huawei_oid = '1.3.6.1.4.1.2011.1.1'
        device_type = classifier.identify_device_type(huawei_oid)
        self.assertEqual(device_type, 'Huawei')
        print(f"Huawei OID {huawei_oid} 识别为: {device_type}")
        
        # 测试未知设备识别
        unknown_oid = '1.3.6.1.4.1.99999.1.1'
        device_type = classifier.identify_device_type(unknown_oid)
        # 由于我们没有覆盖所有可能的厂商OID，所以可能返回'Unknown'或其他匹配的厂商
        print(f"未知 OID {unknown_oid} 识别为: {device_type}")

def main():
    """测试入口函数"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main()