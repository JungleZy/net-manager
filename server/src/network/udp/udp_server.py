#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP服务端 - 用于Net Manager客户端发现服务端
使用多播方式重构
"""

import socket
import json
import threading
import sys
import os
import struct
from datetime import datetime

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

# 使用相对导入修复路径问题
from ...core.config import UDP_HOST, UDP_PORT, TCP_PORT
from ...core.logger import logger

# 多播配置
MULTICAST_GROUP = "239.255.1.1"
MULTICAST_PORT = 37020
TTL = 32

# 全局变量用于控制服务器运行状态
_udp_running = True


def stop_udp_server():
    """停止UDP服务器"""
    global _udp_running
    _udp_running = False


def udp_server():
    """UDP服务发现服务器 - 使用多播方式"""
    global _udp_running

    # 初始化sockets
    listen_socket = None
    send_socket = None

    try:
        # 创建发送socket（用于发送响应）
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ttl_binary = struct.pack("b", TTL)
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_binary)
        send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        # 创建监听socket（用于接收查询）
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(("", MULTICAST_PORT))

        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        listen_socket.settimeout(1.0)

        # Windows: 忽略 ICMP Port Unreachable 导致的 WSAECONNRESET(10054)
        try:
            SIO_UDP_CONNRESET = 0x9800000C
            listen_socket.ioctl(SIO_UDP_CONNRESET, struct.pack('I', 0))
        except Exception:
            pass

        logger.info(f"UDP多播服务端启动，多播组 {MULTICAST_GROUP}:{MULTICAST_PORT}")

        while _udp_running:
            try:
                # 接收数据
                data, address = listen_socket.recvfrom(1024)
                try:
                    message = data.decode("utf-8")
                    logger.debug(f"收到查询: {message} 来自 {address}")

                    # 如果是服务发现请求
                    if data.startswith(b"DISCOVER"):
                        # 解析发现请求
                        parts = message.split("|")

                        if len(parts) >= 2:
                            requested_type = parts[1]

                            # 检查服务类型是否匹配（ANY表示所有类型）
                            if requested_type.upper() == "ANY":
                                # 发送服务端信息作为响应
                                response = {
                                    "type": "discovery_response",
                                    "tcp_port": int(TCP_PORT),  # 确保tcp_port是整数类型
                                    "timestamp": datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                }
                                response_data = json.dumps(response).encode("utf-8")

                                # 通过多播发送响应
                                send_socket.sendto(
                                    response_data, (MULTICAST_GROUP, MULTICAST_PORT)
                                )
                                logger.info(
                                    f"通过多播发送响应到 {MULTICAST_GROUP}:{MULTICAST_PORT}"
                                )

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    logger.error(f"处理发现请求时出错: {e}")
            except socket.timeout:
                # 超时继续循环，检查_udp_running状态
                continue
            except Exception as e:
                if _udp_running:
                    logger.error(f"UDP服务发现运行出错: {e}")
                break

    except KeyboardInterrupt:
        logger.info("UDP服务发现已停止")
    except Exception as e:
        logger.error(f"服务发现运行出错: {e}")
    finally:
        if listen_socket:
            listen_socket.close()
        if send_socket:
            send_socket.close()
        logger.info("UDP服务端已停止")
