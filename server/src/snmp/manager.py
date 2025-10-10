import asyncio
import logging
import threading

from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from .snmp_monitor import SNMPMonitor
from .oid_classifier import OIDClassifier
from pysnmp.hlapi import *

# 配置日志
logger = logging.getLogger(__name__)

class SNMPManager:
    """
    SNMP管理器，整合SNMP监控和OID分类功能
    提供高级API来获取设备信息、CPU/内存使用率、接口流量等
    """
    
    def __init__(self):
        """初始化SNMP管理器"""
        self.monitor = SNMPMonitor()
        self.classifier = OIDClassifier()
        
    async def get_device_overview(self, ip: str, version: str, **kwargs) -> Dict[str, Any]:
        """
        获取设备概览信息
        
        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数
            
        Returns:
            包含设备概览信息的字典
        """
        overview = {}
        
        try:
            # 先进行连接性检查，尝试获取系统描述信息来验证连接
            print(f"检查设备 {ip} 连接性...")
            connection_check, success = await self.monitor.get_data(ip, version, '1.3.6.1.2.1.1.1.0', **kwargs)
            
            if not success:
                # 提供更详细的错误信息
                error_msg = f"无法连接到设备 {ip}，请检查以下可能的原因：\n"
                error_msg += "1. 设备IP地址是否正确\n"
                error_msg += "2. 设备是否开启SNMP服务\n"
                error_msg += "3. SNMP版本和认证参数是否正确\n"
                error_msg += "4. 网络连接是否正常\n"
                error_msg += "5. 防火墙是否阻止了SNMP端口(默认161)"
                
                overview['error'] = error_msg
                return overview
            
            # 获取设备基本信息
            device_info = await self.monitor.get_device_info(ip, version, **kwargs)
            overview.update(device_info)
            
            # 识别设备类型
            sys_object_id = device_info.get('object_id', '')
            
            if sys_object_id:
                device_type = self.classifier.identify_device_type(sys_object_id)
                overview['device_type'] = device_type
            
            # 获取推荐监控的OID
            device_type = overview.get('device_type', 'generic')
            recommended_oids = self.classifier.get_recommended_oids(device_type)
            overview['recommended_oids'] = recommended_oids
            
        except Exception as e:
            logger.error(f"获取设备概览信息时出错: {e}")
            error_msg = f"获取设备概览信息时出错: {str(e)}\n"
            error_msg += "请检查设备配置和网络连接"
            overview['error'] = error_msg
            
        return overview
    
    async def get_cpu_usage(self, ip: str, version: str, **kwargs) -> Dict[str, Any]:
        """
        获取CPU使用率信息
        
        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数
            
        Returns:
            包含CPU使用率信息的字典
        """
        cpu_info = {'usage': None, 'details': {}}
        
        try:
            # 尝试获取Cisco设备的CPU使用率
            value, success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.9.9.109.1.1.1.1.7', **kwargs
            )
            if success and value is not None:
                cpu_info['usage'] = float(value)
                cpu_info['source'] = 'Cisco CPM CPU'
                return cpu_info
            
            # 尝试获取UCD-SNMP-MIB的CPU使用率
            # 用户态CPU
            user_value, user_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.2021.11.9.0', **kwargs
            )
            # 系统态CPU
            system_value, system_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.2021.11.10.0', **kwargs
            )
            # 空闲CPU
            idle_value, idle_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.2021.11.11.0', **kwargs
            )
            
            if user_success and system_success and idle_success:
                user_cpu = float(user_value) if user_value else 0
                system_cpu = float(system_value) if system_value else 0
                idle_cpu = float(idle_value) if idle_value else 0
                
                total = user_cpu + system_cpu + idle_cpu
                if total > 0:
                    usage = ((user_cpu + system_cpu) / total) * 100
                    cpu_info['usage'] = usage
                    cpu_info['details'] = {
                        'user': user_cpu,
                        'system': system_cpu,
                        'idle': idle_cpu
                    }
                    cpu_info['source'] = 'UCD-SNMP-MIB'
                return cpu_info
                
        except Exception as e:
            logger.error(f"获取CPU使用率时出错: {e}")
            cpu_info['error'] = str(e)
            
        return cpu_info
    
    async def get_memory_usage(self, ip: str, version: str, **kwargs) -> Dict[str, Any]:
        """
        获取内存使用率信息
        
        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数
            
        Returns:
            包含内存使用率信息的字典
        """
        memory_info = {'usage': None, 'details': {}}
        
        try:
            # 尝试获取Cisco设备的内存使用率
            used_value, used_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.9.9.48.1.1.1.5.1', **kwargs
            )
            free_value, free_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.9.9.48.1.1.1.6.1', **kwargs
            )
            
            if used_success and free_success:
                used_mem = int(used_value) if used_value else 0
                free_mem = int(free_value) if free_value else 0
                total_mem = used_mem + free_mem
                
                if total_mem > 0:
                    usage = (used_mem / total_mem) * 100
                    memory_info['usage'] = usage
                    memory_info['details'] = {
                        'used': used_mem,
                        'free': free_mem,
                        'total': total_mem
                    }
                    memory_info['source'] = 'Cisco Memory Pool'
                return memory_info
            
            # 尝试获取UCD-SNMP-MIB的内存信息
            total_value, total_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.2021.4.5.0', **kwargs
            )
            avail_value, avail_success = await self.monitor.get_data(
                ip, version, '1.3.6.1.4.1.2021.4.6.0', **kwargs
            )
            
            if total_success and avail_success:
                total_mem = int(total_value) if total_value else 0
                avail_mem = int(avail_value) if avail_value else 0
                used_mem = total_mem - avail_mem
                
                if total_mem > 0:
                    usage = (used_mem / total_mem) * 100
                    memory_info['usage'] = usage
                    memory_info['details'] = {
                        'used': used_mem,
                        'available': avail_mem,
                        'total': total_mem
                    }
                    memory_info['source'] = 'UCD-SNMP-MIB'
                return memory_info
                
        except Exception as e:
            logger.error(f"获取内存使用率时出错: {e}")
            memory_info['error'] = str(e)
            
        return memory_info
    
    async def get_interface_statistics(self, ip: str, version: str, **kwargs) -> List[Dict[str, Any]]:
        """
        获取接口详细统计信息
        
        Args:
            ip: 设备IP地址
            version: SNMP版本
            **kwargs: 认证参数
            
        Returns:
            包含接口统计信息的列表
        """
        statistics = []
        
        try:
            # 获取接口流量统计
            traffic_stats = await self.monitor.get_interface_traffic(ip, version, **kwargs)
            
            # 获取接口基本信息
            interface_info = await self.monitor.get_interface_info(ip, version, **kwargs)
            
            # 合并信息
            for traffic in traffic_stats:
                # 查找匹配的接口信息
                iface_info = next(
                    (info for info in interface_info if info['index'] == traffic['index']),
                    {}
                )
                
                stat = {
                    'index': traffic['index'],
                    'description': traffic.get('description', iface_info.get('description', '')),
                    'in_octets': traffic.get('in_octets', 0),
                    'out_octets': traffic.get('out_octets', 0),
                    'in_discards': traffic.get('in_discards', 0),
                    'out_discards': traffic.get('out_discards', 0),
                    'in_errors': traffic.get('in_errors', 0),
                    'out_errors': traffic.get('out_errors', 0),
                    'admin_status': iface_info.get('admin_status', 0),
                    'oper_status': iface_info.get('oper_status', 0)
                }
                
                # 计算可读性更强的流量数据
                in_octets = stat['in_octets']
                out_octets = stat['out_octets']
                
                if in_octets >= 1024 * 1024 * 1024:  # GB
                    stat['in_readable'] = f"{in_octets / (1024 * 1024 * 1024):.2f} GB"
                elif in_octets >= 1024 * 1024:  # MB
                    stat['in_readable'] = f"{in_octets / (1024 * 1024):.2f} MB"
                elif in_octets >= 1024:  # KB
                    stat['in_readable'] = f"{in_octets / 1024:.2f} KB"
                else:  # B
                    stat['in_readable'] = f"{in_octets} B"
                    
                if out_octets >= 1024 * 1024 * 1024:  # GB
                    stat['out_readable'] = f"{out_octets / (1024 * 1024 * 1024):.2f} GB"
                elif out_octets >= 1024 * 1024:  # MB
                    stat['out_readable'] = f"{out_octets / (1024 * 1024):.2f} MB"
                elif out_octets >= 1024:  # KB
                    stat['out_readable'] = f"{out_octets / 1024:.2f} KB"
                else:  # B
                    stat['out_readable'] = f"{out_octets} B"
                
                statistics.append(stat)
                
        except Exception as e:
            logger.error(f"获取接口统计信息时出错: {e}")
            # 返回基本的流量统计作为备用
            statistics = await self.monitor.get_interface_traffic(ip, version, **kwargs)
            
        return statistics
    
    async def get_custom_oids(self, ip: str, version: str, oids: List[str], **kwargs) -> Dict[str, Any]:
        """
        批量获取自定义OID的数据
        
        Args:
            ip: 设备IP地址
            version: SNMP版本
            oids: OID列表
            **kwargs: 认证参数
            
        Returns:
            包含OID数据的字典
        """
        results = {}
        
        try:
            # 并行获取所有OID的数据
            tasks = [
                self.monitor.get_data(ip, version, oid, **kwargs)
                for oid in oids
            ]
            
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(task_results):
                oid = oids[i]
                if isinstance(result, Exception):
                    results[oid] = {
                        'error': str(result),
                        'name': self.classifier.get_oid_name(oid),
                        'category': self.classifier.classify_oid(oid)
                    }
                else:
                    value, success = result
                    if success:
                        parsed_data = self.classifier.parse_oid_value(oid, value)
                        results[oid] = parsed_data
                    else:
                        results[oid] = {
                            'error': 'Failed to retrieve data',
                            'name': self.classifier.get_oid_name(oid),
                            'category': self.classifier.classify_oid(oid)
                        }
                        
        except Exception as e:
            logger.error(f"获取自定义OID数据时出错: {e}")
            results['error'] = str(e)
            
        return results
    
    @staticmethod
    def snmp_discovery_arp(network, iface=None):
        """使用Ping方式发现本地网络设备"""
        print("正在进行Ping发现...")
        devices = []
        
        try:
            # 解析网络地址
            import ipaddress
            import subprocess
            import platform
            import time
            import asyncio
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            network_obj = ipaddress.ip_network(network, strict=False)
            
            # 根据平台设置ping命令参数
            system = platform.system().lower()
            if system == "windows":
                ping_cmd = ["ping", "-n", "1", "-w", "1000"]  # Windows: -w is timeout in milliseconds
            else:
                ping_cmd = ["ping", "-c", "1", "-W", "1"]     # Linux/macOS: -W is timeout in seconds
            
            # 记录开始时间
            start_time = time.time()
            
            # 使用线程池并行执行ping命令以提高速度
            def ping_host(ip):
                try:
                    cmd = ping_cmd + [str(ip)]
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=2
                    )
                    # 如果返回码为0，表示设备在线
                    return str(ip) if result.returncode == 0 else None
                except Exception:
                    return None
            
            # 使用线程池并发执行ping，最大并发数为100
            hosts = [str(ip) for ip in network_obj.hosts()]
            with ThreadPoolExecutor(max_workers=100) as executor:
                # 提交所有任务
                future_to_ip = {executor.submit(ping_host, ip): ip for ip in hosts}
                
                # 收集结果
                for future in as_completed(future_to_ip):
                    result = future.result()
                    if result:
                        devices.append(result)
            
            elapsed_time = time.time() - start_time
            print(f"Ping发现完成，耗时 {elapsed_time:.2f} 秒")
            
        except Exception as e:
            print(f"Ping发现过程中出现错误: {e}")
            # 返回已发现的设备，而不是空列表
            pass
        
        print(f"Ping发现找到 {len(devices)} 个设备")
        return devices
    
    async def snmp_scan_device(self, ip, version="v2c", community='public'):
        """扫描单个设备的SNMP信息"""
        try:
            print(f"正在扫描设备 {ip}")
            # 获取系统信息
            connection_check, success = await self.monitor.get_data(ip, version, '1.3.6.1.2.1.1.1.0', community=community)
            if success:
                return ip
                    
        except Exception as e:
            logger.error(f"扫描设备 {ip} 时出错: {e}")
            return None
        
        return None
    
    async def scan_network_devices(self, network="192.168.1.0/24", version="v2c", community='public', iface=None) -> List[Dict[str, Any]]:
        """综合SNMP发现"""
        # 使用ARP发现设备，支持指定网络接口
        devices = SNMPManager.snmp_discovery_arp(network, iface=iface)
        print(f"发现 {len(devices)} 个设备:\n {devices}")
        
        # 异步SNMP扫描，控制并发数
        snmp_devices = []
        
        # 分批处理设备，每批最多30个设备以控制并发数
        batch_size = 30
        for i in range(0, len(devices), batch_size):
            batch = devices[i:i+batch_size]
            batch_results = []
            
            # 对每批设备进行扫描
            for ip in batch:
                try:
                    result = await self.snmp_scan_device(ip, version, community)
                    batch_results.append(result)
                except Exception as e:
                    logger.error(f"扫描设备 {ip} 时出错: {e}")
                    batch_results.append(None)
            
            # 处理批次结果
            for result in batch_results:
                if result:
                    snmp_devices.append(result)
        print(f"发现 {len(snmp_devices)} 个SNMP设备:\n {snmp_devices}")
        return snmp_devices

# 导出公共接口
__all__ = ['SNMPManager']