#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
客户端状态管理器
用于统一管理客户端状态，包括client_id的存储和读取
"""

import os
import sys
import json
import threading
from typing import Optional, Any
from pathlib import Path

from .logger import logger
from .unique_id import get_or_create_unique_id


class StateManager:
    """客户端状态管理器，用于存储和读取客户端状态"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """确保单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(StateManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化状态管理器"""
        # 防止重复初始化
        if hasattr(self, '_initialized'):
            return
            
        self._state = {}
        self._state_lock = threading.RLock()
        self._initialized = True
        self._client_id = None
        
        # 获取应用程序路径
        self._app_path = self._get_application_path()
        
        # 添加调试信息
        print(f"DEBUG StateManager: _app_path = {self._app_path}")
        
        # 加载现有状态
        self._load_state()
        
        # 获取或创建客户端ID
        self._client_id = get_or_create_unique_id(self._app_path)
        self.set_state('client_id', self._client_id)
    
    def _get_application_path(self) -> str:
        """获取应用程序路径，兼容开发环境和打包环境"""
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
        
        # 添加调试信息
        print(f"DEBUG StateManager._get_application_path: application_path = {application_path}")
        
        return application_path
    
    def _get_state_file_path(self) -> str:
        """获取状态文件路径"""
        state_file_path = os.path.join(self._app_path, "client_state.json")
        # 添加调试信息
        print(f"DEBUG StateManager._get_state_file_path: state_file_path = {state_file_path}")
        return state_file_path
    
    def _load_state(self) -> None:
        """从文件加载状态"""
        try:
            state_file = self._get_state_file_path()
            print(f"DEBUG StateManager._load_state: state_file = {state_file}")
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    with self._state_lock:
                        self._state.update(loaded_state)
                logger.debug("状态已从文件加载")
                print("DEBUG StateManager._load_state: 状态已从文件加载")
            else:
                logger.debug("状态文件不存在，使用默认状态")
                print("DEBUG StateManager._load_state: 状态文件不存在，使用默认状态")
        except Exception as e:
            logger.error(f"加载状态失败: {e}")
            print(f"DEBUG StateManager._load_state: 加载状态失败: {e}")
    
    def _save_state(self) -> None:
        """将状态保存到文件"""
        try:
            state_file = self._get_state_file_path()
            print(f"DEBUG StateManager._save_state: state_file = {state_file}")
            with self._state_lock:
                state_copy = self._state.copy()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(state_file), exist_ok=True)
            print(f"DEBUG StateManager._save_state: 目录已创建或已存在")
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_copy, f, ensure_ascii=False, indent=2)
            logger.debug("状态已保存到文件")
            print("DEBUG StateManager._save_state: 状态已保存到文件")
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
            print(f"DEBUG StateManager._save_state: 保存状态失败: {e}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        获取状态值
        
        Args:
            key (str): 状态键
            default (Any): 默认值
            
        Returns:
            Any: 状态值
        """
        with self._state_lock:
            return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        """
        设置状态值
        
        Args:
            key (str): 状态键
            value (Any): 状态值
        """
        with self._state_lock:
            self._state[key] = value
        # 自动保存状态
        self._save_state()
        logger.debug(f"状态已更新: {key} = {value}")
        print(f"DEBUG StateManager.set_state: 状态已更新: {key} = {value}")
    
    def get_client_id(self) -> str:
        """
        获取客户端唯一标识符
        
        Returns:
            str: 客户端唯一标识符
        """
        return self._client_id
    
    def update_client_state(self, state_data: dict) -> None:
        """
        批量更新客户端状态
        
        Args:
            state_data (dict): 状态数据字典
        """
        with self._state_lock:
            self._state.update(state_data)
        self._save_state()
        logger.debug(f"批量更新状态: {list(state_data.keys())}")


# 全局状态管理器实例
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """获取全局状态管理器实例"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager