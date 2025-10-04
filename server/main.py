#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务端启动脚本 - 同时启动UDP发现服务和TCP数据服务
"""

import threading
import sys
import os

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from src.udp_server import udp_server
from src.tcp_server import TCPServer
from src.logger import logger

def main():
    """启动服务端"""
    logger.info("Net Manager 服务端启动...")
    
    # 创建并启动UDP服务发现线程
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.daemon = True
    udp_thread.start()
    logger.info("UDP服务发现已启动")
    
    # 创建并启动TCP服务
    tcp_server = TCPServer()
    logger.info("TCP服务已启动")
    tcp_server.start()

if __name__ == "__main__":
    main()