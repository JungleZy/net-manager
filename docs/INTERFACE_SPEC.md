# Net Manager Server 接口规范定义

## 1. 概述

本文档定义了Net Manager Server中各模块间的接口规范，确保模块间的松耦合和高内聚。

## 2. 核心接口

### 2.1 数据库接口 (DatabaseInterface)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.system_info import SystemInfo

class DatabaseInterface(ABC):
    """数据库操作抽象接口"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化数据库"""
        pass
    
    @abstractmethod
    async def save_system_info(self, system_info: SystemInfo) -> None:
        """保存系统信息
        
        Args:
            system_info: SystemInfo对象
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        pass
    
    @abstractmethod
    async def get_all_system_info(self) -> List[Dict[str, Any]]:
        """获取所有系统信息
        
        Returns:
            包含所有系统信息的字典列表
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        pass
    
    @abstractmethod
    async def get_system_info_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """根据MAC地址获取系统信息
        
        Args:
            mac_address: MAC地址
            
        Returns:
            系统信息字典，如果未找到则返回None
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        pass
    
    @abstractmethod
    async def update_device_type(self, mac_address: str, device_type: str) -> bool:
        """更新设备类型
        
        Args:
            mac_address: MAC地址
            device_type: 设备类型
            
        Returns:
            更新是否成功
            
        Raises:
            DatabaseError: 数据库操作失败
        """
        pass
```

### 2.2 网络服务接口 (NetworkServerInterface)

```python
from abc import ABC, abstractmethod
from typing import Callable, Any

class NetworkServerInterface(ABC):
    """网络服务抽象接口"""
    
    @abstractmethod
    def start(self) -> None:
        """启动服务"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止服务"""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """检查服务是否正在运行
        
        Returns:
            服务运行状态
        """
        pass
    
    @abstractmethod
    def register_callback(self, event: str, callback: Callable) -> None:
        """注册事件回调函数
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        pass
```

### 2.3 配置管理接口 (ConfigInterface)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Callable

class ConfigInterface(ABC):
    """配置管理抽象接口"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项值
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项值
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """设置配置项值
        
        Args:
            key: 配置项键名
            value: 配置项值
        """
        pass
    
    @abstractmethod
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置项
        
        Args:
            config_dict: 配置字典
        """
        pass
    
    @abstractmethod
    def subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        """订阅配置项变更
        
        Args:
            key: 配置项键名
            callback: 变更回调函数
        """
        pass
    
    @abstractmethod
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        pass
```

## 3. 服务接口

### 3.1 系统信息服务接口 (SystemServiceInterface)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.system_info import SystemInfo

class SystemServiceInterface(ABC):
    """系统信息服务抽象接口"""
    
    @abstractmethod
    async def save_system_info(self, system_info: SystemInfo) -> None:
        """保存系统信息
        
        Args:
            system_info: SystemInfo对象
        """
        pass
    
    @abstractmethod
    async def get_all_system_info(self) -> List[Dict[str, Any]]:
        """获取所有系统信息
        
        Returns:
            系统信息列表
        """
        pass
    
    @abstractmethod
    async def get_system_info_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """根据MAC地址获取系统信息
        
        Args:
            mac_address: MAC地址
            
        Returns:
            系统信息字典
        """
        pass
    
    @abstractmethod
    async def get_online_status(self, mac_address: str) -> bool:
        """获取设备在线状态
        
        Args:
            mac_address: MAC地址
            
        Returns:
            在线状态
        """
        pass
```

### 3.2 设备管理服务接口 (DeviceServiceInterface)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class DeviceServiceInterface(ABC):
    """设备管理服务抽象接口"""
    
    @abstractmethod
    async def add_switch(self, switch_config: Dict[str, Any]) -> bool:
        """添加交换机配置
        
        Args:
            switch_config: 交换机配置信息
            
        Returns:
            添加是否成功
        """
        pass
    
    @abstractmethod
    async def get_all_switches(self) -> List[Dict[str, Any]]:
        """获取所有交换机配置
        
        Returns:
            交换机配置列表
        """
        pass
    
    @abstractmethod
    async def update_switch(self, ip: str, switch_config: Dict[str, Any]) -> bool:
        """更新交换机配置
        
        Args:
            ip: 交换机IP地址
            switch_config: 交换机配置信息
            
        Returns:
            更新是否成功
        """
        pass
    
    @abstractmethod
    async def delete_switch(self, ip: str) -> bool:
        """删除交换机配置
        
        Args:
            ip: 交换机IP地址
            
        Returns:
            删除是否成功
        """
        pass
```

## 4. 工具接口

### 4.1 日志接口 (LoggerInterface)

```python
from abc import ABC, abstractmethod
from typing import Any

class LoggerInterface(ABC):
    """日志记录抽象接口"""
    
    @abstractmethod
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录调试信息"""
        pass
    
    @abstractmethod
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录一般信息"""
        pass
    
    @abstractmethod
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录警告信息"""
        pass
    
    @abstractmethod
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录错误信息"""
        pass
    
    @abstractmethod
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """记录严重错误信息"""
        pass
```

## 5. 异常接口

### 5.1 基础异常类

```python
class BaseException(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self.cause = cause
    
    def __str__(self) -> str:
        if self.cause:
            return f"{super().__str__()} (cause: {str(self.cause)})"
        return super().__str__()

class DatabaseException(BaseException):
    """数据库异常类"""
    pass

class NetworkException(BaseException):
    """网络异常类"""
    pass

class ConfigurationException(BaseException):
    """配置异常类"""
    pass
```

## 6. 接口使用规范

### 6.1 依赖注入
所有接口实现都应通过依赖注入容器进行管理，避免直接实例化具体实现类。

### 6.2 异常处理
接口方法应明确定义可能抛出的异常类型，调用方应正确处理这些异常。

### 6.3 异步支持
对于I/O密集型操作，接口应提供异步方法，并保持与同步方法的兼容性。

### 6.4 文档注释
所有接口方法都应包含详细的文档注释，说明参数、返回值和异常信息。