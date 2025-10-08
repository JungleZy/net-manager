#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Ctrl+C中断功能的改进脚本
"""

import sys
import os
import signal
import time
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))

from src.core.app_controller import AppController


def main():
    """测试主函数"""
    print("测试Ctrl+C中断功能")
    print("按Ctrl+C应该能够正常停止程序")
    
    # 创建应用控制器实例
    app_controller = AppController()
    
    # 注册信号处理器
    def signal_handler(signum, frame):
        print(f"收到信号 {signum}，准备退出...")
        app_controller.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动应用
        print("启动应用控制器...")
        app_controller.start()
        
        # 等待应用结束
        print("等待应用控制器结束...")
        app_controller.wait()
        
        print("应用控制器正常退出")
        
    except KeyboardInterrupt:
        print("用户中断程序")
        app_controller.stop()
    except Exception as e:
        print(f"程序运行出错: {e}")
        app_controller.stop()


if __name__ == "__main__":
    main()