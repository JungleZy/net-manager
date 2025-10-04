import os
from pathlib import Path

# UDP配置
UDP_HOST = "<broadcast>"  # 广播地址
UDP_PORT = 12345  # UDP端口（用于服务发现）

# TCP配置
TCP_PORT = 12346  # TCP端口（用于数据传输）

# 数据收集间隔（秒）
COLLECT_INTERVAL = 10

# 日志配置
LOG_LEVEL = "INFO"
# 使用pathlib处理跨平台路径
LOG_FILE = Path(__file__).parent.parent / "logs" / "net_manager_client.log"