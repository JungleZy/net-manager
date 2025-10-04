import psutil
import socket
import json
import platform
import uuid
from datetime import datetime
from src.models import SystemInfo
from src.logger import logger

class SystemCollector:
    """系统信息收集器"""
    
    def get_hostname(self):
        """获取主机名"""
        try:
            hostname = socket.gethostname()
            logger.info(f"成功获取主机名: {hostname}")
            return hostname
        except Exception as e:
            logger.error(f"获取主机名失败: {e}")
            return "unknown"
    
    def get_ip_address(self):
        """获取本机IP地址"""
        try:
            # 创建一个UDP连接来获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 连接到远程地址（不会真正发送数据）
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            logger.info(f"成功获取IP地址: {ip}")
            return ip
        except Exception as e:
            logger.error(f"获取IP地址失败: {e}")
            # 如果无法连接，则返回回环地址
            return "127.0.0.1"
    
    def get_mac_address(self):
        """获取MAC地址"""
        try:
            # 获取本机MAC地址
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            logger.info(f"成功获取MAC地址: {mac}")
            return mac
        except Exception as e:
            logger.error(f"获取MAC地址失败: {e}")
            return "unknown"
    
    def get_services(self):
        """获取运行的服务和端口信息"""
        services = []
        try:
            # 获取网络连接信息
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == psutil.CONN_LISTEN:
                    service_info = {
                        "protocol": "TCP",
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "status": conn.status
                    }
                    services.append(service_info)
            
            # 获取UDP连接信息
            udp_connections = psutil.net_connections(kind='udp')
            for conn in udp_connections:
                if conn.laddr:
                    service_info = {
                        "protocol": "UDP",
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "status": "LISTENING"
                    }
                    services.append(service_info)
            
            logger.info(f"成功获取服务信息，共 {len(services)} 个服务")
        except Exception as e:
            logger.error(f"获取服务信息出错: {e}")
        
        return services
    
    def get_processes(self):
        """获取当前运行的所有进程信息"""
        processes = []
        try:
            # 遍历所有进程
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    # 获取进程信息
                    process_info = {
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "username": proc.info['username'] or "unknown",
                        "status": proc.info['status'],
                        "cpu_percent": proc.info['cpu_percent'] or 0.0,
                        "memory_percent": round(proc.info['memory_percent'] or 0.0, 2)
                    }
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # 忽略无法访问的进程
                    pass
            
            logger.info(f"成功获取进程信息，共 {len(processes)} 个进程")
        except Exception as e:
            logger.error(f"获取进程信息出错: {e}")
        
        return processes
    
    def collect_system_info(self):
        """收集完整的系统信息"""
        hostname = self.get_hostname()
        ip_address = self.get_ip_address()
        mac_address = self.get_mac_address()
        services = self.get_services()
        processes = self.get_processes()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 将服务信息转换为JSON字符串存储
        services_json = json.dumps(services, ensure_ascii=False)
        
        # 将进程信息转换为JSON字符串存储
        processes_json = json.dumps(processes, ensure_ascii=False)
        
        return SystemInfo(hostname, ip_address, mac_address, services_json, processes_json, timestamp)