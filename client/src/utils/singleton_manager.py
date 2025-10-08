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
from typing import Optional

class SingletonManager:
    """单例管理器，确保应用程序只能运行一个实例"""
    
    def __init__(self, app_name: str):
        """
        初始化单例管理器
        
        Args:
            app_name (str): 应用程序名称，用于创建唯一的互斥体标识
        """
        self.app_name = app_name
        self.lock_handle = None
        self.lock_file_path = None
        self.is_locked = False
        
        # 根据操作系统选择实现方式
        self.system = platform.system().lower()
        
    def acquire_lock(self) -> bool:
        """
        获取互斥锁，确保只有一个实例运行
        
        Returns:
            bool: 获取锁成功返回True，否则返回False
        """
        if self.system == "windows":
            return self._acquire_lock_windows()
        else:
            # Linux/Unix系统使用文件锁
            return self._acquire_lock_unix()
    
    def _acquire_lock_windows(self) -> bool:
        """
        Windows平台获取命名互斥体锁
        
        Returns:
            bool: 获取锁成功返回True，否则返回False
        """
        try:
            # Windows使用ctypes调用系统API创建命名互斥体
            import ctypes
            from ctypes import wintypes
            
            # 定义Windows API函数
            kernel32 = ctypes.windll.kernel32
            
            # CreateMutex函数原型
            kernel32.CreateMutexW.argtypes = [
                wintypes.LPCVOID,  # lpMutexAttributes
                wintypes.BOOL,     # bInitialOwner
                wintypes.LPCWSTR   # lpName
            ]
            kernel32.CreateMutexW.restype = wintypes.HANDLE
            
            # GetLastError函数原型
            kernel32.GetLastError.argtypes = []
            kernel32.GetLastError.restype = wintypes.DWORD
            
            # 定义错误码
            ERROR_ALREADY_EXISTS = 183
            
            # 创建命名互斥体
            mutex_name = f"Global\\{self.app_name}_Singleton_Mutex"
            handle = kernel32.CreateMutexW(None, True, mutex_name)
            
            # 检查是否已经存在同名互斥体
            last_error = kernel32.GetLastError()
            if last_error == ERROR_ALREADY_EXISTS:
                # 互斥体已存在，说明已经有实例在运行
                if handle:
                    kernel32.CloseHandle(handle)
                return False
            
            # 保存互斥体句柄
            self.lock_handle = handle
            self.is_locked = True
            return True
            
        except Exception as e:
            # 如果Windows API调用失败，回退到文件锁机制
            print(f"Windows互斥体创建失败，回退到文件锁机制: {e}")
            return self._acquire_lock_unix()
    
    def _acquire_lock_unix(self) -> bool:
        """
        Unix/Linux平台获取文件锁
        
        Returns:
            bool: 获取锁成功返回True，否则返回False
        """
        try:
            # 使用文件锁机制
            # 获取应用程序路径
            is_frozen = hasattr(sys, 'frozen') and sys.frozen
            is_nuitka = '__compiled__' in globals()
            
            if is_frozen or is_nuitka:
                # 打包后的可执行文件路径
                application_path = os.path.dirname(sys.executable)
            elif '__compiled__' in globals():
                # Nuitka打包环境
                application_path = os.path.dirname(os.path.abspath(__file__))
            else:
                # 开发环境
                application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 创建锁文件路径
            self.lock_file_path = os.path.join(application_path, f"{self.app_name}.lock")
            
            # 检查锁文件是否已存在
            if os.path.exists(self.lock_file_path):
                # 检查锁文件是否有效（进程是否仍在运行）
                try:
                    with open(self.lock_file_path, "r") as f:
                        pid = int(f.read().strip())
                    # 检查进程是否存在
                    try:
                        os.kill(pid, 0)  # 检查进程是否存在
                        # 进程存在，说明已经有实例在运行
                        return False
                    except OSError:
                        # 进程不存在，可以继续
                        pass
                except (ValueError, IOError):
                    # 锁文件损坏或无法读取，继续执行
                    pass
            
            # 创建新的锁文件
            with open(self.lock_file_path, "w") as f:
                f.write(str(os.getpid()))
            
            self.is_locked = True
            return True
            
        except IOError:
            print("无法创建锁文件，可能没有写入权限")
            return False
    
    def release_lock(self) -> None:
        """释放互斥锁"""
        if not self.is_locked:
            return
            
        if self.system == "windows":
            self._release_lock_windows()
        else:
            self._release_lock_unix()
    
    def _release_lock_windows(self) -> None:
        """Windows平台释放命名互斥体锁"""
        if self.lock_handle:
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.CloseHandle(self.lock_handle)
                self.lock_handle = None
                self.is_locked = False
            except Exception:
                pass
    
    def _release_lock_unix(self) -> None:
        """Unix/Linux平台释放文件锁"""
        if self.lock_file_path and os.path.exists(self.lock_file_path):
            try:
                os.remove(self.lock_file_path)
                self.is_locked = False
            except OSError:
                pass

# 全局单例管理器实例
_client_singleton_manager: Optional[SingletonManager] = None
_server_singleton_manager: Optional[SingletonManager] = None

def get_client_singleton_manager() -> SingletonManager:
    """获取客户端单例管理器实例"""
    global _client_singleton_manager
    if _client_singleton_manager is None:
        _client_singleton_manager = SingletonManager("NetManagerClient")
    return _client_singleton_manager