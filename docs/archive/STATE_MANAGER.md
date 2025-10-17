# 客户端状态管理器使用说明

## 概述

状态管理器 (`state_manager.py`) 是一个用于统一管理客户端状态的模块，包括客户端ID的存储和读取。它采用单例模式设计，确保在整个应用程序中只有一个状态管理器实例。

## 主要功能

1. **客户端ID管理**：自动生成并持久化客户端唯一标识符
2. **状态存储**：提供键值对形式的状态存储功能
3. **状态持久化**：自动将状态保存到JSON文件中
4. **线程安全**：支持多线程环境下的安全访问

## 使用方法

### 1. 获取状态管理器实例

```python
from src.state_manager import get_state_manager

# 获取全局状态管理器实例
state_manager = get_state_manager()
```

### 2. 获取客户端ID

```python
# 获取客户端唯一标识符
client_id = state_manager.get_client_id()
```

### 3. 设置和获取状态

```python
# 设置状态值
state_manager.set_state("key", "value")

# 获取状态值
value = state_manager.get_state("key", "default_value")
```

### 4. 批量更新状态

```python
# 批量更新多个状态值
state_manager.update_client_state({
    "status": "active",
    "version": "1.0.0",
    "last_update": "2025-10-05"
})
```

## 文件说明

- `client_state.json`：存储客户端状态的JSON文件，包括客户端唯一标识符和其他状态信息

## 注意事项

1. 状态管理器采用单例模式，多次调用 `get_state_manager()` 将返回同一个实例
2. 状态变更会自动保存到文件中
3. 客户端ID在首次运行时自动生成，并持久化存储