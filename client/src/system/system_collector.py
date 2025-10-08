#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统信息收集模块
负责收集客户端系统的各种信息，包括硬件、网络、进程等
"""

import psutil
import socket
import platform
import subprocess
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

# 第三方库导入
# 无

# 本地应用/库导入
from src.exceptions.exceptions import SystemInfoCollectionError
from src.utils.logger import get_logger


@dataclass
class SystemInfo:
    """系统信息数据类"""
    hostname: str
    ip_address: str
    mac_address: str
    gateway: str
    netmask: str
    services: str
    processes: str
    timestamp: str
    client_id: str = ""
    os_name: str = ""
    os_version: str = ""
    os_architecture: str = ""
    machine_type: str = ""


class SystemCollector:
    """系统信息收集器类"""
    
    def __init__(self):
        """初始化系统信息收集器"""
        self.logger = get_logger()
        self.logger.debug("初始化系统信息收集器")
    
    def get_hostname(self) -> str:
        """
        获取主机名
        
        Returns:
            str: 主机名
            
        Raises:
            SystemInfoCollectionError: 获取主机名失败
        """
        try:
            hostname = socket.gethostname()
            self.logger.debug(f"获取到主机名: {hostname}")
            return hostname
        except Exception as e:
            self.logger.error(f"获取主机名失败: {e}")
            raise SystemInfoCollectionError(f"获取主机名失败: {e}")
    
    def get_ip_address(self) -> str:
        """
        获取IP地址
        
        Returns:
            str: IP地址
            
        Raises:
            SystemInfoCollectionError: 获取IP地址失败
        """
        try:
            # 创建一个UDP socket来获取本地IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 连接到一个远程地址（不需要真实存在）
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
            
            self.logger.debug(f"获取到IP地址: {ip_address}")
            return ip_address
        except Exception as e:
            self.logger.error(f"获取IP地址失败: {e}")
            raise SystemInfoCollectionError(f"获取IP地址失败: {e}")
    
    def get_mac_address(self):
        """获取MAC地址"""
        
        try:
            # 使用psutil获取网络接口信息，选择合适的MAC地址
            import psutil
            net_if_addrs = psutil.net_if_addrs()
            
            # 查找第一个有效的物理网卡MAC地址
            mac_address = None
            for interface, addrs in net_if_addrs.items():
                # 跳过回环接口
                if interface.startswith('lo') or interface.startswith('Loopback'):
                    continue
                    
                for addr in addrs:
                    # AF_LINK在Windows上是-1，在Linux上是17，使用psutil.AF_LINK更安全
                    if addr.family == psutil.AF_LINK:
                        # 检查MAC地址是否有效（不为空且不是全0或全F）
                        if addr.address and addr.address != '00:00:00:00:00:00' and addr.address != 'ff:ff:ff:ff:ff:ff':
                            mac_address = addr.address.lower()
                            # 优先选择以太网或Wi-Fi接口
                            if 'eth' in interface.lower() or 'en' in interface.lower() or 'wl' in interface.lower() or '无线' in interface:
                                break
            
            # 如果没找到合适的接口，使用第一个有效的MAC地址
            if not mac_address:
                for interface, addrs in net_if_addrs.items():
                    for addr in addrs:
                        if addr.family == psutil.AF_LINK and addr.address and addr.address != '00:00:00:00:00:00':
                            mac_address = addr.address.lower()
                            break
                    if mac_address:
                        break
            
            if mac_address:
                self.logger.debug(f"成功获取MAC地址: {mac_address}")
                return mac_address
            else:
                self.logger.warning("未找到有效的MAC地址")
                return "unknown"
        except Exception as e:
            self.logger.error(f"获取MAC地址失败: {e}")
            return "unknown"

    def get_gateway_and_netmask(self):
        """获取网关和子网掩码"""
        try:
            # 获取网络接口统计信息
            net_if_addrs = psutil.net_if_addrs()
            
            # 获取当前使用的IP地址
            current_ip = self.get_ip_address()
            
            # 查找对应的网络接口
            gateway = "unknown"
            netmask = "unknown"
            
            for interface, addrs in net_if_addrs.items():
                for addr in addrs:
                    # 找到与当前IP匹配的地址
                    if addr.family == socket.AF_INET and addr.address == current_ip:
                        netmask = addr.netmask if addr.netmask else "unknown"
                        
                        # 在Windows上尝试获取网关
                        if platform.system() == "Windows":
                            # 尝试多种方法获取网关
                            gateway = self._get_windows_gateway(current_ip)
                        # 在Linux上尝试其他方法
                        else:
                            # 尝试多种方法获取网关
                            gateway = self._get_linux_gateway()
                        
                        # 如果获取到网关，则返回
                        if gateway != "unknown":
                            return gateway, netmask
                        
                        return gateway, netmask
            
            self.logger.warning(f"未找到IP地址 {current_ip} 对应的网关和子网掩码")
            return "unknown", "unknown"
        except Exception as e:
            self.logger.error(f"获取网关和子网掩码失败: {e}")
            return "unknown", "unknown"

    def _get_windows_gateway(self, current_ip):
        """获取Windows系统下的网关"""
        gateway = "unknown"
        try:
            # 方法1: 使用netstat命令获取路由表
            import subprocess
            result = subprocess.run(["netstat", "-rn"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # 查找默认路由
                    if line.strip().startswith('0.0.0.0') or 'default' in line.lower():
                        parts = line.split()
                        if len(parts) >= 3:
                            # 检查网关是否有效
                            gateway_candidate = parts[2]
                            if self._is_valid_ip(gateway_candidate):
                                gateway = gateway_candidate
                                self.logger.debug(f"通过netstat命令获取到网关: {gateway}")
                                break
            
            # 如果方法1失败，尝试使用route print命令
            if gateway == "unknown":
                result = subprocess.run(["route", "print"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        # 查找默认路由
                        if line.strip().startswith('0.0.0.0') and '0.0.0.0' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                # 检查网关是否有效
                                gateway_candidate = parts[3]  # Windows route print中网关在第4列
                                if self._is_valid_ip(gateway_candidate):
                                    gateway = gateway_candidate
                                    self.logger.debug(f"通过route print命令获取到网关: {gateway}")
                                    break
            
            # 如果方法2失败，尝试使用Get-NetRoute PowerShell命令
            if gateway == "unknown":
                try:
                    result = subprocess.run([
                        "powershell", 
                        "-Command", 
                        "Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -ExpandProperty NextHop"
                    ], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and result.stdout.strip():
                        gateway_candidate = result.stdout.strip().split('\n')[0]
                        if self._is_valid_ip(gateway_candidate):
                            gateway = gateway_candidate
                            self.logger.debug(f"通过PowerShell Get-NetRoute获取到网关: {gateway}")
                except Exception as e:
                    self.logger.warning(f"通过PowerShell获取网关失败: {e}")
            
            return gateway
        except subprocess.TimeoutExpired:
            self.logger.warning("获取Windows网关超时")
            return "unknown"
        except Exception as e:
            self.logger.warning(f"获取Windows网关时出错: {e}")
            return "unknown"
    
    def _get_linux_gateway(self):
        """获取Linux系统下的网关"""
        gateway = "unknown"
        try:
            # 方法1: 使用ip route命令获取默认网关
            import subprocess
            result = subprocess.run(["ip", "route"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('default'):
                        parts = line.split()
                        if len(parts) >= 3:
                            gateway_candidate = parts[2]
                            if self._is_valid_ip(gateway_candidate):
                                gateway = gateway_candidate
                                self.logger.debug(f"通过ip route命令获取到网关: {gateway}")
                                break
            
            # 如果方法1失败，尝试使用route命令
            if gateway == "unknown":
                result = subprocess.run(["route", "-n"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        # 查找默认路由
                        if line.startswith('0.0.0.0') or 'default' in line.lower():
                            parts = line.split()
                            if len(parts) >= 2:
                                gateway_candidate = parts[1]
                                if self._is_valid_ip(gateway_candidate):
                                    gateway = gateway_candidate
                                    self.logger.debug(f"通过route -n命令获取到网关: {gateway}")
                                    break
            
            # 如果方法2失败，尝试读取/proc/net/route文件
            if gateway == "unknown":
                try:
                    with open('/proc/net/route', 'r') as f:
                        lines = f.readlines()
                        for line in lines[1:]:  # 跳过标题行
                            fields = line.strip().split()
                            if len(fields) >= 3 and fields[1] == '00000000':  # 默认路由
                                # 网关地址是十六进制格式，需要转换
                                gateway_hex = fields[2]
                                gateway_ip = self._hex_to_ip(gateway_hex)
                                if gateway_ip and self._is_valid_ip(gateway_ip):
                                    gateway = gateway_ip
                                    self.logger.debug(f"通过/proc/net/route文件获取到网关: {gateway}")
                                    break
                except Exception as e:
                    self.logger.warning(f"通过/proc/net/route获取网关失败: {e}")
            
            return gateway
        except subprocess.TimeoutExpired:
            self.logger.warning("获取Linux网关超时")
            return "unknown"
        except Exception as e:
            self.logger.warning(f"获取Linux网关时出错: {e}")
            return "unknown"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """
        验证IP地址是否有效
        
        Args:
            ip (str): IP地址
            
        Returns:
            bool: IP地址是否有效
        """
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    def _hex_to_ip(self, hex_ip: str) -> str:
        """
        将十六进制IP地址转换为点分十进制格式
        
        Args:
            hex_ip (str): 十六进制IP地址
            
        Returns:
            str: 点分十进制IP地址
        """
        try:
            # 移除可能的0x前缀
            hex_ip = hex_ip.replace('0x', '')
            
            # 确保是8位十六进制数
            hex_ip = hex_ip.zfill(8)
            
            # 转换为点分十进制
            ip_parts = []
            for i in range(0, 8, 2):
                part = hex_ip[i:i+2]
                ip_parts.append(str(int(part, 16)))
            
            ip_address = '.'.join(ip_parts)
            return ip_address
        except Exception as e:
            self.logger.error(f"十六进制IP地址转换失败: {e}")
            return "0.0.0.0"
     
    def get_os_info(self):
        """
        获取操作系统信息
        
        Returns:
            str: 操作系统信息
            
        Raises:
            SystemInfoCollectionError: 获取操作系统信息失败
        """
        try:
            os_name = platform.system()
            os_version = platform.version()
            os_architecture = platform.architecture()[0]
            machine_type = platform.machine()
            
            self.logger.debug(f"成功获取操作系统信息: {os_name} {os_version} {os_architecture} {machine_type}")
            return os_name, os_version, os_architecture, machine_type
        except Exception as e:
            self.logger.error(f"获取操作系统信息失败: {e}")
            return "unknown", "unknown", "unknown", "unknown"
    
    def get_services(self) -> List[Dict[str, Any]]:
        """
        获取服务信息（网络连接信息）
        
        Returns:
            List[Dict[str, Any]]: 服务信息列表
            
        Raises:
            SystemInfoCollectionError: 获取服务信息失败
        """
        try:
            # 延迟导入logger以避免循环依赖
            from src.utils.logger import get_logger
            logger = get_logger()
            
            services = []
            connections = psutil.net_connections()
            
            for conn in connections:
                if conn.status == psutil.CONN_LISTEN:
                    # 根据连接类型确定协议
                    protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP" if conn.type == socket.SOCK_DGRAM else "Unknown"
                    
                    services.append({
                        'protocol': protocol,
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "None",
                        'status': conn.status
                    })
            
            logger.debug(f"获取到服务信息: {services}")
            return services
        except Exception as e:
            self.logger.error(f"获取服务信息失败: {e}")
            # 返回空列表而不是抛出异常，以避免影响整体系统信息收集
            return []
    
    def get_processes(self) -> List[Dict[str, Any]]:
        """
        获取进程信息
        
        Returns:
            List[Dict[str, Any]]: 进程信息列表
            
        Raises:
            SystemInfoCollectionError: 获取进程信息失败
        """
        try:
            # 延迟导入logger以避免循环依赖
            from src.utils.logger import get_logger
            logger = get_logger()
            
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'username': proc.info['username'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': round(proc.info['memory_percent'], 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # 忽略无法访问的进程
                    pass
            
            logger.debug(f"获取到进程信息，共{len(processes)}个进程")
            return processes
        except Exception as e:
            self.logger.error(f"获取进程信息失败: {e}")
            raise SystemInfoCollectionError(f"获取进程信息失败: {e}")
    
    def collect_system_info(self) -> SystemInfo:
        """
        收集完整的系统信息
        
        Returns:
            SystemInfo: 系统信息对象
            
        Raises:
            SystemInfoCollectionError: 收集系统信息失败
        """
        try:
            self.logger.info("开始收集系统信息")
            os_name, os_version, os_architecture, machine_type = self.get_os_info()
            gateway, netmask = self.get_gateway_and_netmask()
            services = self.get_services()
            processes = self.get_processes()

            from src.core.state_manager import StateManager
            client_id = StateManager().get_client_id()

             # 将服务信息转换为JSON字符串存储
            services_json = json.dumps(services, ensure_ascii=False)
            
            # 将进程信息转换为JSON字符串存储
            processes_json = json.dumps(processes, ensure_ascii=False)

            system_info = SystemInfo(
                hostname=self.get_hostname(),
                ip_address=self.get_ip_address(),
                mac_address=self.get_mac_address(),
                gateway=gateway,
                netmask=netmask,
                processes=processes_json,
                services=services_json,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                client_id=client_id or "", 
                os_name=os_name, 
                os_version=os_version, 
                os_architecture=os_architecture, 
                machine_type=machine_type
            )
            
            self.logger.info("系统信息收集完成")
            return system_info
        except Exception as e:
            self.logger.error(f"收集系统信息失败: {e}")
            raise SystemInfoCollectionError(f"收集系统信息失败: {e}")
