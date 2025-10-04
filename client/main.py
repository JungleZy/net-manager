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
from src.udp_sender import UDPSender
from src.logger import logger

# 全局变量用于信号处理
udp_sender = None

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭程序...")
    if udp_sender:
        udp_sender.close()
    logger.info("程序已退出")
    sys.exit(0)

def main():
    """主程序入口"""
    global udp_sender
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Net Manager 启动...")
    
    # 初始化各组件
    collector = SystemCollector()
    db_manager = DatabaseManager()
    udp_sender = UDPSender()
    
    try:
        while True:
            logger.info("开始收集系统信息...")
            
            # 收集系统信息
            system_info = collector.collect_system_info()
            
            # 保存到数据库
            db_manager.save_system_info(system_info)
            logger.info("系统信息已保存到数据库")
            
            # 通过UDP发送
            success = udp_sender.send_system_info(system_info)
            if not success:
                logger.warning("系统信息发送失败")
            
            # 等待下次收集
            logger.info(f"等待 {COLLECT_INTERVAL} 秒后进行下次收集...")
            time.sleep(COLLECT_INTERVAL)
            
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        if udp_sender:
            udp_sender.close()
        raise

if __name__ == "__main__":
    main()