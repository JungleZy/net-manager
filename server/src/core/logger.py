#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块 - 负责设置和管理Net Manager的日志系统

该模块提供了日志记录器的配置功能，支持：
1. 按天自动切分日志文件
2. 控制台和文件双输出
3. 跨平台编码支持
4. 可配置的日志级别
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# 修复导入路径问题，确保可以正确导入配置
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 导入配置中的日志设置
# 优先尝试绝对导入，失败则使用相对导入（用于直接运行此文件时）
try:
    from config import LOG_LEVEL, LOG_FILE
except ImportError:
    from .config import LOG_LEVEL, LOG_FILE


def get_log_level(level_str):
    """根据字符串获取对应的日志级别常量
    
    Args:
        level_str: 日志级别字符串，如 "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        
    Returns:
        int: 对应的logging模块日志级别常量
    """
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return levels.get(level_str.upper(), logging.INFO)  # 默认返回INFO级别


def get_appropriate_encoding():
    """根据操作系统获取适合的文件编码
    
    Returns:
        str: 适合当前平台的编码字符串
    """
    import platform

    if platform.system().lower() == "windows":
        return "gbk"  # Windows中文系统通常使用gbk编码
    return "utf-8"  # Unix-like系统通常使用utf-8编码


def setup_logger(name, log_file, level=logging.INFO):
    """配置日志记录器，支持按天切分日志
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（字符串或Path对象）
        level: 日志级别，默认为logging.INFO
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    # 确保log_file是Path对象，便于路径操作
    if isinstance(log_file, str):
        log_file = Path(log_file)

    # 创建日志目录（如果不存在）
    log_dir = log_file.parent
    if log_dir and not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)  # 递归创建目录，忽略已存在的情况

    # 获取或创建日志记录器
    logger = logging.getLogger(name)

    # 清空现有处理器，避免重复日志输出
    if logger.handlers:
        logger.handlers.clear()

    # 设置日志级别
    logger.setLevel(level)

    # 创建日志格式化器，定义日志输出格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 根据平台选择适当的文件编码
    file_encoding = get_appropriate_encoding()

    # 配置按天滚动的文件日志处理器
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",  # 在午夜进行日志切分
        interval=1,  # 每1天切分一次
        backupCount=30,  # 保留最近30天的日志文件
        encoding=file_encoding,  # 使用适合平台的编码
    )
    
    # 设置日志文件名后缀格式为 YYYY-MM-DD.log
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 配置控制台日志处理器，输出到标准输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 创建全局日志记录器实例，供其他模块直接使用
log_level = get_log_level(LOG_LEVEL)  # 从配置获取日志级别

# 确保LOG_FILE是Path对象
if isinstance(LOG_FILE, str):
    LOG_FILE = Path(LOG_FILE)

# 初始化全局日志记录器
logger = setup_logger("net_manager", LOG_FILE, log_level)
