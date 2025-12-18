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
SERVER_MONITOR_FD_BACKOFF_SEC = int(os.getenv("SERVER_MONITOR_FD_BACKOFF_SEC", 60))

# TCP 接收控制
TCP_MAX_MESSAGE_SIZE = 16 * 1024 * 1024  # 单消息最大长度（字节）
TCP_RECV_TIMEOUT = 5  # 接收超时（秒）

# SNMP 轮询队列控制
SNMP_QUEUE_MAXSIZE = 200  # 队列最大长度
SNMP_QUEUE_STRATEGY = "drop_new"  # 可选：drop_new / drop_oldest / backpressure
SNMP_QUEUE_PUT_TIMEOUT = 1  # backpressure模式下入队等待超时（秒）

# 阶段3：并发与配置（默认值可通过环境变量覆盖）
try:
    import multiprocessing as _mp

    _cpu = max(1, _mp.cpu_count())
    _default_workers = max(100, min(200, _cpu * 10))
except Exception:
    _default_workers = 100
TCP_THREADPOOL_WORKERS = int(os.getenv("TCP_THREADPOOL_WORKERS", _default_workers))
TCP_MAX_PENDING_TASKS = 500

POLLERS_DEVICE_MIN_WORKERS = 5
POLLERS_DEVICE_MAX_WORKERS = 20
POLLERS_DEVICE_INTERVAL = 10

POLLERS_INTERFACE_MIN_WORKERS = 5
POLLERS_INTERFACE_MAX_WORKERS = 30
POLLERS_INTERFACE_INTERVAL = 15

# 轻量指标端点
METRICS_ENABLED = True
METRICS_ROUTE = "/api/metrics"

# 内存守护
MEMORY_GUARD_ENABLED = True
MEMORY_GUARD_CHECK_INTERVAL = 10
MEMORY_GUARD_RSS_HIGH_MB = 2000
MEMORY_GUARD_RSS_LOW_MB = 1500
SNMP_HISTORY_RETENTION_DAYS = 3
SNMP_HISTORY_PURGE_INTERVAL_MIN = 60

DB_MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", TCP_THREADPOOL_WORKERS + 20))
DB_ACQUIRE_TIMEOUT = float(os.getenv("DB_ACQUIRE_TIMEOUT", 15.0))
DEVICE_PERSIST_QUEUE_MAXSIZE = int(os.getenv("DEVICE_PERSIST_QUEUE_MAXSIZE", 2000))
DEVICE_PERSIST_FLUSH_INTERVAL_MS = int(
    os.getenv("DEVICE_PERSIST_FLUSH_INTERVAL_MS", 100)
)
DEVICE_PERSIST_BATCH_SIZE = int(os.getenv("DEVICE_PERSIST_BATCH_SIZE", 200))
TCP_MAX_CLIENTS = 500
TCP_ACCEPT_EMFILE_BACKOFF_MS = int(os.getenv("TCP_ACCEPT_EMFILE_BACKOFF_MS", 1000))
TCP_EMFILE_DROP_COUNT = int(os.getenv("TCP_EMFILE_DROP_COUNT", 50))
