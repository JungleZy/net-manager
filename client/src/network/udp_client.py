#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP客户端模块
负责通过多播和UDP广播发现服务端
"""

import socket
import struct
import time
import json
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from functools import lru_cache

# 导入自定义异常类
from src.exceptions.exceptions import NetworkDiscoveryError

from src.utils.logger import get_logger

# 导入psutil，确保模块级别有这个属性
try:
    import psutil
except ImportError:
    psutil = None


class UDPClient:
    """UDP客户端类，负责服务发现"""

    def __init__(self):
        """初始化UDP客户端"""
        # 延迟导入config，使用正确的相对导入路径
        from ..config_module.config import config

        self.broadcast_address = config.get_server_broadcast_address()
        self.broadcast_port = config.get_server_broadcast_port()

        # 初始化logger
        self.logger = get_logger()

        self.logger.debug("UDP客户端初始化完成")

    def discover_server_multicast(self) -> Optional[Tuple[str, int]]:
        """
        通过多播发现服务端

        Returns:
            Optional[Tuple[str, int]]: 服务端地址和端口，如果发现失败则返回None
        """
        self.logger.info("开始多播服务发现")

        # 多播配置
        MULTICAST_GROUP = "239.255.1.1"
        MULTICAST_PORT = 37020
        DISCOVERY_TIMEOUT = 5  # 5秒超时

        # 验证多播设置
        is_valid, error_msg = self._validate_multicast_setup(MULTICAST_GROUP, MULTICAST_PORT)
        if not is_valid:
            self.logger.error(f"多播设置验证失败: {error_msg}")
            self.logger.info("尝试使用广播方式作为回退方案")
            return self.discover_server_broadcast()

        discovered_services = {}
        discovery_id = int(time.time() * 1000) % 1000000  # 生成一个发现ID

        listen_socket = None
        send_socket = None

        try:
            # 检查是否有可用的网络接口
            active_interfaces = self.refresh_network_interfaces()
            if not active_interfaces:
                self.logger.warning("未找到活跃的网络接口，多播服务发现可能会失败")
            
            # 优先选择支持多播的接口
            multicast_interfaces = [iface for iface in active_interfaces if iface.get("is_multicast_capable", True)]
            if multicast_interfaces:
                self.logger.info(f"找到 {len(multicast_interfaces)} 个支持多播的网络接口")
            else:
                self.logger.warning("没有找到明确支持多播的网络接口，将尝试使用所有可用接口")
            
            # 创建发送socket
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ttl = struct.pack("b", 32)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

            # 创建监听socket
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 尝试绑定到多播端口，如果失败则尝试绑定到特定接口
            try:
                listen_socket.bind(("", MULTICAST_PORT))
            except OSError as e:
                self.logger.warning(f"绑定到所有接口失败: {e}，尝试绑定到特定接口")
                
                # 尝试绑定到第一个活跃的非回环接口
                bind_success = False
                for interface in active_interfaces:
                    try:
                        listen_socket.bind((interface["ip"], MULTICAST_PORT))
                        self.logger.info(f"成功绑定到接口 {interface['name']} ({interface['ip']})")
                        bind_success = True
                        break
                    except OSError as bind_error:
                        self.logger.debug(f"绑定到接口 {interface['name']} ({interface['ip']}) 失败: {bind_error}")
                        continue
                
                if not bind_success:
                    raise OSError("无法绑定到任何网络接口进行多播监听")

            # 尝试加入多播组，处理可能的错误
            try:
                group = socket.inet_aton(MULTICAST_GROUP)
                mreq = struct.pack("4sL", group, socket.INADDR_ANY)
                listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                self.logger.info(f"成功加入多播组 {MULTICAST_GROUP}")
            except OSError as e:
                self.logger.error(f"加入多播组失败: {e}")
                # 如果加入多播组失败，尝试使用特定接口
                if active_interfaces:
                    # 优先尝试支持多播的接口
                    interfaces_to_try = multicast_interfaces if multicast_interfaces else active_interfaces
                    
                    for interface in interfaces_to_try:
                        try:
                            interface_ip = interface["ip"]
                            group = socket.inet_aton(MULTICAST_GROUP)
                            mreq = struct.pack("4sL", group, socket.inet_aton(interface_ip))
                            listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                            self.logger.info(f"使用接口 {interface['name']} ({interface_ip}) 成功加入多播组 {MULTICAST_GROUP}")
                            break
                        except OSError as interface_error:
                            self.logger.debug(f"使用接口 {interface['name']} ({interface_ip}) 加入多播组失败: {interface_error}")
                            continue
                    else:
                        raise OSError("无法使用任何接口加入多播组")
                else:
                    raise OSError(f"无法加入多播组且没有可用接口: {e}")

            listen_socket.settimeout(1.0)

            self.logger.info("开始监听响应...")

            # 发送发现查询
            query_msg = f"DISCOVER|ANY|{discovery_id}"
            send_socket.sendto(query_msg.encode(), (MULTICAST_GROUP, MULTICAST_PORT))
            self.logger.info(f"发送多播查询: {query_msg}")

            # 等待响应
            start_time = time.time()
            while time.time() - start_time < DISCOVERY_TIMEOUT:
                try:
                    data, addr = listen_socket.recvfrom(1024)
                    response = data.decode("utf-8", errors="replace")

                    self.logger.debug(f"收到响应: {response} 来自 {addr}")

                    # 解析响应
                    if data.startswith(b"{"):  # JSON格式的响应
                        try:
                            response_data = json.loads(response)
                            if response_data.get("type") == "discovery_response":
                                server_ip = addr[0]
                                server_port = response_data.get("tcp_port")

                                if server_ip and server_port:
                                    if isinstance(server_port, str):
                                        server_port = int(server_port)
                                    service_key = f"{server_ip}:{server_port}"
                                    discovered_services[service_key] = {
                                        "address": server_ip,
                                        "port": server_port,
                                        "discovery_time": datetime.now().isoformat(),
                                    }
                                    self.logger.info(
                                        f"发现服务端: {server_ip}:{server_port}"
                                    )
                        except json.JSONDecodeError:
                            pass

                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"接收响应错误: {e}")
                    break

            # 返回发现的第一个服务（如果有）
            if discovered_services:
                first_service = list(discovered_services.values())[0]
                return (first_service["address"], first_service["port"])
            else:
                self.logger.warning("未能发现任何服务端")
                return None

        except OSError as e:
            error_msg = str(e)
            self.logger.error(f"多播服务发现过程中出现网络错误: {error_msg}")
            
            # 特殊错误处理
            if "errno 19" in error_msg or "No such device" in error_msg:
                self.logger.error("网络设备不存在或不可用，可能是因为网络接口被禁用或不存在")
                self.logger.info("尝试使用广播方式作为回退方案")
                # 回退到广播方式
                return self.discover_server_broadcast()
            
            # 其他网络错误
            self.logger.error(f"多播服务发现失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"多播服务发现过程中出错: {e}")
            return None
        finally:
            if listen_socket:
                listen_socket.close()
            if send_socket:
                send_socket.close()

    def discover_server_broadcast(self) -> Optional[Tuple[str, int]]:
        """
        通过UDP广播发现服务端

        Returns:
            Optional[Tuple[str, int]]: 服务端地址和端口，如果发现失败则返回None
        """
        self.logger.info("开始UDP广播服务发现")

        # 强制刷新网络接口信息，确保获取最新的IP地址
        active_interfaces = self.refresh_network_interfaces()

        if not active_interfaces:
            self.logger.error("未找到活跃的网络接口")
            return None

        self.logger.info(f"发现 {len(active_interfaces)} 个活跃网络接口")

        # 轮询每个活跃接口的每个IP地址进行服务发现
        for interface in active_interfaces:
            interface_name = interface["name"]
            interface_ip = interface["ip"]

            self.logger.info(
                f"尝试通过接口 {interface_name} ({interface_ip}) 进行服务发现"
            )

            sock = None  # 初始化sock变量
            try:
                # 创建临时socket绑定到特定接口进行服务发现
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((interface_ip, 0))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.settimeout(3.0)  # 3秒超时

                # 发送发现消息
                discovery_message = {
                    "type": "discovery",
                    "timestamp": datetime.now().isoformat(),
                }

                self.logger.info(
                    f"发送服务发现广播到 {self.broadcast_address}:{self.broadcast_port}"
                )
                sock.sendto(
                    json.dumps(discovery_message).encode("utf-8"),
                    (self.broadcast_address, self.broadcast_port),
                )

                # 等待响应
                data, addr = sock.recvfrom(1024)
                response = json.loads(data.decode("utf-8"))

                if response.get("type") == "discovery_response":
                    server_ip = addr[0]
                    # 确保server_port是整数类型
                    server_port = response.get("tcp_port")

                    if server_ip and server_port:
                        if isinstance(server_port, str):
                            server_port = int(server_port)
                        self.logger.info(
                            f"通过接口 {interface_name} ({interface_ip}) 成功发现服务端: {server_ip}:{server_port}"
                        )
                        sock.close()
                        return (server_ip, server_port)
            except socket.timeout:
                self.logger.warning(
                    f"通过接口 {interface_name} ({interface_ip}) 进行服务发现超时"
                )
            except Exception as e:
                self.logger.error(
                    f"通过接口 {interface_name} ({interface_ip}) 进行服务发现时出错: {e}"
                )
            finally:
                if sock is not None:
                    sock.close()

        self.logger.warning("通过所有活跃接口均未能发现服务端")
        return None

    def refresh_network_interfaces(self) -> List[Dict[str, Any]]:
        """
        强制刷新并获取最新的网络接口列表
        
        Returns:
            List[Dict[str, Any]]: 包含接口名称和IP地址的字典列表
        """
        self.logger.info("强制刷新网络接口信息")
        return self._get_active_interfaces()

    def _get_active_interfaces(self) -> List[Dict[str, Any]]:
        """
        获取活跃的网络接口列表

        Returns:
            List[Dict[str, Any]]: 包含接口名称和IP地址的字典列表
        """
        active_interfaces = []

        try:
            # 检查psutil是否可用
            if psutil is None:
                self.logger.error("psutil模块不可用，无法获取网络接口信息")
                return active_interfaces

            # 获取网络接口状态
            net_if_stats = psutil.net_if_stats()
            # 获取网络接口地址信息
            net_if_addrs = psutil.net_if_addrs()

            # 遍历所有网络接口
            for interface_name, interface_stats in net_if_stats.items():
                # 检查接口是否活跃
                if interface_stats.isup:
                    # 处理psutil版本兼容性问题，使用is_loopback替代isloopback
                    is_loopback = getattr(
                        interface_stats,
                        "isloopback",
                        getattr(interface_stats, "is_loopback", False),
                    )

                    # 排除回环接口
                    if not is_loopback:
                        # 获取该接口的所有IPv4地址
                        if interface_name in net_if_addrs:
                            for addr in net_if_addrs[interface_name]:
                                # 只处理IPv4地址
                                if addr.family == socket.AF_INET:
                                    # 排除回环地址
                                    if addr.address != "127.0.0.1":
                                        # 验证接口是否支持多播
                                        is_multicast_capable = self._check_interface_multicast_capability(interface_name)
                                        
                                        active_interfaces.append(
                                            {
                                                "name": interface_name,
                                                "ip": addr.address,
                                                "netmask": addr.netmask,
                                                "is_multicast_capable": is_multicast_capable,
                                            }
                                        )
        except Exception as e:
            self.logger.error(f"获取网络接口信息失败: {e}")

        return active_interfaces
    
    def _check_interface_multicast_capability(self, interface_name: str) -> bool:
        """
        检查网络接口是否支持多播
        
        Args:
            interface_name: 网络接口名称
            
        Returns:
            bool: 如果接口支持多播返回True，否则返回False
        """
        try:
            # 在Windows系统上，使用Get-NetAdapter检查接口是否支持多播
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ["powershell", "-Command", f"Get-NetAdapter -Name '{interface_name}' | Select-Object -ExpandProperty 'Multicast'"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().lower() == "true"
            
            # 在Linux系统上，检查/proc/net/dev中的接口标志
            elif platform.system() == "Linux":
                with open("/proc/net/dev", "r") as f:
                    for line in f:
                        if interface_name in line:
                            # 检查接口标志，MULTICAST标志通常表示支持多播
                            return True
            
            # 在macOS系统上，使用ifconfig检查
            elif platform.system() == "Darwin":
                import subprocess
                result = subprocess.run(
                    ["ifconfig", interface_name],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and "MULTICAST" in result.stdout:
                    return True
            
            # 默认情况下，假设接口支持多播
            return True
        except Exception as e:
            self.logger.debug(f"检查接口 {interface_name} 多播能力时出错: {e}")
            # 出错时默认返回True，避免阻止多播尝试
            return True
    
    def _validate_multicast_setup(self, multicast_group: str, multicast_port: int) -> Tuple[bool, str]:
        """
        验证多播设置是否有效
        
        Args:
            multicast_group: 多播组地址
            multicast_port: 多播端口
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        try:
            # 验证多播组地址
            try:
                socket.inet_aton(multicast_group)
                # 检查是否为有效的多播地址 (224.0.0.0 到 239.255.255.255)
                ip_parts = list(map(int, multicast_group.split('.')))
                if not (224 <= ip_parts[0] <= 239):
                    return False, f"无效的多播组地址: {multicast_group}，多播地址应在224.0.0.0-239.255.255.255范围内"
            except socket.error:
                return False, f"无效的IP地址格式: {multicast_group}"
            
            # 验证端口范围
            if not (1 <= multicast_port <= 65535):
                return False, f"无效的端口号: {multicast_port}，端口应在1-65535范围内"
            
            # 检查是否有支持多播的网络接口
            active_interfaces = self._get_active_interfaces()
            if not active_interfaces:
                return False, "没有找到活跃的网络接口"
            
            multicast_capable = [iface for iface in active_interfaces if iface.get("is_multicast_capable", True)]
            if not multicast_capable:
                self.logger.warning("没有找到明确支持多播的网络接口，仍将尝试多播操作")
            
            return True, ""
        except Exception as e:
            return False, f"验证多播设置时出错: {e}"


# 全局UDP客户端实例
_udp_client: Optional[UDPClient] = None
_udp_client_lock = None


def get_udp_client() -> UDPClient:
    """
    获取全局UDP客户端实例（单例模式）

    Returns:
        UDPClient: UDP客户端实例
    """
    global _udp_client, _udp_client_lock

    # 延迟初始化锁以避免在模块导入时的问题
    if _udp_client_lock is None:
        import threading

        _udp_client_lock = threading.Lock()

    if _udp_client is None:
        with _udp_client_lock:
            if _udp_client is None:
                _udp_client = UDPClient()
    return _udp_client




