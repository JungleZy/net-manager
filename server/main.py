#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务端启动脚本 - 同时启动UDP发现服务、TCP数据服务和API服务
"""

import threading
import sys
import os
import time
import atexit

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from src.network.udp.udp_server import udp_server
from src.network.tcp.tcp_server import TCPServer
from src.network.api.api_server import APIServer
from src.database import DatabaseManager
from src.core.logger import logger
from src.core.config import VERSION
from src.core.singleton_manager import get_server_singleton_manager
from src.snmp.unified_poller import stop_device_poller, stop_interface_poller

# 获取单例管理器实例
singleton_manager = get_server_singleton_manager()

# 全局变量，用于优雅退出
_shutdown_in_progress = False
tcp_server = None
api_server = None


def print_welcome_banner():
    """打印欢迎条幅和版本号"""
    print("=" * 50)
    print(
        r"""
 _    _  _____  _____ ______  _____ ___  ___    _   _  _____ ______ 
| |  | ||_   _|/  ___||  _  \|  _  ||  \/  |   | \ | ||_   _|| ___ \
| |  | |  | |  \ `--. | | | || | | || .  . |   |  \| |  | |  | |_/ /
| |/\| |  | |   `--. \| | | || | | || |\/| |   | . ` |  | |  |  __/ 
\  /\  / _| |_ /\__/ /| |/ / \ \_/ /| |  | | _ | |\  | _| |_ | |    
 \/  \/  \___/ \____/ |___/   \___/ \_|  |_/(_)\_| \_/ \___/ \_|    
    """
    )
    print("=" * 50)
    print(f"版本: {VERSION}")
    print("=" * 50)


def cleanup_on_exit():
    """程序退出时的清理函数"""
    global _shutdown_in_progress

    if _shutdown_in_progress:
        return  # 避免重复执行

    _shutdown_in_progress = True
    logger.info("开始执行退出清理...")

    # 停止服务器性能监控器
    try:
        from src.monitor import get_server_monitor

        server_monitor = get_server_monitor()
        if server_monitor.running:
            logger.info("停止服务器监控器...")
            server_monitor.stop()
    except Exception as e:
        logger.error(f"停止服务器监控器时出错: {e}")

    # 停止SNMP轮询器
    try:
        logger.info("停止SNMP轮询器...")
        stop_device_poller()
        stop_interface_poller()
    except Exception as e:
        logger.error(f"停止SNMP轮询器时出错: {e}")

    # 停止TCP服务器
    if "tcp_server" in globals() and tcp_server is not None:
        try:
            logger.info("停止TCP服务器...")
            tcp_server.running = False
        except Exception as e:
            logger.error(f"停止TCP服务器时出错: {e}")

    # 停止API服务器
    if "api_server" in globals() and api_server is not None:
        try:
            logger.info("停止API服务器...")
            api_server.stop()
        except Exception as e:
            logger.error(f"停止API服务器时出错: {e}")

    # 停止UDP服务器
    try:
        from src.network.udp.udp_server import stop_udp_server

        logger.info("停止UDP服务器...")
        stop_udp_server()
    except Exception as e:
        logger.error(f"停止UDP服务器时出错: {e}")

    # 释放单例锁
    try:
        singleton_manager.release_lock()
    except Exception as e:
        logger.error(f"释放单例锁时出错: {e}")

    logger.info("服务端已完成退出清理")


def signal_handler(sig, frame):
    """信号处理函数"""
    global _shutdown_in_progress

    if _shutdown_in_progress:
        return  # 避免重复处理

    logger.info(f"接收到信号 {sig}，正在关闭服务端...")
    cleanup_on_exit()
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
    global tcp_server, api_server

    # 尝试获取锁
    if not singleton_manager.acquire_lock():
        logger.error("服务端已在运行中，请勿重复启动")
        sys.exit(1)

    # 注册退出清理函数
    atexit.register(cleanup_on_exit)

    # 注册信号处理器
    import signal

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 打印欢迎条幅和版本号
    print_welcome_banner()

    logger.info("Net Manager 服务端启动...")

    try:
        # 1. 初始化数据库
        logger.info("数据库初始化...")
        db_manager = DatabaseManager()

        # 2. 创建TCP服务器实例
        tcp_server = TCPServer(db_manager)

        # 3. 创建API服务器实例
        api_server = APIServer(db_manager)

        # 4. 设置API服务器的TCP服务器引用
        api_server.set_tcp_server(tcp_server)

        # 5. 启动API服务器线程
        api_thread = threading.Thread(target=start_api_server, args=(api_server,))
        api_thread.daemon = True
        api_thread.start()

        # 等待API服务器完全启动
        time.sleep(0.5)

        # 6. 启动TCP服务线程
        tcp_thread = threading.Thread(target=start_tcp_server, args=(tcp_server,))
        tcp_thread.daemon = True
        tcp_thread.start()

        # 等待TCP服务器完全启动
        time.sleep(0.5)

        # 7. 启动UDP服务发现线程
        udp_thread = threading.Thread(target=udp_server)
        udp_thread.daemon = True
        udp_thread.start()

        # 等待UDP服务器完全启动
        time.sleep(0.5)

        # 8. 启动SNMP轮询器（统一管理）
        logger.info("启动SNMP轮询器...")
        from src.snmp.manager import SNMPManager

        # 将 db_manager 传递给 SNMPManager，共享连接池
        snmp_manager = SNMPManager(db_manager=db_manager)
        snmp_manager.start_pollers()

        # 9. 启动服务器性能监控器
        logger.info("启动服务器性能监控器...")
        from src.monitor import get_server_monitor

        server_monitor = get_server_monitor()  # 使用配置文件中的间隔
        server_monitor.start()

        logger.info("所有服务已启动完成")

        # 保持主线程运行，同时允许信号处理
        while True:
            time.sleep(1)
            # 检查线程是否还在运行
            if (
                not api_thread.is_alive()
                and not tcp_thread.is_alive()
                and not udp_thread.is_alive()
            ):
                logger.warning("服务线程已停止运行")
                break

    except KeyboardInterrupt:
        logger.info("服务端被用户中断")
    except Exception as e:
        logger.error(f"服务端运行出错: {e}", exc_info=True)
    finally:
        # cleanup_on_exit 会通过 atexit 自动调用
        pass


if __name__ == "__main__":
    main()
