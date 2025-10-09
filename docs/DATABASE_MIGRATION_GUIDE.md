# 数据库模块迁移指南

本文档旨在帮助开发者从旧版数据库模块迁移到新版模块。

## 重构背景

为了提高代码的可维护性和可扩展性，我们将原有的单一数据库管理器文件重构为多个专门的管理器类：

1. **BaseDatabaseManager**: 提供基础的数据库连接和线程安全访问
2. **DeviceManager**: 专门处理设备信息管理
3. **SwitchManager**: 专门处理交换机配置管理
4. **DatabaseManager**: 统一接口，保持向后兼容性

## 模块结构变化

### 旧结构
```
database/
├── __init__.py
├── database_manager.py  # 包含所有功能的单一文件
└── db_exceptions.py
```

### 新结构
```
database/
├── __init__.py                 # 保持向后兼容性
├── database_manager.py         # 旧版接口（已重构，保持向后兼容）
├── db_exceptions.py            # 数据库异常定义
└── managers/                   # 新的数据库管理器模块
    ├── __init__.py             # 管理器模块入口
    ├── base_manager.py         # 基础数据库管理器
    ├── database_manager.py     # 统一数据库管理器接口
    ├── device_manager.py       # 设备信息管理器
    └── switch_manager.py       # 交换机信息管理器
```

## 迁移指南

### 1. 向后兼容用法（无需修改代码）

如果你使用的是以下导入方式，代码无需修改：

```python
from src.database import DatabaseManager

# 创建数据库管理器
db_manager = DatabaseManager("database.db")

# 使用统一接口操作所有功能
db_manager.save_system_info(system_info)
db_manager.add_switch(switch_info)
```

### 2. 推荐用法（新项目或重构项目）

对于新项目或准备重构的项目，建议使用新的模块结构：

```python
# 导入新的管理器类
from src.database.managers import DeviceManager, SwitchManager

# 创建专门的管理器实例
device_manager = DeviceManager("database.db")
switch_manager = SwitchManager("database.db")

# 使用专门的管理器操作对应功能
device_manager.save_system_info(system_info)
switch_manager.add_switch(switch_info)
```

### 3. 模块级导入（推荐）

你也可以直接从 managers 模块导入：

```python
from src.database.managers.device_manager import DeviceManager
from src.database.managers.switch_manager import SwitchManager
from src.database.managers.database_manager import DatabaseManager
```

## API 变化

### DatabaseManager 类

统一数据库管理器类现在作为组合模式的实现，内部使用专门的管理器：

```python
class DatabaseManager:
    def __init__(self, db_path: str = "net_manager_server.db"):
        self.base_manager = BaseDatabaseManager(db_path)
        self.device_manager = DeviceManager(db_path)
        self.switch_manager = SwitchManager(db_path)
    
    # 设备管理方法委托给 DeviceManager
    def save_system_info(self, system_info: SystemInfo) -> None:
        return self.device_manager.save_system_info(system_info)
    
    # 交换机管理方法委托给 SwitchManager
    def add_switch(self, switch_info: SwitchInfo) -> Tuple[bool, str]:
        return self.switch_manager.add_switch(switch_info)
```

## 注意事项

1. **导入路径**: 新的管理器类位于 `src.database.managers` 包中
2. **向后兼容性**: 旧的导入方式仍然可以工作，但建议使用新的结构
3. **性能**: 新的结构提供了更好的模块化，有助于减少不必要的导入
4. **维护性**: 专门的管理器使代码更容易维护和扩展

## 常见问题

### Q: 我需要修改现有代码吗？
A: 如果你使用的是 `from src.database import DatabaseManager` 的方式导入，无需修改代码。

### Q: 新的结构有什么优势？
A: 新结构提供了更好的模块化、可维护性和可扩展性，每个管理器只关注特定的功能。

### Q: 异常处理有变化吗？
A: 异常类保持不变，仍然可以从 `src.database` 导入。

## 示例代码

### 旧代码
```python
from src.database import DatabaseManager

db_manager = DatabaseManager("database.db")
db_manager.save_system_info(system_info)
```

### 新代码（推荐）
```python
from src.database.managers import DeviceManager

device_manager = DeviceManager("database.db")
device_manager.save_system_info(system_info)
```

通过以上迁移，你可以更好地利用新架构的优势，同时保持与现有代码的兼容性。