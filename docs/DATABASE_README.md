# 数据库模块说明

## 模块结构

```
database/
├── __init__.py                 # 数据库模块入口，保持向后兼容性
├── database_manager.py         # 旧版数据库管理器（已重构，保持向后兼容）
├── db_exceptions.py            # 数据库异常定义
└── managers/                   # 新的数据库管理器模块
    ├── __init__.py             # 管理器模块入口
    ├── base_manager.py         # 基础数据库管理器
    ├── database_manager.py     # 统一数据库管理器接口
    ├── device_manager.py       # 设备信息管理器
    └── switch_manager.py       # 交换机信息管理器
```

## 模块功能

### BaseDatabaseManager (base_manager.py)
- 提供基础的数据库连接管理功能
- 实现线程安全的数据库访问机制
- 提供数据库连接上下文管理器

### DeviceManager (device_manager.py)
- 管理设备信息表 (devices_info)
- 提供设备的增删改查操作
- 处理设备相关的业务逻辑

### SwitchManager (switch_manager.py)
- 管理交换机配置表 (switch_info)
- 提供交换机配置的增删改查操作
- 处理交换机相关的业务逻辑

### DatabaseManager (managers/database_manager.py)
- 统一的数据库管理器接口
- 组合其他管理器提供完整功能
- 保持与旧版API的兼容性

## 使用方法

### 新项目推荐用法

```python
from src.database.managers import BaseDatabaseManager, DeviceManager, SwitchManager

# 创建设备管理器
device_manager = DeviceManager("database.db")
# 创建交换机管理器
switch_manager = SwitchManager("database.db")

# 使用设备管理器操作设备信息
device_manager.save_system_info(system_info)
devices = device_manager.get_all_system_info()

# 使用交换机管理器操作交换机配置
switch_manager.add_switch(switch_info)
switches = switch_manager.get_all_switches()
```

### 向后兼容用法

```python
from src.database import DatabaseManager

# 创建数据库管理器（兼容旧版API）
db_manager = DatabaseManager("database.db")

# 使用统一接口操作所有功能
db_manager.save_system_info(system_info)
db_manager.add_switch(switch_info)
```

## 数据库表结构

### device_info（设备信息表）
```sql
CREATE TABLE IF NOT EXISTS device_info (
    id TEXT PRIMARY KEY,
    client_id TEXT,
    hostname TEXT,
    os_name TEXT,
    os_version TEXT,
    os_architecture TEXT,
    machine_type TEXT,
    services TEXT,
    processes TEXT,
    networks TEXT,
    cpu_info TEXT,
    memory_info TEXT,
    disk_info TEXT,
    type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### switch_info（交换机配置表）
```sql
CREATE TABLE IF NOT EXISTS switch_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL UNIQUE,
    snmp_version TEXT NOT NULL,
    community TEXT,
    user TEXT,
    auth_key TEXT,
    auth_protocol TEXT,
    priv_key TEXT,
    priv_protocol TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## 异常处理

数据库模块定义了以下异常类型：

- `DatabaseError`: 数据库基础异常
- `DatabaseConnectionError`: 数据库连接异常
- `DatabaseInitializationError`: 数据库初始化异常
- `DatabaseQueryError`: 数据库查询异常
- `DeviceNotFoundError`: 设备未找到异常
- `DeviceAlreadyExistsError`: 设备已存在异常

使用时应捕获相应的异常类型以进行正确的错误处理。