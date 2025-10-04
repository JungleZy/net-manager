#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Net Manager 启动脚本
"""

import sys
import os
import subprocess
import signal
import time

def main():
    """启动Net Manager"""
    print("正在启动Net Manager...")
    
    # 启动主程序
    try:
        # 使用子进程启动主程序
        process = subprocess.Popen([sys.executable, "main.py"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
        
        print(f"Net Manager已启动，进程ID: {process.pid}")
        print("按Ctrl+C停止程序")
        
        # 等待进程结束或接收中断信号
        try:
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"程序出错: {stderr}")
            else:
                print("程序正常退出")
        except KeyboardInterrupt:
            print("\n正在停止Net Manager...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            print("Net Manager已停止")
            
    except FileNotFoundError:
        print("错误: 找不到main.py文件，请确保在项目根目录运行此脚本")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()