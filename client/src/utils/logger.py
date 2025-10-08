import logging
import os
import sys
from typing import Optional
from src.exceptions.exceptions import ConfigurationError

# 延迟导入以避免循环依赖
# from src.utils.platform_utils import get_appropriate_encoding, normalize_path

# 全局日志记录器实例
_logger: Optional[logging.Logger] = None

def get_appropriate_encoding() -> str:
    """
    获取适合当前平台的编码格式
    
    Returns:
        str: 适合当前平台的编码格式
    """
    import platform
    if platform.system() == 'Windows':
        return 'gbk'
    else:
        return 'utf-8'

def normalize_path(path: str) -> str:
    """
    标准化路径，将路径中的分隔符统一为当前平台的分隔符
    
    Args:
        path (str): 原始路径
        
    Returns:
        str: 标准化后的路径
    """
    import os
    return os.path.normpath(path)

def get_log_level() -> int:
    """
    根据配置获取日志级别
    
    Returns:
        int: 日志级别常量
        
    Raises:
        ConfigurationError: 配置获取失败
    """
    try:
        # 延迟导入以避免循环依赖
        from src.config_module.config import config
        # 检查config是否已正确初始化
        if hasattr(config, 'get'):
            level_str = config.get('logging', 'level', 'INFO').upper()
        else:
            # 如果config未正确初始化，使用默认值
            level_str = 'INFO'
        level = getattr(logging, level_str, logging.INFO)
        return level
    except Exception as e:
        # 如果配置获取失败，返回默认级别
        logging.warning(f"获取日志级别配置失败: {e}，使用默认级别INFO")
        return logging.INFO

def setup_logger() -> logging.Logger:
    """
    设置并获取日志记录器实例
    
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    global _logger
    
    # 如果已经初始化过，直接返回
    if _logger is not None:
        return _logger
    
    # 创建日志记录器
    _logger = logging.getLogger('net_manager')
    
    # 禁止传播到父logger（根logger），避免重复日志
    _logger.propagate = False
    
    try:
        # 获取日志级别
        level = get_log_level()
        _logger.setLevel(level)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器（如果还没有）
        if not any(isinstance(handler, logging.StreamHandler) for handler in _logger.handlers):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            _logger.addHandler(console_handler)
        
        # 添加文件处理器（如果还没有）
        if not any(isinstance(handler, logging.FileHandler) for handler in _logger.handlers):
            try:
                # 延迟导入以避免循环依赖
                from src.config_module.config import config
                # 检查config是否已正确初始化
                if hasattr(config, 'get'):
                    log_file = config.get('logging', 'file', 'logs/net_manager.log')
                else:
                    # 如果config未正确初始化，使用默认值
                    log_file = 'logs/net_manager.log'
                log_file = normalize_path(log_file)
                
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                # 使用适合平台的编码
                encoding = get_appropriate_encoding()
                file_handler = logging.FileHandler(log_file, encoding=encoding)
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                _logger.addHandler(file_handler)
            except Exception as e:
                # 文件日志设置失败不中断程序
                logging.warning(f"设置文件日志失败: {e}")
        
        return _logger
    except Exception as e:
        # 初始化失败时创建基本的日志记录器
        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            _logger.addHandler(handler)
        _logger.error(f"日志记录器初始化失败: {e}")
        return _logger

def get_logger() -> logging.Logger:
    """
    获取日志记录器实例
    
    Returns:
        logging.Logger: 日志记录器实例
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger