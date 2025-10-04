import time
import json
import signal
import sys
import os

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from src.config import COLLECT_INTERVAL
from src.system_collector import SystemCollector
from src.models import DatabaseManager
from src.tcp_client import TCPClient
from src.logger import logger
from src.platform_utils import setup_signal_handlers

# 全局变量用于信号处理
tcp_client = None

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭程序...")
    if tcp_client:
        tcp_client.disconnect()
    logger.info("程序已退出")
    sys.exit(0)

def main():

    """主程序入口"""
    global tcp_client
    
    # 注册跨平台信号处理器
    if not setup_signal_handlers(signal_handler):
        logger.error("设置信号处理器失败")
        return
    
    logger.info("Net Manager 启动...")
    
    # 初始化各组件
    collector = SystemCollector()
    db_manager = DatabaseManager()
    tcp_client = TCPClient()
    
    # 尝试通过UDP发现并连接到服务端
    if tcp_client.discover_server() and tcp_client.connect_to_server():
        logger.info("已通过TCP连接到服务端")
    else:
        logger.error("无法通过TCP连接到服务端，程序将退出")
        return
    
    try:
        while True:
            logger.info("开始收集系统信息...")
            
            # 收集系统信息（包括进程信息）
            system_info = collector.collect_system_info()
            
            # 保存到数据库
            db_manager.save_system_info(system_info)
            logger.info("系统信息已保存到数据库")
            
            # 通过TCP发送
            if tcp_client and tcp_client.is_connected():
                success_tcp = tcp_client.send_system_info(system_info)
                if not success_tcp:
                    logger.warning("系统信息TCP发送失败")
                    # 尝试重新连接
                    if tcp_client.discover_server() and tcp_client.connect_to_server():
                        logger.info("TCP连接已恢复")
                        # 重新发送数据
                        tcp_client.send_system_info(system_info)
            else:
                # 尝试重新连接
                if tcp_client.discover_server() and tcp_client.connect_to_server():
                    logger.info("TCP连接已恢复")
            
            # 等待下次收集
            logger.info(f"等待 {COLLECT_INTERVAL} 秒后进行下次收集...")
            time.sleep(COLLECT_INTERVAL)
            
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        if tcp_client:
            tcp_client.disconnect()
        raise

if __name__ == "__main__":
    main()