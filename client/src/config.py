import os
from pathlib import Path

# UDP配置
UDP_PORT = 12306
# 使用广播地址发送UDP数据包
UDP_HOST = "<broadcast>"  # 广播地址

# SQLite数据库配置
DB_PATH = Path(__file__).parent.parent / "net_manager.db"

# 数据收集间隔（秒）
COLLECT_INTERVAL = 30

# 日志配置
LOG_LEVEL = "INFO"
# 使用pathlib处理跨平台路径
LOG_FILE = Path(__file__).parent.parent / "logs" / "net_manager.log"