#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态管理器
用于统一管理客户端状态，包括client_id的存储和读取
"""

import os
import sys
import json
import uuid
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from ..exceptions.exceptions import StateManagerError


class StateManager:
    """状态管理器，使用单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定模式
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):

        # 防止重复初始化
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.state_file = self._get_application_path() / "client_state.json"
        self.lock = threading.RLock()  # 使用可重入锁保护状态访问
        self._load_state()

    def _get_application_path(self) -> Path:
        """
        获取应用程序路径，兼容开发环境和打包环境

        Returns:
            Path: 应用程序路径
        """
        # 延迟导入logger以避免循环依赖
        from ..utils.logger import get_logger

        logger = get_logger()

        try:
            is_frozen = getattr(sys, "frozen", False)
            is_nuitka = "__compiled__" in globals()
            if is_frozen or is_nuitka:
                # 打包后的exe路径
                application_path = Path(sys.executable).parent
                logger.info(f"检测到打包环境，应用路径: {application_path}")
            else:
                # 开发环境路径
                application_path = Path(__file__).parent.parent.parent
                logger.info(f"检测到开发环境，应用路径: {application_path}")

            # 确保目录存在
            application_path.mkdir(parents=True, exist_ok=True)

            # 在Linux下设置目录权限
            if os.name != "nt":
                try:
                    os.chmod(application_path, 0o755)
                    logger.debug(f"已设置应用目录权限: {application_path}")
                except Exception as chmod_err:
                    logger.warning(f"设置应用目录权限失败: {chmod_err}")

            logger.info(
                f"应用程序路径: {application_path} (可写: {os.access(application_path, os.W_OK)})"
            )
            return application_path
        except PermissionError as e:
            logger.error(f"获取应用程序路径失败 - 权限不足: {e}")
            raise StateManagerError(f"无法确定应用程序路径 - 权限不足: {e}")
        except Exception as e:
            logger.error(f"获取应用程序路径失败: {e}")
            raise StateManagerError(f"无法确定应用程序路径: {e}")

    def _load_state(self) -> None:
        """
        加载状态文件
        """
        # 延迟导入logger以避免循环依赖
        from ..utils.logger import get_logger

        logger = get_logger()

        with self.lock:
            try:
                logger.info(f"尝试加载状态文件: {self.state_file}")
                logger.info(
                    f"文件存在: {self.state_file.exists()}, 目录可写: {os.access(self.state_file.parent, os.W_OK)}"
                )

                if self.state_file.exists():
                    with open(self.state_file, "r", encoding="utf-8") as f:
                        loaded_state = json.load(f)
                        if isinstance(loaded_state, dict):
                            self.state = loaded_state
                            logger.info(f"状态文件已加载: {self.state_file}")
                        else:
                            logger.warning("状态文件格式不正确，使用默认状态")
                            self.state = {}
                else:
                    # 初始化默认状态
                    logger.info("状态文件不存在，创建新的状态文件")
                    self.state = {}
                    self._save_state()
                    logger.info("创建新的状态文件")
            except json.JSONDecodeError as e:
                logger.error(f"解析状态文件失败: {e}")
                # 使用默认状态
                self.state = {}
            except PermissionError as e:
                logger.error(f"加载状态文件失败 - 权限不足: {e}")
                logger.error(f"目标路径: {self.state_file}")
                # 使用默认状态
                self.state = {}
            except Exception as e:
                logger.error(f"加载状态文件失败: {e}")
                logger.error(f"目标路径: {self.state_file}")
                # 使用默认状态
                self.state = {}

    def _save_state(self) -> None:
        """
        保存状态到文件
        """
        # 延迟导入logger以避免循环依赖
        from ..utils.logger import get_logger

        logger = get_logger()

        try:
            # 确保目录存在
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            # 在Linux下设置目录权限
            if os.name != "nt":
                try:
                    os.chmod(self.state_file.parent, 0o755)
                except Exception as chmod_err:
                    logger.warning(f"设置目录权限失败: {chmod_err}")

            # 写入状态文件
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)

            # 在Linux下设置文件权限
            if os.name != "nt":
                try:
                    os.chmod(self.state_file, 0o644)
                except Exception as chmod_err:
                    logger.warning(f"设置文件权限失败: {chmod_err}")

            logger.debug(f"状态已保存到: {self.state_file}")
        except PermissionError as e:
            logger.error(f"保存状态文件失败 - 权限不足: {e}")
            logger.error(f"目标路径: {self.state_file}")
            logger.error(f"请检查目录权限或以适当权限运行程序")
            raise StateManagerError(f"保存状态文件失败 - 权限不足: {e}")
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")
            logger.error(f"目标路径: {self.state_file}")
            raise StateManagerError(f"保存状态文件失败: {e}")

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        获取状态值

        Args:
            key: 状态键
            default: 默认值

        Returns:
            状态值或默认值
        """
        with self.lock:
            return self.state.get(key, default)

    def set_state(self, key: str, value: Any) -> bool:
        """
        设置状态值

        Args:
            key: 状态键
            value: 状态值

        Returns:
            是否设置成功
        """
        # 延迟导入logger以避免循环依赖
        from ..utils.logger import get_logger

        logger = get_logger()

        with self.lock:
            try:
                self.state[key] = value
                self.state["udp_port"] = 12345
                self.state["tcp_port"] = 12346
                self.state["collect_interval"] = 10
                self._save_state()
                return True
            except Exception as e:
                logger.error(f"设置状态失败: {e}")
                return False

    def update_states(self, states: Dict[str, Any]) -> bool:
        """
        批量更新状态

        Args:
            states: 状态字典

        Returns:
            是否更新成功
        """
        # 延迟导入logger以避免循环依赖
        from ..utils.logger import get_logger

        logger = get_logger()

        with self.lock:
            try:
                self.state.update(states)
                self._save_state()
                return True
            except Exception as e:
                logger.error(f"批量更新状态失败: {e}")
                return False

    def get_client_id(self) -> str:
        """
        获取客户端ID，如果不存在则生成一个新的

        Returns:
            客户端ID

        Raises:
            StateManagerError: 获取或生成客户端ID失败
        """
        # 延迟导入logger以避免循环依赖
        from ..utils.logger import get_logger

        logger = get_logger()

        try:
            client_id = self.get_state("client_id")
            if not client_id:
                # 生成新的UUID作为client_id
                client_id = str(uuid.uuid4())
                if not self.set_state("client_id", client_id):
                    raise StateManagerError("无法保存新生成的客户端ID")
                logger.info(f"生成新的客户端ID: {client_id}")
            return client_id
        except Exception as e:
            logger.error(f"获取客户端ID失败: {e}")
            raise StateManagerError(f"获取客户端ID失败: {e}")


# 创建全局状态管理器实例
_state_manager_instance: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """
    获取全局状态管理器实例

    Returns:
        StateManager: 状态管理器实例

    Raises:
        StateManagerError: 初始化状态管理器失败
    """
    global _state_manager_instance
    if _state_manager_instance is None:
        try:
            _state_manager_instance = StateManager()
        except Exception as e:
            # 延迟导入logger以避免循环依赖
            from ..utils.logger import get_logger

            logger = get_logger()
            logger.error(f"初始化状态管理器失败: {e}")
            raise StateManagerError(f"初始化状态管理器失败: {e}")
    return _state_manager_instance
