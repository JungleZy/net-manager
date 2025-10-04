#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UDP服务端 - 监听12306端口接收Net Manager发送的数据
"""

import socket
import json
import sys
import os
from datetime import datetime

import sys
import os

# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config import UDP_PORT

def udp_server():
    """UDP服务端，监听指定端口接收数据"""
    # 创建UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 绑定端口
    server_address = ('0.0.0.0', UDP_PORT)  # 监听所有网络接口
    print(f"UDP服务端启动，监听端口 {UDP_PORT}...")
    print(f"按Ctrl+C停止服务")
    
    try:
        sock.bind(server_address)
        
        while True:
            # 接收数据 (增大缓冲区以处理大数据包)
            data, address = sock.recvfrom(65536)  # 64KB缓冲区
            receive_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{receive_time}] 收到来自 {address} 的数据:")
            
            try:
                # 解析JSON数据
                info = json.loads(data.decode('utf-8'))
                print(f"  主机名: {info.get('hostname', 'N/A')}")
                print(f"  IP地址: {info.get('ip_address', 'N/A')}")
                print(f"  MAC地址: {info.get('mac_address', 'N/A')}")
                print(f"  时间戳: {info.get('timestamp', 'N/A')}")
                
                # 解析服务信息
                services_data = info.get('services', '[]')
                try:
                    services = json.loads(services_data)
                    print(f"  服务数量: {len(services)}")
                    
                    # 显示前5个服务作为示例
                    print("  服务列表 (前5个):")
                    for i, service in enumerate(services[:5]):
                        print(f"    {i+1}. {service.get('protocol', 'N/A')} - {service.get('local_address', 'N/A')} - {service.get('status', 'N/A')}")
                    if len(services) > 5:
                        print(f"    ... 还有 {len(services) - 5} 个服务")
                except json.JSONDecodeError:
                    print(f"  服务信息无法解析: {services_data}")
                
                print("-" * 50)
                
            except json.JSONDecodeError:
                print(f"  无法解析的JSON数据: {data.decode('utf-8')}")
            except Exception as e:
                print(f"  处理数据时出错: {e}")
                
    except KeyboardInterrupt:
        print("\nUDP服务端已停止")
    except Exception as e:
        print(f"服务端运行出错: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    udp_server()