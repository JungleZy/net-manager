import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# 修复导入路径问题
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from config import LOG_LEVEL, LOG_FILE
except ImportError:
    # 如果直接运行此文件，使用相对导入
    from .config import LOG_LEVEL, LOG_FILE

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

def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    # 确保log_file是Path对象
    if isinstance(log_file, str):
        log_file = Path(log_file)
    
    # 创建日志目录（如果不存在）
    log_dir = log_file.parent
    if log_dir and not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取记录器
    logger = logging.getLogger(name)
    
    # 如果记录器已有处理器，先清空它们以避免重复日志
    if logger.handlers:
        logger.handlers.clear()
    
    # 设置日志级别
    logger.setLevel(level)
    
    # 创建日志格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 根据平台选择适当的编码
    file_encoding = get_appropriate_encoding()
    
    # 文件处理器
    file_handler = logging.FileHandler(str(log_file), encoding=file_encoding)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)  # 明确指定stdout
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# 创建全局日志记录器
log_level = get_log_level(LOG_LEVEL)
# 确保LOG_FILE是Path对象
if isinstance(LOG_FILE, str):
    LOG_FILE = Path(LOG_FILE)
logger = setup_logger('net_manager', LOG_FILE, log_level)