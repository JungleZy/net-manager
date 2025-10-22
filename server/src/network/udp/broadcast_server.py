#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP广播服务端 - 用于Net Manager客户端通过广播方式发现服务端
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


# 全局变量用于控制服务器运行状态
_broadcast_running = True


def stop_broadcast_server():
    """停止UDP广播服务器"""
    global _broadcast_running
    _broadcast_running = False


def broadcast_server():
    """UDP广播服务发现服务器"""
    global _broadcast_running

    sock = None
    try:
        # 创建UDP socket监听广播端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定到配置的地址和端口
        bind_address = (UDP_HOST, UDP_PORT)
        sock.bind(bind_address)
        sock.settimeout(1.0)

        logger.info(f"UDP广播服务端启动，监听 {UDP_HOST}:{UDP_PORT}")

        while _broadcast_running:
            try:
                # 接收数据
                data, address = sock.recvfrom(1024)
                try:
                    message = json.loads(data.decode("utf-8"))
                    logger.debug(f"收到广播查询: {message} 来自 {address}")

                    # 如果是服务发现请求
                    if message.get("type") == "discovery":
                        # 发送服务端信息作为响应（直接单播回客户端）
                        response = {
                            "type": "discovery_response",
                            "tcp_port": int(TCP_PORT),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        response_data = json.dumps(response).encode("utf-8")

                        # 直接发送给客户端地址
                        sock.sendto(response_data, address)
                        logger.info(f"通过广播发送响应到 {address}")

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    logger.error(f"处理广播发现请求时出错: {e}")
            except socket.timeout:
                continue
            except Exception as e:
                if _broadcast_running:
                    logger.error(f"UDP广播服务发现运行出错: {e}")
                break

    except Exception as e:
        logger.error(f"广播服务发现运行出错: {e}")
    finally:
        if sock:
            sock.close()
        logger.info("UDP广播服务端已停止")
