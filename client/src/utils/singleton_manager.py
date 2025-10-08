#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
跨平台单例管理器
使用命名互斥体确保应用程序只能运行一个实例
兼容Windows和Linux平台
"""

import os
import sys
import platform
import threading
from typing import Optional
import uuid

try:
    import win32event
    import win32api
    import winerror
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from ..utils.platform_utils import get_executable_path, normalize_path
from ..exceptions.exceptions import SingletonManagerError
from ..utils.logger import get_logger

# 延迟初始化logger以避免循环依赖
_logger = None

def _get_logger():
    global _logger
    if _logger is None:
        _logger = get_logger()
    return _logger

class SingletonManager:
    """单例管理器，确保应用只运行一个实例"""
    
    def __init__(self):
        self.lock_handle: Optional[int] = None
        self.lock_file: Optional[str] = None
        self.lock_acquired = False
        self._lock = threading.RLock()  # 使用可重入锁
        
    def _get_lock_name(self) -> str:
        """
        获取锁名称
        
        Returns:
            str: 锁名称
        """
        # 使用固定的名称加上用户名和主机名，确保在不同环境下生成一致的名称
        import getpass
        import socket
        try:
            username = getpass.getuser()
        except Exception:
            username = "unknown"
            
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "unknown"
            
        # 使用固定的前缀加上用户名和主机名
        return f"net_manager_client_{username}_{hostname}"
    
    def _acquire_windows_lock(self) -> bool:
        """
        在Windows系统上获取锁
        
        Returns:
            bool: 成功获取锁返回True，否则返回False
        """
        if not WIN32_AVAILABLE:
            _get_logger().warning("Windows API不可用，无法创建Windows锁，请安装pywin32库")
            return False
            
        try:
            lock_name = self._get_lock_name()
            _get_logger().debug(f"尝试获取Windows锁，锁名称: {lock_name}")
            # 创建命名互斥体
            self.lock_handle = win32event.CreateMutex(
                None,  # 安全属性
                False,  # 初始不拥有
                lock_name  # 互斥体名称
            )
            
            # 检查是否已经存在
            last_error = win32api.GetLastError()
            _get_logger().debug(f"Windows锁创建后LastError: {last_error}")
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                # 锁已被占用
                _get_logger().warning(f"检测到已存在的实例，无法获取锁。锁名称: {lock_name}")
                try:
                    win32api.CloseHandle(self.lock_handle)
                except Exception as e:
                    _get_logger().warning(f"关闭锁句柄时出错: {e}")
                self.lock_handle = None
                return False
            elif last_error != 0:
                # 其他错误
                _get_logger().error(f"创建Windows锁时发生错误，错误码: {last_error}")
                try:
                    win32api.CloseHandle(self.lock_handle)
                except Exception as e:
                    _get_logger().warning(f"关闭锁句柄时出错: {e}")
                self.lock_handle = None
                return False
                
            _get_logger().info(f"成功获取Windows锁: {lock_name}")
            return True
        except Exception as e:
            _get_logger().error(f"获取Windows锁失败: {e}")
            # 确保句柄被正确清理
            if self.lock_handle:
                try:
                    win32api.CloseHandle(self.lock_handle)
                except Exception as close_e:
                    _get_logger().warning(f"关闭锁句柄时出错: {close_e}")
                self.lock_handle = None
            return False
    
    def _acquire_unix_lock(self) -> bool:
        """
        在Unix/Linux系统上获取锁
        
        Returns:
            bool: 成功获取锁返回True，否则返回False
        """
        try:
            lock_name = self._get_lock_name()
            _get_logger().debug(f"尝试获取Unix锁，锁名称: {lock_name}")
            # 在临时目录创建锁文件
            temp_dir = "/tmp" if os.path.exists("/tmp") else os.path.expanduser("~")
            self.lock_file = os.path.join(temp_dir, f"{lock_name}.lock")
            _get_logger().debug(f"锁文件路径: {self.lock_file}")
            
            # 打开或创建锁文件
            self.lock_handle = os.open(
                self.lock_file,
                os.O_CREAT | os.O_RDWR | os.O_TRUNC
            )
            
            # 尝试获取排他锁
            try:
                import fcntl
                fcntl.flock(self.lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # 写入进程ID
                os.write(self.lock_handle, str(os.getpid()).encode())
                _get_logger().info(f"成功获取Unix锁: {self.lock_file}")
                return True
            except (IOError, OSError) as e:
                # 锁已被占用
                _get_logger().warning(f"无法获取Unix锁，可能已存在实例: {e}")
                try:
                    os.close(self.lock_handle)
                except Exception as close_e:
                    _get_logger().warning(f"关闭锁文件时出错: {close_e}")
                self.lock_handle = None
                # 不立即删除锁文件，因为它可能被其他实例使用
                self.lock_file = None
                return False
                
        except Exception as e:
            _get_logger().error(f"获取Unix锁失败: {e}")
            # 确保资源被正确清理
            if self.lock_handle:
                try:
                    os.close(self.lock_handle)
                except Exception as close_e:
                    _get_logger().warning(f"关闭锁文件时出错: {close_e}")
                self.lock_handle = None
            if self.lock_file:
                # 在创建锁文件失败的情况下，尝试删除可能创建的空文件
                if os.path.exists(self.lock_file):
                    try:
                        os.remove(self.lock_file)
                    except Exception as remove_e:
                        _get_logger().warning(f"删除锁文件时出错: {remove_e}")
                self.lock_file = None
            return False
    
    def acquire_lock(self) -> bool:
        """
        获取单例锁
        
        Returns:
            bool: 成功获取锁返回True，否则返回False
            
        Raises:
            SingletonManagerError: 获取锁过程中发生错误
        """
        with self._lock:
            if self.lock_acquired:
                return True
                
            try:
                system = platform.system().lower()
                if system == "windows":
                    success = self._acquire_windows_lock()
                else:
                    success = self._acquire_unix_lock()
                
                if success:
                    self.lock_acquired = True
                else:
                    # 获取锁失败时清理资源
                    self.release_lock()
                    
                return success
            except Exception as e:
                _get_logger().error(f"获取单例锁过程中发生错误: {e}")
                # 确保在异常情况下也释放资源
                self.release_lock()
                raise SingletonManagerError(f"获取单例锁失败: {e}")
    
    def release_lock(self) -> None:
        """
        释放锁
        """
        with self._lock:
            if not self.lock_acquired:
                return
                
            try:
                system = platform.system().lower()
                if system == "windows" and self.lock_handle:
                    if WIN32_AVAILABLE:
                        try:
                            win32api.CloseHandle(self.lock_handle)
                        except Exception as e:
                            _get_logger().warning(f"关闭Windows锁句柄失败: {e}")
                    self.lock_handle = None
                elif self.lock_handle:
                    try:
                        import fcntl
                        fcntl.flock(self.lock_handle, fcntl.LOCK_UN)
                    except Exception as e:
                        _get_logger().warning(f"解锁Unix锁失败: {e}")
                    try:
                        os.close(self.lock_handle)
                    except Exception as e:
                        _get_logger().warning(f"关闭Unix锁文件失败: {e}")
                    self.lock_handle = None
                    
                    # 删除锁文件
                    if self.lock_file and os.path.exists(self.lock_file):
                        try:
                            os.remove(self.lock_file)
                        except Exception as e:
                            _get_logger().warning(f"删除锁文件失败: {e}")
                        self.lock_file = None
                
                self.lock_acquired = False
                _get_logger().debug("成功释放锁")
            except Exception as e:
                _get_logger().error(f"释放锁失败: {e}")
                # 即使释放失败，也要标记为未锁定以避免状态不一致
                self.lock_acquired = False

    def check_lock_status(self) -> dict:
        """
        检查锁的当前状态（用于调试）
        
        Returns:
            dict: 包含锁状态信息的字典
        """
        status = {
            "has_lock": self.lock_handle is not None,
            "lock_file": self.lock_file,
            "platform": sys.platform
        }
        
        # 添加锁名称信息
        try:
            status["lock_name"] = self._get_lock_name()
        except Exception as e:
            status["lock_name_error"] = str(e)
        
        # 对于Unix系统，检查锁文件是否存在
        if sys.platform != "win32" and self.lock_file:
            status["file_exists"] = os.path.exists(self.lock_file)
            if status["file_exists"]:
                try:
                    with open(self.lock_file, 'r') as f:
                        content = f.read().strip()
                        status["file_content"] = content
                        # 尝试检查进程是否存在
                        if content.isdigit():
                            pid = int(content)
                            status["pid"] = pid
                            # 在Unix系统上检查进程是否存在
                            try:
                                os.kill(pid, 0)  # 不发送信号，只检查进程是否存在
                                status["process_exists"] = True
                            except OSError:
                                status["process_exists"] = False
                except Exception as e:
                    status["read_error"] = str(e)
            
        return status

# 全局单例管理器实例
_singleton_manager: Optional[SingletonManager] = None
_singleton_manager_lock = threading.RLock()  # 使用可重入锁

def get_client_singleton_manager() -> SingletonManager:
    """
    获取客户端单例管理器实例
    
    Returns:
        SingletonManager: 单例管理器实例
        
    Raises:
        SingletonManagerError: 初始化单例管理器失败
    """
    global _singleton_manager
    
    with _singleton_manager_lock:
        if _singleton_manager is None:
            try:
                _singleton_manager = SingletonManager()
            except Exception as e:
                _get_logger().error(f"初始化单例管理器失败: {e}")
                raise SingletonManagerError(f"初始化单例管理器失败: {e}")
        return _singleton_manager