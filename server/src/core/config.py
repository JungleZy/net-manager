#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器端配置文件
"""

import os
from pathlib import Path

# 版本信息
VERSION = "1.0.0"

# 服务端配置
UDP_HOST = "0.0.0.0"  # 本地回环地址（用于开发测试，避免权限问题）
UDP_PORT = 12345  # UDP监听端口（用于服务发现）
TCP_PORT = 12346  # TCP监听端口（用于数据传输）
API_HOST = "0.0.0.0"  # API监听主机（默认本地回环）
API_PORT = 12344  # API监听端口（用于RESTful API服务）

# 日志配置
LOG_LEVEL = "INFO"
# 使用pathlib处理跨平台路径
# TimedRotatingFileHandler会自动添加日期后缀，所以基础文件名不需要.log扩展名
LOG_FILE = Path(__file__).parent.parent.parent / "logs" / "net_manager_server"

# 服务器性能监控配置
SERVER_MONITOR_INTERVAL = 10  # 服务器性能数据采集间隔（秒）
