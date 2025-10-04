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

from src.config import UDP_HOST, UDP_PORT, TCP_PORT
from src.logger import logger

def udp_server():
    """UDP服务发现服务器"""
    # 创建UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 绑定端口
    server_address = (UDP_HOST, UDP_PORT)  # 使用配置的主机地址
    sock.bind(server_address)
    
    logger.info(f"UDP服务发现启动，监听地址 {UDP_HOST}:{UDP_PORT}...")
    
    try:
        
        while True:
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
                        'tcp_port': TCP_PORT,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    response_data = json.dumps(response).encode('utf-8')
                    sock.sendto(response_data, address)
                    logger.info(f"向 {address} 发送服务发现响应，TCP端口: {TCP_PORT}")
                    
            except json.JSONDecodeError:
                # 不是JSON数据，忽略
                logger.warning("收到非JSON格式的服务发现请求")
            except Exception as e:
                logger.error(f"处理发现请求时出错: {e}")
                
    except KeyboardInterrupt:
        logger.info("UDP服务发现已停止")
    except Exception as e:
        logger.error(f"服务发现运行出错: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    udp_server()