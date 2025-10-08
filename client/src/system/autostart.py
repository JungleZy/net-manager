#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开机自启动管理模块
负责在不同操作系统上启用/禁用客户端的开机自启动功能
支持Windows、Linux(systemd)
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional

# 第三方库导入
# 无

# 本地应用/库导入
from src.exceptions.exceptions import PlatformError, AutoStartError
from src.utils.logger import get_logger
from src.utils.platform_utils import (
    get_executable_path,
    get_appropriate_encoding,
    normalize_path
)

# Windows注册表路径常量，用于管理开机自启动项
WINDOWS_AUTOSTART_REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_client_executable_path() -> str:
    """
    获取客户端可执行文件路径
    
    Returns:
        str: 客户端可执行文件路径
        
    Raises:
        AutoStartError: 获取可执行文件路径失败
    """
    try:
        return get_executable_path()
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取客户端可执行文件路径失败: {e}")
        raise AutoStartError(f"获取客户端可执行文件路径失败: {e}")


def enable_autostart(daemon_script_path: Optional[str] = None) -> bool:
    """
    启用开机自启动
    
    Args:
        daemon_script_path (Optional[str]): 守护进程脚本路径
        
    Returns:
        bool: 是否成功启用开机自启动
    """
    logger = get_logger()
    system = platform.system().lower()
    
    try:
        if system == "windows":
            return _enable_autostart_windows(daemon_script_path)
        elif system == "linux":
            return _enable_autostart_linux(daemon_script_path)
        else:
            logger.error(f"不支持的操作系统: {system}")
            raise PlatformError(f"不支持的操作系统: {system}")
    except Exception as e:
        logger.error(f"启用开机自启动失败: {e}")
        return False


def disable_autostart(daemon_script_path: Optional[str] = None) -> bool:
    """
    禁用开机自启动
    
    Args:
        daemon_script_path (Optional[str]): 守护进程脚本路径
        
    Returns:
        bool: 是否成功禁用开机自启动
    """
    logger = get_logger()
    system = platform.system().lower()
    
    try:
        if system == "windows":
            return _disable_autostart_windows()
        elif system == "linux":
            return _disable_autostart_linux()
        else:
            logger.error(f"不支持的操作系统: {system}")
            raise PlatformError(f"不支持的操作系统: {system}")
    except Exception as e:
        logger.error(f"禁用开机自启动失败: {e}")
        return False


def is_autostart_enabled() -> bool:
    """
    检查是否已启用开机自启动
    
    Returns:
        bool: 是否已启用开机自启动
    """
    logger = get_logger()
    system = platform.system().lower()
    
    try:
        if system == "windows":
            return _is_autostart_enabled_windows()
        elif system == "linux":
            return _is_autostart_enabled_linux()
        else:
            logger.error(f"不支持的操作系统: {system}")
            raise PlatformError(f"不支持的操作系统: {system}")
    except Exception as e:
        logger.error(f"检查开机自启动状态失败: {e}")
        return False


def _enable_autostart_windows(daemon_script_path: Optional[str]) -> bool:
    """
    在Windows上启用开机自启动
    
    Args:
        daemon_script_path (Optional[str]): 守护进程脚本路径
        
    Returns:
        bool: 是否成功启用开机自启动
    """
    logger = get_logger()
    try:
        import winreg
        
        # 获取客户端可执行文件路径
        if daemon_script_path:
            executable_path = daemon_script_path
        else:
            executable_path = get_client_executable_path()
        
        # 打开注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_AUTOSTART_REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        
        # 设置开机自启动项
        winreg.SetValueEx(key, "NetManagerClient", 0, winreg.REG_SZ, executable_path)
        winreg.CloseKey(key)
        
        return True
    except Exception as e:
        logger.error(f"在Windows上启用开机自启动失败: {e}")
        return False


def _disable_autostart_windows() -> bool:
    """
    在Windows上禁用开机自启动
    
    Returns:
        bool: 是否成功禁用开机自启动
    """
    logger = get_logger()
    try:
        import winreg
        
        # 打开注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_AUTOSTART_REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        
        # 删除开机自启动项
        winreg.DeleteValue(key, "NetManagerClient")
        winreg.CloseKey(key)
        
        logger.info("Windows开机自启动已禁用")
        return True
    except FileNotFoundError:
        # 如果键不存在，说明已经禁用
        logger.info("Windows开机自启动已禁用（注册表项不存在）")
        return True
    except Exception as e:
        logger.error(f"在Windows上禁用开机自启动失败: {e}")
        return False


def _is_autostart_enabled_windows() -> bool:
    """
    检查Windows上是否已启用开机自启动
    
    Returns:
        bool: 是否已启用开机自启动
    """
    logger = get_logger()
    try:
        import winreg
        
        # 打开注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_AUTOSTART_REGISTRY_PATH,
            0,
            winreg.KEY_READ
        )
        
        # 检查是否存在开机自启动项
        try:
            value, _ = winreg.QueryValueEx(key, "NetManagerClient")
            winreg.CloseKey(key)
            return bool(value)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        logger.error(f"检查Windows开机自启动状态失败: {e}")
        return False


def _enable_autostart_linux(daemon_script_path: Optional[str]) -> bool:
    """
    在Linux上启用开机自启动（使用systemd）
    
    Args:
        daemon_script_path (Optional[str]): 守护进程脚本路径
        
    Returns:
        bool: 是否成功启用开机自启动
    """
    logger = get_logger()
    try:
        # 获取客户端可执行文件路径
        if daemon_script_path:
            executable_path = daemon_script_path
        else:
            executable_path = get_client_executable_path()
        
        # 创建systemd服务文件内容
        service_content = f"""[Unit]
Description=NetManager Client
After=network.target

[Service]
Type=simple
ExecStart={executable_path}
Restart=always
RestartSec=10
User={os.getenv('USER', 'root')}

[Install]
WantedBy=multi-user.target
"""
        
        # 获取服务文件路径
        service_file = Path.home() / ".config" / "systemd" / "user" / "netmanager-client.service"
        
        # 确保目录存在
        service_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入服务文件
        with open(service_file, "w", encoding=get_appropriate_encoding()) as f:
            f.write(service_content)
        
        # 启用服务
        os.system("systemctl --user daemon-reload")
        os.system("systemctl --user enable netmanager-client.service")
        
        logger.info("Linux开机自启动已启用")
        return True
    except Exception as e:
        logger.error(f"在Linux上启用开机自启动失败: {e}")
        return False


def _disable_autostart_linux() -> bool:
    """
    在Linux上禁用开机自启动（使用systemd）
    
    Returns:
        bool: 是否成功禁用开机自启动
    """
    logger = get_logger()
    try:
        # 获取服务文件路径
        service_file = Path.home() / ".config" / "systemd" / "user" / "netmanager-client.service"
        
        # 禁用并删除服务
        os.system("systemctl --user disable netmanager-client.service")
        service_file.unlink(missing_ok=True)
        
        # 重新加载systemd配置
        os.system("systemctl --user daemon-reload")
        
        logger.info("Linux开机自启动已禁用")
        return True
    except Exception as e:
        logger.error(f"在Linux上禁用开机自启动失败: {e}")
        return False


def _is_autostart_enabled_linux() -> bool:
    """
    检查Linux上是否已启用开机自启动（使用systemd）
    
    Returns:
        bool: 是否已启用开机自启动
    """
    logger = get_logger()
    try:
        # 检查服务是否已启用
        result = os.system("systemctl --user is-enabled netmanager-client.service > /dev/null 2>&1")
        return result == 0
    except Exception as e:
        logger.error(f"检查Linux开机自启动状态失败: {e}")
        return False


def create_daemon_script() -> Optional[str]:
    """
    创建守护进程脚本
    
    Returns:
        Optional[str]: 守护进程脚本路径，如果创建失败则返回None
    """
    logger = get_logger()
    system = platform.system().lower()
    
    try:
        if system == "windows":
            return _create_daemon_script_windows()
        elif system == "linux":
            return _create_daemon_script_linux()
        else:
            logger.error(f"不支持的操作系统: {system}")
            raise PlatformError(f"不支持的操作系统: {system}")
    except Exception as e:
        logger.error(f"创建守护进程脚本失败: {e}")
        return None


def _create_daemon_script_windows() -> Optional[str]:
    """
    在Windows上创建守护进程脚本
    
    Returns:
        Optional[str]: 守护进程脚本路径，如果创建失败则返回None
    """
    logger = get_logger()
    try:
        # 获取客户端可执行文件路径
        client_path = get_client_executable_path()
        
        # 创建批处理脚本内容
        script_content = f"""@echo off
"{client_path}"
"""
        
        # 获取脚本路径
        script_path = Path(normalize_path("./netmanager_daemon.bat"))
        
        # 写入脚本文件
        with open(script_path, "w", encoding=get_appropriate_encoding()) as f:
            f.write(script_content)
        
        logger.info(f"Windows守护进程脚本已创建: {script_path}")
        return str(script_path)
    except Exception as e:
        logger.error(f"在Windows上创建守护进程脚本失败: {e}")
        return None


def _create_daemon_script_linux() -> Optional[str]:
    """
    在Linux上创建守护进程脚本
    
    Returns:
        Optional[str]: 守护进程脚本路径，如果创建失败则返回None
    """
    logger = get_logger()
    try:
        # 获取客户端可执行文件路径
        client_path = get_client_executable_path()
        
        # 创建shell脚本内容
        script_content = f"""#!/bin/bash
{client_path}
"""
        
        # 获取脚本路径
        script_path = Path(normalize_path("./netmanager_daemon.sh"))
        
        # 写入脚本文件
        with open(script_path, "w", encoding=get_appropriate_encoding()) as f:
            f.write(script_content)
        
        # 添加执行权限
        os.chmod(script_path, 0o755)
        
        logger.info(f"Linux守护进程脚本已创建: {script_path}")
        return str(script_path)
    except Exception as e:
        logger.error(f"在Linux上创建守护进程脚本失败: {e}")
        return None


# 测试代码
if __name__ == "__main__":
    # 这里可以添加一些测试代码
    pass