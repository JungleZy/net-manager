#!/usr/bin/env python3
"""
测试多播服务发现修复功能
验证对"errno 19 no such device"错误的处理
"""

import sys
import os
import time
import logging
import socket
import platform
import netifaces
import psutil
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "client"))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_multicast_fix")

# 直接导入UDPClient类
from client.src.network.udp_client import UDPClient

def test_multicast_error_handling():
    """测试多播错误处理"""
    logger.info("测试多播错误处理...")
    
    client = UDPClient()
    
    # 模拟多播组加入失败，触发"errno 19 no such device"错误
    with patch('socket.socket') as mock_socket:
        # 创建模拟socket
        mock_listen_socket = MagicMock()
        mock_send_socket = MagicMock()
        
        # 配置socket模拟
        mock_socket.return_value = mock_listen_socket
        
        # 模拟绑定成功但加入多播组失败
        mock_listen_socket.setsockopt.side_effect = [
            None,  # SO_REUSEADDR设置成功
            OSError("errno 19 no such device"),  # IP_ADD_MEMBERSHIP失败
        ]
        
        # 模拟广播发现成功
        with patch.object(client, 'discover_server_broadcast') as mock_broadcast:
            mock_broadcast.return_value = ("192.168.1.100", 8080)
            
            # 执行多播发现
            result = client.discover_server_multicast()
            
            # 验证结果
            assert result == ("192.168.1.100", 8080), f"期望返回广播结果，但得到: {result}"
            assert mock_broadcast.called, "广播发现应该被调用"
            
            logger.info("✓ 多播错误处理测试通过 - 成功回退到广播方式")

def test_interface_validation():
    """测试接口验证功能"""
    logger.info("测试接口验证功能...")
    
    client = UDPClient()
    
    # 测试无效多播地址
    is_valid, error_msg = client._validate_multicast_setup("invalid_address", 37020)
    assert not is_valid, "无效多播地址应该被拒绝"
    assert "无效的多播组地址" in error_msg, f"错误消息应该包含地址验证信息: {error_msg}"
    
    # 测试无效端口
    is_valid, error_msg = client._validate_multicast_setup("239.255.1.1", 70000)
    assert not is_valid, "无效端口应该被拒绝"
    assert "无效的端口" in error_msg, f"错误消息应该包含端口验证信息: {error_msg}"
    
    # 测试有效配置
    is_valid, error_msg = client._validate_multicast_setup("239.255.1.1", 37020)
    assert is_valid, f"有效的多播配置应该通过验证: {error_msg}"
    
    logger.info("✓ 接口验证功能测试通过")

def test_interface_multicast_capability():
    """测试接口多播能力检查"""
    logger.info("测试接口多播能力检查...")
    
    client = UDPClient()
    
    # 测试Windows系统
    with patch('platform.system', return_value='Windows'):
        # 模拟接口信息
        interface = {
            "name": "以太网",
            "ip": "192.168.1.100"
        }
        
        # 模拟netifaces接口
        with patch('netifaces.ifaddresses') as mock_ifaddresses:
            mock_ifaddresses.return_value = {
                netifaces.AF_INET: [{
                    'addr': '192.168.1.100',
                    'netmask': '255.255.255.0'
                }]
            }
            
            is_capable, error_msg = client._check_interface_multicast_capability(interface)
            assert is_capable, f"Windows接口应该支持多播: {error_msg}"
    
    # 测试Linux系统
    with patch('platform.system', return_value='Linux'):
        # 模拟接口信息
        interface = {
            "name": "eth0",
            "ip": "192.168.1.100"
        }
        
        # 模拟proc文件系统
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value = mock_file
                mock_file.read.return_value = "6\n"
                mock_open.return_value = mock_file
                
                is_capable, error_msg = client._check_interface_multicast_capability(interface)
                assert is_capable, f"Linux接口应该支持多播: {error_msg}"
    
    logger.info("✓ 接口多播能力检查测试通过")

def test_interface_refresh():
    """测试接口刷新功能"""
    logger.info("测试接口刷新功能...")
    
    client = UDPClient()
    
    # 模拟psutil
    with patch('psutil.net_if_addrs') as mock_if_addrs, \
         patch('psutil.net_if_stats') as mock_if_stats:
        
        # 模拟接口数据
        mock_if_addrs.return_value = {
            "eth0": [
                MagicMock(family=socket.AF_INET, address="192.168.1.100"),
                MagicMock(family=socket.AF_INET6, address="fe80::1"),
            ],
            "lo": [
                MagicMock(family=socket.AF_INET, address="127.0.0.1"),
            ]
        }
        
        mock_if_stats.return_value = {
            "eth0": MagicMock(isup=True),
            "lo": MagicMock(isup=True)
        }
        
        # 模拟netifaces
        with patch('netifaces.ifaddresses') as mock_ifaddresses:
            mock_ifaddresses.return_value = {
                netifaces.AF_INET: [{
                    'addr': '192.168.1.100',
                    'netmask': '255.255.255.0'
                }]
            }
            
            # 调用刷新方法
            interfaces = client.refresh_network_interfaces()
            
            # 验证结果
            assert len(interfaces) == 1, f"应该有一个非回环接口，但找到: {len(interfaces)}"
            assert interfaces[0]["ip"] == "192.168.1.100", f"接口IP应该是192.168.1.100，但得到: {interfaces[0]['ip']}"
            assert interfaces[0].get("is_multicast_capable", False), "接口应该支持多播"
    
    logger.info("✓ 接口刷新功能测试通过")

def test_multicast_discovery_with_validation():
    """测试带验证的多播发现"""
    logger.info("测试带验证的多播发现...")
    
    client = UDPClient()
    
    # 模拟验证失败
    with patch.object(client, '_validate_multicast_setup') as mock_validate:
        mock_validate.return_value = (False, "模拟验证失败")
        
        # 模拟广播发现成功
        with patch.object(client, 'discover_server_broadcast') as mock_broadcast:
            mock_broadcast.return_value = ("192.168.1.100", 8080)
            
            # 执行多播发现
            result = client.discover_server_multicast()
            
            # 验证结果
            assert result == ("192.168.1.100", 8080), f"期望返回广播结果，但得到: {result}"
            assert mock_validate.called, "多播验证应该被调用"
            assert mock_broadcast.called, "广播发现应该被调用"
    
    logger.info("✓ 带验证的多播发现测试通过")

def main():
    """运行所有测试"""
    logger.info("开始测试多播服务发现修复功能...")
    
    try:
        test_multicast_error_handling()
        test_interface_validation()
        test_interface_multicast_capability()
        test_interface_refresh()
        test_multicast_discovery_with_validation()
        
        logger.info("✅ 所有测试通过！多播服务发现修复功能正常工作。")
        return 0
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())