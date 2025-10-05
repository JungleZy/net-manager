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
from src.config import VERSION

# 单一实例锁文件路径
LOCK_FILE_PATH = os.path.join(parent_dir, "server.lock")

def acquire_lock():
    """获取文件锁，确保只有一个实例运行"""
    if os.path.exists(LOCK_FILE_PATH):
        # 检查锁文件是否有效（进程是否仍在运行）
        try:
            with open(LOCK_FILE_PATH, "r") as f:
                pid = int(f.read().strip())
            # 检查进程是否存在
            if os.name == 'nt':  # Windows
                import subprocess
                result = subprocess.run(["tasklist", "/fi", f"PID eq {pid}"], 
                                      capture_output=True, text=True)
                if str(pid) in result.stdout:
                    logger.error("服务端已在运行中，请勿重复启动")
                    return False
            else:  # Unix-like systems
                import signal as sys_signal
                try:
                    os.kill(pid, 0)  # 检查进程是否存在
                    logger.error("服务端已在运行中，请勿重复启动")
                    return False
                except OSError:
                    pass  # 进程不存在，可以继续
        except (ValueError, IOError):
            pass  # 锁文件损坏或无法读取，继续执行
    
    # 创建新的锁文件
    try:
        with open(LOCK_FILE_PATH, "w") as f:
            f.write(str(os.getpid()))
        return True
    except IOError:
        logger.error("无法创建锁文件，可能没有写入权限")
        return False

def release_lock():
    """释放文件锁"""
    try:
        if os.path.exists(LOCK_FILE_PATH):
            os.remove(LOCK_FILE_PATH)
    except OSError:
        pass  # 忽略删除失败

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
    release_lock()  # 释放锁
    logger.info("服务端已退出")
    sys.exit(0)

def main():
    """启动服务端"""
    # 尝试获取锁
    if not acquire_lock():
        sys.exit(1)
    
    # 注册信号处理器
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 打印欢迎条幅和版本号
    print_welcome_banner()
    
    logger.info("Net Manager 服务端启动...")
    
    try:
        # 创建并启动UDP服务发现线程
        udp_thread = threading.Thread(target=udp_server)
        udp_thread.daemon = True
        udp_thread.start()
        
        # 创建并启动TCP服务
        tcp_server = TCPServer()
        tcp_server.start()
    except KeyboardInterrupt:
        logger.info("服务端被用户中断")
    except Exception as e:
        logger.error(f"服务端运行出错: {e}")
    finally:
        # 正常退出时释放锁
        release_lock()
        logger.info("服务端正常退出")

if __name__ == "__main__":
    main()