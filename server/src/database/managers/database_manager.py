#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一数据库管理器 - 整合设备和交换机管理功能
"""

from typing import List, Dict, Any, Optional, Tuple

from src.core.logger import logger
from src.models.system_info import SystemInfo
from src.models.switch_info import SwitchInfo
from src.database.db_exceptions import (
    DatabaseError, 
    DatabaseConnectionError, 
    DatabaseInitializationError,
    DatabaseQueryError,
    DeviceNotFoundError,
    DeviceAlreadyExistsError
)
from src.database.managers.base_manager import BaseDatabaseManager
from src.database.managers.device_manager import DeviceManager
from src.database.managers.switch_manager import SwitchManager


class DatabaseManager:
    """统一数据库管理器类
    
    整合设备和交换机管理功能，提供统一的数据库操作接口。
    """
    
    def __init__(self, db_path: str = "net_manager_server.db"):
        """
        初始化统一数据库管理器
        
        Args:
            db_path: 数据库文件路径
            
        Raises:
            DatabaseInitializationError: 数据库初始化失败时抛出
        """
        try:
            self.base_manager = BaseDatabaseManager(db_path)
            self.device_manager = DeviceManager(db_path)
            self.switch_manager = SwitchManager(db_path)
            logger.info("数据库管理器初始化成功")
        except Exception as e:
            logger.error(f"数据库管理器初始化失败: {e}")
            raise DatabaseInitializationError(f"数据库管理器初始化失败: {e}") from e

    # ==================== 数据库健康检查 ====================

    def health_check(self) -> bool:
        """
        数据库健康检查
        
        Returns:
            数据库连接正常返回True，否则返回False
        """
        try:
            with self.base_manager.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

    # ==================== 设备信息管理方法 ====================

    def save_system_info(self, system_info: SystemInfo) -> None:
        """
        保存设备信息到数据库
        
        Args:
            system_info: SystemInfo对象
            
        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
        """
        return self.device_manager.save_system_info(system_info)

    def get_all_system_info(self) -> List[Dict[str, Any]]:
        """
        获取所有设备信息
        
        Returns:
            包含所有设备信息的字典列表，按时间戳降序排列
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.device_manager.get_all_system_info()

    def get_system_info_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """
        根据MAC地址获取设备信息
        
        Args:
            mac_address: MAC地址
            
        Returns:
            设备信息字典，如果未找到则返回None
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.device_manager.get_system_info_by_mac(mac_address)

    def update_system_type(self, mac_address: str, device_type: str) -> bool:
        """
        更新设备类型
        
        Args:
            mac_address: MAC地址
            device_type: 设备类型
            
        Returns:
            更新成功返回True，设备不存在返回False
            
        Raises:
            DatabaseQueryError: 更新失败时抛出
        """
        return self.device_manager.update_system_type(mac_address, device_type)

    def create_device(self, device_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        创建新设备
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 创建失败时抛出
            DeviceAlreadyExistsError: 设备已存在时抛出
        """
        return self.device_manager.create_device(device_data)

    def update_device(self, device_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新设备信息
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 更新失败时抛出
            DeviceNotFoundError: 设备不存在时抛出
        """
        return self.device_manager.update_device(device_data)

    def delete_device(self, mac_address: str) -> Tuple[bool, str]:
        """
        删除设备
        
        Args:
            mac_address: MAC地址
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 删除失败时抛出
            DeviceNotFoundError: 设备不存在时抛出
        """
        return self.device_manager.delete_device(mac_address)

    def get_device_count(self) -> int:
        """
        获取设备总数
        
        Returns:
            设备总数
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.device_manager.get_device_count()

    # ==================== 交换机信息管理方法 ====================

    def add_switch(self, switch_info: 'SwitchInfo') -> Tuple[bool, str]:
        """
        添加新的交换机配置
        
        Args:
            switch_info: SwitchInfo对象
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 数据库操作失败时抛出
            DeviceAlreadyExistsError: 交换机IP已存在时抛出
        """
        return self.switch_manager.add_switch(switch_info)

    def update_switch(self, switch_info: 'SwitchInfo') -> Tuple[bool, str]:
        """
        更新交换机配置
        
        Args:
            switch_info: SwitchInfo对象
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 更新失败时抛出
            DeviceNotFoundError: 交换机不存在时抛出
        """
        return self.switch_manager.update_switch(switch_info)

    def delete_switch(self, switch_id: int) -> Tuple[bool, str]:
        """
        删除交换机配置
        
        Args:
            switch_id: 交换机ID
            
        Returns:
            (成功标志, 消息) 的元组
            
        Raises:
            DatabaseQueryError: 删除失败时抛出
            DeviceNotFoundError: 交换机不存在时抛出
        """
        return self.switch_manager.delete_switch(switch_id)

    def get_switch_by_id(self, switch_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取交换机配置
        
        Args:
            switch_id: 交换机ID
            
        Returns:
            交换机配置字典，如果未找到则返回None
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.switch_manager.get_switch_by_id(switch_id)

    def get_switch_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        根据IP地址获取交换机配置
        
        Args:
            ip: 交换机IP地址
            
        Returns:
            交换机配置字典，如果未找到则返回None
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.switch_manager.get_switch_by_ip(ip)

    def get_all_switches(self) -> List[Dict[str, Any]]:
        """
        获取所有交换机配置
        
        Returns:
            包含所有交换机配置的字典列表，按创建时间降序排列
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.switch_manager.get_all_switches()

    def get_switch_count(self) -> int:
        """
        获取交换机总数
        
        Returns:
            交换机总数
            
        Raises:
            DatabaseQueryError: 查询失败时抛出
        """
        return self.switch_manager.get_switch_count()