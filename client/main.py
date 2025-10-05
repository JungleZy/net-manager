import time
import json
import signal
import sys
import os
import hashlib
import threading
from typing import Optional

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from src.config import COLLECT_INTERVAL
from src.system_collector import SystemCollector
from src.tcp_client import TCPClient
from src.logger import logger
from src.platform_utils import setup_signal_handlers

# 全局变量用于信号处理
tcp_client: Optional[TCPClient] = None
last_system_info_hash: Optional[str] = None  # 用于存储上一次系统信息的哈希值
shutdown_event = threading.Event()  # 用于优雅关闭程序

# 单一实例锁文件路径
LOCK_FILE_PATH = os.path.join(parent_dir, "client.lock")

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
                    logger.error("客户端已在运行中，请勿重复启动")
                    return False
            else:  # Unix-like systems
                import signal as sys_signal
                try:
                    os.kill(pid, 0)  # 检查进程是否存在
                    logger.error("客户端已在运行中，请勿重复启动")
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

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭程序...")
    shutdown_event.set()  # 设置关闭事件
    if tcp_client:
        tcp_client.disconnect()
    release_lock()  # 释放锁
    logger.info("程序已退出")
    sys.exit(0)

def calculate_system_info_hash(system_info):
    """计算系统信息的哈希值，用于比较两次数据是否相同"""
    # 将SystemInfo对象转换为字典，排除时间戳字段
    info_dict = {
        'hostname': system_info.hostname,
        'ip_address': system_info.ip_address,
        'mac_address': system_info.mac_address,
        'services': system_info.services,  # 这已经是JSON字符串
        'processes': system_info.processes  # 这已经是JSON字符串
    }
    
    # 将字典转换为JSON字符串并计算哈希值
    info_str = json.dumps(info_dict, sort_keys=True)
    return hashlib.md5(info_str.encode('utf-8')).hexdigest()

def main():
    """主程序入口"""
    global tcp_client, last_system_info_hash
    
    # 尝试获取锁
    if not acquire_lock():
        sys.exit(1)
    
    # 注册跨平台信号处理器
    setup_signal_handlers(signal_handler)
    
    logger.info("Net Manager 启动...")
    
    # 初始化各组件
    collector = SystemCollector()
    tcp_client = TCPClient()
    
    # 尝试通过UDP发现并连接到服务端
    connection_retry_count = 0
    
    while not shutdown_event.is_set():
        if tcp_client.discover_server():
            if tcp_client.connect_to_server():
                logger.info("已通过TCP连接到服务端")
                connection_retry_count = 0  # 重置重试计数
                break
            else:
                connection_retry_count += 1
                logger.warning(f"TCP连接失败，{connection_retry_count}次重试后重试...")

        else:
            connection_retry_count += 1
            logger.warning(f"无法通过UDP发现服务端，{connection_retry_count}次重试后重试...")
    
    # 如果成功连接到服务端，进入主循环
    try:
        # 主循环
        while not shutdown_event.is_set():
            logger.debug("开始收集系统信息...")
            
            # 收集系统信息（包括进程信息）
            try:
                system_info = collector.collect_system_info()
            except Exception as e:
                logger.error(f"收集系统信息时出错: {e}")
                if shutdown_event.wait(COLLECT_INTERVAL):
                    break
                continue
            
            # 计算当前系统信息的哈希值
            current_hash = calculate_system_info_hash(system_info)
            
            # 比较当前数据与上一次数据是否相同
            if current_hash != last_system_info_hash:
                logger.info("系统信息发生变化，准备发送到服务端...")
                
                # 通过TCP发送到服务端
                send_success = False
                if tcp_client and tcp_client.is_connected():
                    success_tcp = tcp_client.send_system_info(system_info)
                    if success_tcp:
                        # 更新上一次的哈希值
                        last_system_info_hash = current_hash
                        logger.info("系统信息已发送到服务端")
                        send_success = True
                    else:
                        logger.warning("系统信息TCP发送失败")
                else:
                    logger.warning("TCP连接已断开")
                
                # 如果发送失败，尝试重新连接
                if not send_success:
                    logger.info("尝试重新连接到服务端...")
                    reconnect_success = False
                    for i in range(3):  # 最多重试3次
                        if tcp_client.discover_server() and tcp_client.connect_to_server():
                            logger.info("TCP连接已恢复")
                            # 重新发送数据
                            if tcp_client.send_system_info(system_info):
                                last_system_info_hash = current_hash
                                logger.info("系统信息已重新发送到服务端")
                                reconnect_success = True
                                break
                            else:
                                logger.warning(f"重新发送数据失败，第{i+1}次重试")
                        else:
                            logger.warning(f"重新连接失败，第{i+1}次重试")
                        # 等待一段时间再重试
                        if shutdown_event.wait(2):
                            break
                    
                    if not reconnect_success:
                        logger.error("重新连接和发送数据均失败")
            else:
                logger.debug("系统信息未发生变化，跳过发送")
            
            # 等待下次收集，支持优雅关闭
            logger.debug(f"等待 {COLLECT_INTERVAL} 秒后进行下次收集...")
            if shutdown_event.wait(COLLECT_INTERVAL):
                break
                
        # 正常退出时释放锁
        release_lock()
        logger.info("程序正常退出")
                
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        if tcp_client:
            tcp_client.disconnect()
        release_lock()
        raise
            
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        if tcp_client:
            tcp_client.disconnect()
        release_lock()
        raise

if __name__ == "__main__":
    main()