import time
import json
import signal
import sys
import os
import hashlib
import threading
import json
from typing import Optional

def get_application_path():
    """获取应用程序路径，兼容开发环境和打包环境"""
    is_frozen = hasattr(sys, 'frozen') and sys.frozen
    is_nuitka = '__compiled__' in globals()
    
    if is_frozen or is_nuitka:
        # 打包后的可执行文件路径
        application_path = os.path.dirname(sys.executable)
    elif '__compiled__' in globals():
        # Nuitka打包环境
        application_path = os.path.dirname(os.path.abspath(__file__))
    else:
        # 开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))

    
    return application_path

# 添加项目根目录到Python路径
parent_dir = get_application_path()
sys.path.insert(0, parent_dir)

from src.config import COLLECT_INTERVAL
from src.system_collector import SystemCollector
from src.tcp_client import TCPClient
from src.logger import logger
from src.platform_utils import setup_signal_handlers
from src.autostart import enable_autostart, disable_autostart, is_autostart_enabled, create_daemon_script
from src.singleton_manager import get_client_singleton_manager
from src.state_manager import get_state_manager

# 全局变量用于信号处理
tcp_client: Optional[TCPClient] = None
last_system_info_hash: Optional[str] = None  # 用于存储上一次系统信息的哈希值
shutdown_event = threading.Event()  # 用于优雅关闭程序

# 获取单例管理器实例
singleton_manager = get_client_singleton_manager()

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭程序...")
    shutdown_event.set()  # 设置关闭事件
    if tcp_client:
        tcp_client.disconnect()
    singleton_manager.release_lock()  # 释放锁
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
    
    # 添加调试信息
    print("DEBUG: 程序启动")
    
    # 尝试获取锁
    if not singleton_manager.acquire_lock():
        print("DEBUG: 客户端已在运行中，请勿重复启动")
        logger.error("客户端已在运行中，请勿重复启动")
        # 添加延迟以便观察输出
        time.sleep(5)
        sys.exit(1)
    
    # 获取状态管理器实例
    state_manager = get_state_manager()
    client_id = state_manager.get_client_id()
    logger.info(f"客户端唯一标识符: {client_id}")
    
    # 只在打包环境下执行开机自启动和守护进程功能
    # 检查是否处于打包环境（Nuitka或PyInstaller）
    is_frozen = hasattr(sys, 'frozen') and sys.frozen
    is_nuitka = '__compiled__' in globals()
    
    if is_frozen or is_nuitka:
        print("DEBUG: 检测到打包环境，执行开机自启动和守护进程功能")
        logger.info("检测到打包环境，执行开机自启动和守护进程功能")
        
        # 默认启动时自动启用开机自启动和创建守护进程
        if is_autostart_enabled():
            print("DEBUG: 开机自启动已启用")
            logger.info("开机自启动已启用")
        else:
            if enable_autostart():
                print("DEBUG: 已自动启用开机自启动")
                logger.info("已自动启用开机自启动")
            else:
                print("DEBUG: 自动启用开机自启动失败")
                logger.warning("自动启用开机自启动失败")
            
        if create_daemon_script():
            print("DEBUG: 已自动创建守护进程脚本")
            logger.info("已自动创建守护进程脚本")
        else:
            print("DEBUG: 自动创建守护进程脚本失败")
            logger.warning("自动创建守护进程脚本失败")
    else:
        print("DEBUG: 检测到开发环境，跳过开机自启动和守护进程功能")
        logger.info("检测到开发环境，跳过开机自启动和守护进程功能")
    
    # 注册跨平台信号处理器
    setup_signal_handlers(signal_handler)
    
    logger.info("Net Manager 启动...")
    print("DEBUG: Net Manager 启动...")
    
    # 初始化各组件
    collector = SystemCollector()
    tcp_client = TCPClient()
    
    # 添加延迟以便观察
    print("DEBUG: 程序初始化完成，等待5秒...")
    time.sleep(5)
    
    # 尝试通过UDP发现并连接到服务端
    connection_retry_count = 0
    
    while not shutdown_event.is_set():
        print(f"DEBUG: 尝试发现服务端，第{connection_retry_count+1}次")
        if tcp_client.discover_server():
            print("DEBUG: 发现服务端，尝试连接...")
            if tcp_client.connect_to_server():
                logger.info("已通过TCP连接到服务端")
                print("DEBUG: 已通过TCP连接到服务端")
                connection_retry_count = 0  # 重置重试计数
                break
            else:
                connection_retry_count += 1
                logger.warning(f"TCP连接失败，{connection_retry_count}次重试后重试...")
                print(f"DEBUG: TCP连接失败，{connection_retry_count}次重试后重试...")

        else:
            connection_retry_count += 1
            logger.warning(f"无法通过UDP发现服务端，{connection_retry_count}次重试后重试...")
            print(f"DEBUG: 无法通过UDP发现服务端，{connection_retry_count}次重试后重试...")
        
        # 添加延迟
        if shutdown_event.wait(5):
            break
    
    # 如果成功连接到服务端，进入主循环
    if not shutdown_event.is_set():
        print("DEBUG: 进入主循环")
        try:
            # 主循环
            while not shutdown_event.is_set():
                logger.debug("开始收集系统信息...")
                print("DEBUG: 开始收集系统信息...")
                
                # 收集系统信息（包括进程信息）
                try:
                    system_info = collector.collect_system_info()
                    print("DEBUG: 系统信息收集完成")
                except Exception as e:
                    logger.error(f"收集系统信息时出错: {e}")
                    print(f"DEBUG: 收集系统信息时出错: {e}")
                    if shutdown_event.wait(COLLECT_INTERVAL):
                        break
                    continue
                
                # 计算当前系统信息的哈希值
                current_hash = calculate_system_info_hash(system_info)
                print(f"DEBUG: 当前系统信息哈希值: {current_hash}")
                
                # 比较当前数据与上一次数据是否相同
                if current_hash != last_system_info_hash:
                    print("DEBUG: 系统信息发生变化，准备发送到服务端...")
                    logger.info("系统信息发生变化，准备发送到服务端...")
                    
                    # 通过TCP发送到服务端
                    send_success = False
                    if tcp_client and tcp_client.is_connected():
                        print("DEBUG: 尝试发送系统信息到服务端...")
                        success_tcp = tcp_client.send_system_info(system_info)
                        if success_tcp:
                            # 更新上一次的哈希值
                            last_system_info_hash = current_hash
                            logger.info("系统信息已发送到服务端")
                            print("DEBUG: 系统信息已发送到服务端")
                            send_success = True
                        else:
                            logger.warning("系统信息TCP发送失败")
                            print("DEBUG: 系统信息TCP发送失败")
                    else:
                        logger.warning("TCP连接已断开")
                        print("DEBUG: TCP连接已断开")
                    
                    # 如果发送失败，尝试重新连接
                    if not send_success:
                        print("DEBUG: 尝试重新连接到服务端...")
                        logger.info("尝试重新连接到服务端...")
                        if tcp_client.discover_server() and tcp_client.connect_to_server():
                            logger.info("TCP连接已恢复")
                            print("DEBUG: TCP连接已恢复")
                            if tcp_client.send_system_info(system_info):
                                last_system_info_hash = current_hash
                                logger.info("系统信息已重新发送到服务端")
                                print("DEBUG: 系统信息已重新发送到服务端")
                            else:
                                logger.warning("重新发送数据失败")
                                print("DEBUG: 重新发送数据失败")
                        else:
                            logger.warning("重新连接失败")
                            print("DEBUG: 重新连接失败")
                            
                else:
                    logger.debug("系统信息未发生变化，跳过发送")
                    print("DEBUG: 系统信息未发生变化，跳过发送")
                
                # 添加延迟
                print("DEBUG: 等待下一次收集...")
                if shutdown_event.wait(COLLECT_INTERVAL):
                    break
                    
        except Exception as e:
            logger.error(f"主循环中发生错误: {e}")
            print(f"DEBUG: 主循环中发生错误: {e}")
    
    print("DEBUG: 程序即将退出")
    logger.info("程序正常退出")

if __name__ == "__main__":
    main()