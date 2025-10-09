# Net Manager Server 模块化设计说明

## 1. 设计原则

### 1.1 单一职责原则 (SRP)
每个模块只负责一个特定的功能领域，确保模块功能单一、职责清晰。

### 1.2 依赖倒置原则 (DIP)
高层模块不依赖低层模块，两者都依赖抽象。通过接口和抽象类定义依赖关系，使用依赖注入降低耦合度。

### 1.3 开闭原则 (OCP)
模块对扩展开放，对修改关闭。通过继承和多态支持功能扩展，使用配置和插件机制支持定制。

## 2. 模块详细设计

### 2.1 核心模块 (core)

#### 2.1.1 应用程序主入口 (application.py)
- 负责应用程序的启动、运行和关闭
- 协调各模块的初始化和生命周期管理
- 提供统一的应用程序控制接口

#### 2.1.2 配置管理器 (config_manager.py)
- 集中管理所有配置项
- 支持多种配置源（文件、环境变量、命令行参数）
- 支持配置的运行时动态更新
- 提供配置变更通知机制

#### 2.1.3 依赖注入容器 (di_container.py)
- 管理对象的创建和生命周期
- 实现依赖注入功能
- 支持单例模式和原型模式
- 提供服务定位功能

### 2.2 数据模型模块 (models)

#### 2.2.1 系统信息模型 (system_info.py)
- 定义系统信息数据结构
- 提供数据验证和转换方法
- 支持序列化和反序列化

#### 2.2.2 设备模型 (device.py)
- 定义设备数据结构
- 提供设备状态管理
- 支持设备类型识别

#### 2.2.3 交换机模型 (switch.py)
- 定义交换机数据结构
- 提供SNMP配置管理
- 支持交换机状态监控

### 2.3 数据库模块 (database)

#### 2.3.1 数据库接口 (interfaces/database_interface.py)
- 定义数据库操作的抽象接口
- 包含系统信息和设备管理方法
- 提供同步和异步操作接口

#### 2.3.2 SQLite实现 (implementations/sqlite_database.py)
- SQLite数据库的具体实现
- 实现数据库接口定义的方法
- 提供线程安全的数据库访问

#### 2.3.3 数据库工厂 (factories/database_factory.py)
- 根据配置创建数据库实例
- 支持多种数据库后端扩展
- 提供数据库实例管理

### 2.4 网络通信模块 (network)

#### 2.4.1 TCP服务器 (tcp/tcp_server.py)
- 实现TCP长连接服务
- 处理客户端连接和数据接收
- 支持多客户端并发处理

#### 2.4.2 UDP服务器 (udp/udp_server.py)
- 实现UDP服务发现功能
- 处理广播和组播消息
- 提供轻量级通信机制

#### 2.4.3 API服务 (api/api_server.py)
- 基于Tornado的RESTful API服务
- 提供系统信息查询接口
- 支持CORS和认证机制

#### 2.4.4 SNMP监控 (snmp/)
- SNMP设备监控功能
- 支持多种SNMP版本
- 提供OID分类和识别功能

### 2.5 业务服务模块 (services)

#### 2.5.1 系统信息服务 (system_service.py)
- 处理系统信息相关的业务逻辑
- 协调数据模型和数据库操作
- 提供系统信息查询和管理功能

#### 2.5.2 设备管理服务 (device_service.py)
- 处理设备管理相关的业务逻辑
- 提供设备注册、查询和配置功能
- 支持设备状态监控

#### 2.5.3 监控服务 (monitor_service.py)
- 协调各种监控任务
- 提供定时任务调度
- 支持监控数据收集和分析

### 2.6 工具类模块 (utils)

#### 2.6.1 日志工具 (logger.py)
- 提供统一的日志记录接口
- 支持多种日志输出格式
- 实现日志级别动态调整

#### 2.6.2 数据验证工具 (validators.py)
- 提供数据验证功能
- 支持常见数据类型验证
- 提供自定义验证规则

#### 2.6.3 辅助函数 (helpers.py)
- 提供常用的辅助函数
- 包括字符串处理、数据转换等
- 支持跨模块复用

### 2.7 异常类模块 (exceptions)

#### 2.7.1 基础异常类 (base_exceptions.py)
- 定义系统基础异常类
- 提供统一的异常处理机制
- 支持异常链和上下文信息

#### 2.7.2 数据库异常 (database_exceptions.py)
- 定义数据库相关异常
- 包括连接、查询、事务等异常
- 提供详细的错误信息

#### 2.7.3 网络异常 (network_exceptions.py)
- 定义网络通信相关异常
- 包括连接、超时、协议等异常
- 提供网络错误诊断信息

## 3. 模块间依赖关系

```
+----------------+     +----------------+     +----------------+
|   core模块     |---->|   utils模块    |---->| exceptions模块 |
+----------------+     +----------------+     +----------------+
       |                       |
       |                       |
       v                       v
+----------------+     +----------------+
|   models模块   |     |  database模块  |
+----------------+     +----------------+
       |                       |
       |                       |
       v                       v
+----------------+     +----------------+
|  services模块  |<----|  network模块   |
+----------------+     +----------------+
```

## 4. 接口设计

### 4.1 数据库接口
```python
class DatabaseInterface(ABC):
    @abstractmethod
    async def save_system_info(self, system_info: SystemInfo) -> None:
        pass
    
    @abstractmethod
    async def get_all_system_info(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_system_info_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        pass
```

### 4.2 网络服务接口
```python
class NetworkServerInterface(ABC):
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        pass
```

## 5. 配置驱动设计

所有配置项通过`config_manager.py`集中管理，支持：
- 环境变量覆盖配置
- 运行时配置更新
- 配置变更通知机制

## 6. 异步处理设计

- 数据库操作支持异步接口
- 网络通信使用异步IO
- 多线程任务处理CPU密集型操作