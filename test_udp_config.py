#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试UDP配置 - 验证在未设置UDP_HOST的情况下程序的行为
"""

import os
import sys
import time
import subprocess

def test_udp_config():
    """测试UDP配置功能"""
    print("开始测试UDP配置...")
    
    # 运行主程序并捕获输出
    print("测试场景1: 未设置UDP_HOST环境变量")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # 读取输出行，直到找到我们需要的信息或超时
    start_time = time.time()
    timeout = 5  # 增加超时时间到5秒
    output_lines = []
    warning_found = False
    error_found = False
    
    while time.time() - start_time < timeout and process.poll() is None:
        line = process.stdout.readline()
        if line:
            output_lines.append(line)
            if "UDP发送器初始化完成，但目标地址未设置" in line:
                warning_found = True
                print("✓ 验证通过: 检测到UDP_HOST未设置的警告信息")
            if "无法发送数据：UDP_HOST未设置" in line:
                error_found = True
                print("✓ 验证通过: 检测到无法发送数据的错误信息")
            # 如果两个信息都找到了，可以提前结束
            if warning_found and error_found:
                break
    
    # 如果还没找到预期信息，输出已收集的所有行
    if not warning_found or not error_found:
        print("\n收集到的输出:")
        for line in output_lines:
            print(line.strip())
        
    if not warning_found:
        print("✗ 验证失败: 未检测到UDP_HOST未设置的警告信息")
    if not error_found:
        print("✗ 验证失败: 未检测到无法发送数据的错误信息")
    
    # 终止进程
    try:
        process.terminate()
        process.wait(timeout=2)
    except:
        try:
            process.kill()
        except:
            pass
    
    print("\n测试完成，请参考README.md中的说明设置UDP_HOST环境变量或修改config.py文件")

if __name__ == "__main__":
    test_udp_config()