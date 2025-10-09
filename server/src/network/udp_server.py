#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP服务端 - 用于Net Manager客户端发现服务端
"""

import socket
import json
import threading
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.core.config import UDP_HOST, UDP_PORT, TCP_PORT
from src.core.logger import logger

# 全局变量用于控制服务器运行状态
_udp_running = True

def stop_udp_server():
    """停止UDP服务器"""
    global _udp_running
    _udp_running = False

def udp_server():
    """UDP服务发现服务器"""
    global _udp_running
    # 创建UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 绑定端口
    server_address = (UDP_HOST, UDP_PORT)  # 使用配置的主机地址
    sock.bind(server_address)
    
    # 设置socket超时，以便能够响应停止信号
    sock.settimeout(1.0)
    
    logger.info(f"UDP服务端启动，监听端口 {UDP_PORT}")
    
    try:
        
        while _udp_running:
            try:
                # 接收数据
                data, address = sock.recvfrom(1024)  # 服务发现数据包应该很小
                try:
                    # 解析发现请求
                    request = json.loads(data.decode('utf-8'))
                    
                    # 如果是服务发现请求
                    if request.get('type') == 'discovery':
                        # 发送服务端信息作为响应
                        response = {
                            'type': 'discovery_response',
                            'tcp_port': int(TCP_PORT),  # 确保tcp_port是整数类型
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        response_data = json.dumps(response).encode('utf-8')
                        sock.sendto(response_data, address)
                        
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
        sock.close()
        logger.info("UDP服务端已停止")