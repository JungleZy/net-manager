import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from src.config import LOG_LEVEL, LOG_FILE

def get_log_level(level_str):
    """根据字符串返回日志级别"""
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return levels.get(level_str.upper(), logging.INFO)

def get_appropriate_encoding():
    """获取适合当前平台的文件编码"""
    import platform
    if platform.system().lower() == 'windows':
        return 'gbk'  # Windows中文系统通常使用gbk编码
    return 'utf-8'  # Unix-like系统通常使用utf-8编码

def setup_logger(name, log_file=None, level=logging.INFO):
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding=get_appropriate_encoding())
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"创建文件日志处理器失败: {e}")
            # 即使文件日志创建失败，控制台日志仍然可以工作
    
    return logger

# 创建全局日志记录器
log_level = get_log_level(LOG_LEVEL)
# 确保LOG_FILE是Path对象
if isinstance(LOG_FILE, str):
    LOG_FILE = Path(LOG_FILE)
logger = setup_logger('net_manager', LOG_FILE, log_level)