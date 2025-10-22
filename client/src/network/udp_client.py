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

        discovered_services = {}
        discovery_id = int(time.time() * 1000) % 1000000  # 生成一个发现ID

        listen_socket = None
        send_socket = None

        try:
            # 创建发送socket
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ttl = struct.pack("b", 32)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

            # 创建监听socket
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind(("", MULTICAST_PORT))

            group = socket.inet_aton(MULTICAST_GROUP)
            mreq = struct.pack("4sL", group, socket.INADDR_ANY)
            listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

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

        # 获取活跃的网络接口
        active_interfaces = self._get_active_interfaces()

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

    @lru_cache(maxsize=1)
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
                                        active_interfaces.append(
                                            {
                                                "name": interface_name,
                                                "ip": addr.address,
                                                "netmask": addr.netmask,
                                            }
                                        )
        except Exception as e:
            self.logger.error(f"获取网络接口信息失败: {e}")

        return active_interfaces


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
