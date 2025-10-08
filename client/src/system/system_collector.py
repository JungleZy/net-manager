import psutil
import socket
import json
import platform
import uuid
import threading
from datetime import datetime
from typing import List, Dict, Any
from ..utils.logger import logger

class SystemInfo:
    """系统信息模型"""
    def __init__(self, hostname: str, ip_address: str, mac_address: str, 
                 gateway: str, netmask: str, services: str, processes: str, timestamp: str,
                 client_id: str = "", os_name: str = "", os_version: str = "", 
                 os_architecture: str = "", machine_type: str = ""):
        self.hostname = hostname
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.gateway = gateway
        self.netmask = netmask
        self.services = services  # 存储为JSON字符串
        self.processes = processes  # 存储为JSON字符串
        self.timestamp = timestamp
        self.client_id = client_id  # 客户端唯一标识符
        self.os_name = os_name  # 操作系统名称
        self.os_version = os_version  # 操作系统版本
        self.os_architecture = os_architecture  # 操作系统架构
        self.machine_type = machine_type  # 机器类型

class SystemCollector:
    """系统信息收集器"""
    
    def __init__(self):
        self._cache = {}  # 缓存一些不经常变化的信息
        self._cache_lock = threading.Lock()
        self._cache_ttl = 300  # 缓存5分钟
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        with self._cache_lock:
            if key not in self._cache:
                return False
            timestamp, _ = self._cache[key]
            return (datetime.now() - timestamp).total_seconds() < self._cache_ttl
    
    def _get_from_cache(self, key: str) -> Any:
        """从缓存获取数据"""
        with self._cache_lock:
            if key in self._cache:
                return self._cache[key][1]
            return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        with self._cache_lock:
            self._cache[key] = (datetime.now(), value)
    
    def get_hostname(self):
        """获取主机名"""
        cache_key = "hostname"
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            hostname = socket.gethostname()
            logger.debug(f"成功获取主机名: {hostname}")
            self._set_cache(cache_key, hostname)
            return hostname
        except Exception as e:
            logger.error(f"获取主机名失败: {e}")
            return "unknown"
    
    def get_ip_address(self):
        """获取本机IP地址"""
        cache_key = "ip_address"
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            # 创建一个UDP连接来获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 连接到远程地址（不会真正发送数据）
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            logger.debug(f"成功获取IP地址: {ip}")
            self._set_cache(cache_key, ip)
            return ip
        except Exception as e:
            logger.error(f"获取IP地址失败: {e}")
            # 如果无法连接，则返回回环地址
            return "127.0.0.1"
    
    def get_mac_address(self):
        """获取MAC地址"""
        cache_key = "mac_address"
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
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
                logger.debug(f"成功获取MAC地址: {mac_address}")
                self._set_cache(cache_key, mac_address)
                return mac_address
            else:
                logger.warning("未找到有效的MAC地址")
                return "unknown"
        except Exception as e:
            logger.error(f"获取MAC地址失败: {e}")
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
            
            logger.warning(f"未找到IP地址 {current_ip} 对应的网关和子网掩码")
            return "unknown", "unknown"
        except Exception as e:
            logger.error(f"获取网关和子网掩码失败: {e}")
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
                                logger.debug(f"通过netstat命令获取到网关: {gateway}")
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
                                    logger.debug(f"通过route print命令获取到网关: {gateway}")
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
                            logger.debug(f"通过PowerShell Get-NetRoute获取到网关: {gateway}")
                except Exception as e:
                    logger.warning(f"通过PowerShell获取网关失败: {e}")
            
            return gateway
        except subprocess.TimeoutExpired:
            logger.warning("获取Windows网关超时")
            return "unknown"
        except Exception as e:
            logger.warning(f"获取Windows网关时出错: {e}")
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
                                logger.debug(f"通过ip route命令获取到网关: {gateway}")
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
                                    logger.debug(f"通过route -n命令获取到网关: {gateway}")
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
                                    logger.debug(f"通过/proc/net/route文件获取到网关: {gateway}")
                                    break
                except Exception as e:
                    logger.warning(f"通过/proc/net/route获取网关失败: {e}")
            
            return gateway
        except subprocess.TimeoutExpired:
            logger.warning("获取Linux网关超时")
            return "unknown"
        except Exception as e:
            logger.warning(f"获取Linux网关时出错: {e}")
            return "unknown"
    
    def _is_valid_ip(self, ip):
        """检查IP地址是否有效"""
        if not ip or ip == "unknown":
            return False
        try:
            import ipaddress
            ipaddress.ip_address(ip)
            return True
        except Exception:
            return False
    
    def _hex_to_ip(self, hex_ip):
        """将十六进制IP地址转换为点分十进制格式"""
        try:
            # 十六进制转换为整数，然后转换为IP地址
            import struct
            import socket
            # 确保是8个字符的十六进制字符串
            if len(hex_ip) == 8:
                # 转换为字节并解包为IP地址
                ip_bytes = bytes.fromhex(hex_ip)
                ip_address = socket.inet_ntoa(ip_bytes)
                return ip_address
        except Exception as e:
            logger.warning(f"十六进制IP转换失败: {e}")
        return None
    
    def get_services(self):
        """获取运行的服务和端口信息，包括使用该端口的进程信息"""
        services = []
        try:
            # 获取网络连接信息
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == psutil.CONN_LISTEN:
                    service_info = {
                        "protocol": "TCP",
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "status": conn.status,
                        "pid": conn.pid if conn.pid else None,
                        "process_name": None
                    }
                    
                    # 如果有PID信息，获取进程名称
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            service_info["process_name"] = process.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    services.append(service_info)
            
            # 获取UDP连接信息
            udp_connections = psutil.net_connections(kind='udp')
            for conn in udp_connections:
                if conn.laddr:
                    service_info = {
                        "protocol": "UDP",
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "status": "LISTENING",
                        "pid": conn.pid if conn.pid else None,
                        "process_name": None
                    }
                    
                    # 如果有PID信息，获取进程名称
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            service_info["process_name"] = process.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    services.append(service_info)
            
            logger.debug(f"成功获取服务信息，共 {len(services)} 个服务")
        except Exception as e:
            logger.error(f"获取服务信息出错: {e}")
        
        return services
    
    def get_processes(self):
        """获取当前运行的所有进程信息，包括进程占用的端口信息"""
        processes = []
        try:
            # 遍历所有进程
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    process_info = {
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "status": proc.info['status'],
                        "cpu_percent": proc.info['cpu_percent'] or 0.0,
                        "memory_percent": round(proc.info['memory_percent'] or 0.0, 2),
                        "ports": []  # 添加端口信息
                    }
                    
                    # 获取进程占用的端口信息
                    try:
                        process = psutil.Process(proc.info['pid'])
                        connections = process.connections()
                        for conn in connections:
                            # 只收集监听状态的连接
                            if conn.status == psutil.CONN_LISTEN:
                                port_info = {
                                    "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                                }
                                process_info["ports"].append(port_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # 如果无法获取连接信息，跳过
                        pass
                    
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # 忽略无法访问的进程
                    pass
            
            logger.debug(f"成功获取进程信息，共 {len(processes)} 个进程")
        except Exception as e:
            logger.error(f"获取进程信息出错: {e}")
        
        return processes
    
    def collect_system_info(self):
        """收集完整的系统信息"""
        try:
            hostname = self.get_hostname()
            ip_address = self.get_ip_address()
            mac_address = self.get_mac_address()
            gateway, netmask = self.get_gateway_and_netmask()
            services = self.get_services()
            processes = self.get_processes()
            os_name, os_version, os_architecture, machine_type = self.get_os_info()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 将服务信息转换为JSON字符串存储
            services_json = json.dumps(services, ensure_ascii=False)
            
            # 将进程信息转换为JSON字符串存储
            processes_json = json.dumps(processes, ensure_ascii=False)
            
            # 获取全局的客户端唯一标识符
            # 使用状态管理器获取client_id
            try:
                from ..core.state_manager import get_state_manager
                state_manager = get_state_manager()
                client_id = state_manager.get_client_id()
            except Exception as e:
                logger.error(f"从状态管理器获取client_id失败: {e}")
                client_id = ''
            
            return SystemInfo(hostname, ip_address, mac_address, gateway, netmask, services_json, processes_json, timestamp, client_id or "", os_name, os_version, os_architecture, machine_type)
        except Exception as e:
            logger.error(f"收集系统信息时发生错误: {e}")
            raise

    def get_os_info(self):
        """获取操作系统信息"""
        try:
            os_name = platform.system()
            os_version = platform.version()
            os_architecture = platform.architecture()[0]
            machine_type = platform.machine()
            
            logger.debug(f"成功获取操作系统信息: {os_name} {os_version} {os_architecture} {machine_type}")
            return os_name, os_version, os_architecture, machine_type
        except Exception as e:
            logger.error(f"获取操作系统信息失败: {e}")
            return "unknown", "unknown", "unknown", "unknown"