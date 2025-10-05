#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务端启动脚本 - 同时启动UDP发现服务、TCP数据服务和API服务
"""

import threading
import sys
import os

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from src.udp_server import udp_server
from src.tcp_server import TCPServer
from src.api_server import APIServer
from src.logger import logger
from src.config import VERSION
from src.singleton_manager import get_server_singleton_manager

# 获取单例管理器实例
singleton_manager = get_server_singleton_manager()

def print_welcome_banner():
    """打印欢迎条幅和版本号"""
    print("=" * 50)
    print(r"""
 _    _  _____  _____ ______  _____ ___  ___    _   _  _____ ______ 
| |  | ||_   _|/  ___||  _  \|  _  ||  \/  |   | \ | ||_   _|| ___ \
| |  | |  | |  \ `--. | | | || | | || .  . |   |  \| |  | |  | |_/ /
| |/\| |  | |   `--. \| | | || | | || |\/| |   | . ` |  | |  |  __/ 
\  /\  / _| |_ /\__/ /| |/ / \ \_/ /| |  | | _ | |\  | _| |_ | |    
 \/  \/  \___/ \____/ |___/   \___/ \_|  |_/(_)\_| \_/ \___/ \_|    
    """)
    print("=" * 50)

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭服务端...")
    singleton_manager.release_lock()  # 释放锁
    logger.info("服务端已退出")
    sys.exit(0)

def start_tcp_server(tcp_server_instance):
    """启动TCP服务器"""
    try:
        tcp_server_instance.start()
    except Exception as e:
        logger.error(f"TCP服务端运行出错: {e}")

def start_api_server(api_server_instance):
    """启动API服务器"""
    try:
        api_server_instance.start()
    except Exception as e:
        logger.error(f"API服务端运行出错: {e}")

def main():
    """启动服务端"""
    # 尝试获取锁
    if not singleton_manager.acquire_lock():
        logger.error("服务端已在运行中，请勿重复启动")
        sys.exit(1)
    
    # 注册信号处理器
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 打印欢迎条幅和版本号
    print_welcome_banner()
    
    logger.info("Net Manager 服务端启动...")
    
    try:
        # 1. 初始化数据库（在API服务器和TCP服务器的构造函数中完成）
        logger.info("数据库初始化...")
        
        # 2. 创建API服务器实例（会初始化数据库）
        api_server = APIServer()
        
        # 3. 创建TCP服务器实例（会初始化数据库）
        tcp_server = TCPServer()
        
        # 4. 启动API服务器线程
        api_thread = threading.Thread(target=start_api_server, args=(api_server,))
        api_thread.daemon = True
        api_thread.start()
        
        # 等待API服务器完全启动
        import time
        time.sleep(0.5)
        
        # 5. 启动TCP服务线程
        tcp_thread = threading.Thread(target=start_tcp_server, args=(tcp_server,))
        tcp_thread.daemon = True
        tcp_thread.start()
        
        # 等待TCP服务器完全启动
        time.sleep(0.5)
        
        # 6. 启动UDP服务发现线程
        udp_thread = threading.Thread(target=udp_server)
        udp_thread.daemon = True
        udp_thread.start()
        
        # 保持主线程运行，同时允许信号处理
        while True:
            time.sleep(1)
            # 检查线程是否还在运行
            if not api_thread.is_alive() and not tcp_thread.is_alive():
                logger.warning("服务线程已停止运行")
                break
                
    except KeyboardInterrupt:
        logger.info("服务端被用户中断")
    except Exception as e:
        logger.error(f"服务端运行出错: {e}")
    finally:
        # 正常退出时释放锁
        singleton_manager.release_lock()
        logger.info("服务端正常退出")

if __name__ == "__main__":
    main()