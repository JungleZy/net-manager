import os

# UDP配置
UDP_PORT = 12306
# 使用广播地址发送UDP数据包
UDP_HOST = "<broadcast>"  # 广播地址

# SQLite数据库配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "net_manager.db")

# 数据收集间隔（秒）
COLLECT_INTERVAL = 30

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "net_manager.log")