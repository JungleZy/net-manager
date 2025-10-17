# SNMPManager 统一API使用指南

## 📋 概述

[SNMPManager](file://e:\workspace\project\net-manager\server\src\snmp\manager.py) 现已集成统一轮询器管理功能，提供一站式 SNMP 监控服务。

## 🎯 核心功能

### 1. 统一启动轮询器

通过 [start_pollers()](file://e:\workspace\project\net-manager\server\src\snmp\manager.py#L553-L628) 方法一次性启动设备和接口轮询器。

### 2. 统一停止轮询器

通过 [stop_pollers()](file://e:\workspace\project\net-manager\server\src\snmp\manager.py#L630-L650) 方法统一停止所有轮询器。

### 3. 统计信息查询

通过 [get_poller_statistics()](file://e:\workspace\project\net-manager\server\src\snmp\manager.py#L652-L669) 方法获取轮询器运行状态。

## 🚀 快速开始

### 基本用法

```python
from src.snmp.manager import SNMPManager
from src.database.managers.switch_manager import SwitchManager

# 初始化管理器
switch_manager = SwitchManager()
snmp_manager = SNMPManager()

# 启动轮询器（使用默认配置）
snmp_manager.start_pollers(switch_manager)

# 获取统计信息
stats = snmp_manager.get_poller_statistics()
print(stats)

# 停止轮询器
snmp_manager.stop_pollers()
```

### 自定义配置

```python
# 启动轮询器（自定义配置）
snmp_manager.start_pollers(
    switch_manager,
    # 设备信息轮询配置
    device_poll_interval=10,      # 10秒轮询一次
    device_min_workers=5,          # 最小5个并发
    device_max_workers=20,         # 最大20个并发
    device_timeout=30,             # 超时30秒
    # 接口信息轮询配置
    interface_poll_interval=30,   # 30秒轮询一次
    interface_min_workers=5,       # 最小5个并发
    interface_max_workers=30,      # 最大30个并发
    interface_timeout=60,          # 超时60秒
    # 通用配置
    enable_cache=True,             # 启用缓存
    cache_ttl=300,                 # 缓存5分钟
    dynamic_adjustment=True,       # 启用动态并发调整
)
```

## 📊 API 详解

### [start_pollers()](file://e:\workspace\project\net-manager\server\src\snmp\manager.py#L553-L628)

启动设备和接口轮询器。

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `switch_manager` | SwitchManager | 必需 | 交换机管理器实例 |
| `device_poll_interval` | int | 10 | 设备信息轮询间隔（秒） |
| `device_min_workers` | int | 5 | 设备轮询最小并发数 |
| `device_max_workers` | int | 20 | 设备轮询最大并发数 |
| `device_timeout` | int | 30 | 设备轮询超时时间（秒） |
| `interface_poll_interval` | int | 30 | 接口信息轮询间隔（秒） |
| `interface_min_workers` | int | 5 | 接口轮询最小并发数 |
| `interface_max_workers` | int | 30 | 接口轮询最大并发数 |
| `interface_timeout` | int | 60 | 接口轮询超时时间（秒） |
| `enable_cache` | bool | True | 是否启用缓存 |
| `cache_ttl` | int | 300 | 缓存生存时间（秒） |
| `dynamic_adjustment` | bool | True | 是否启用动态并发调整 |

**返回值：**

```python
(device_poller, interface_poller)  # 两个轮询器实例的元组
```

**使用示例：**

```python
device_poller, interface_poller = snmp_manager.start_pollers(
    switch_manager,
    device_poll_interval=10,
    interface_poll_interval=30,
)
```

### [stop_pollers()](file://e:\workspace\project\net-manager\server\src\snmp\manager.py#L630-L650)

停止所有SNMP轮询器。

**参数：** 无

**返回值：** 无

**使用示例：**

```python
snmp_manager.stop_pollers()
```

### [get_poller_statistics()](file://e:\workspace\project\net-manager\server\src\snmp\manager.py#L652-L669)

获取轮询器统计信息。

**参数：** 无

**返回值：**

```python
{
    "device_poller": {
        "total_polls": 1000,
        "success_count": 950,
        "error_count": 50,
        "avg_response_time": 1.23,
        "queue_size": 5,
        "active_workers": 8,
        "current_concurrency": 10,
        "failed_devices": 2,
        "highly_failed_devices": 1,
        "cached_devices": 45,
        "p95_response_time": 2.5
    },
    "interface_poller": {
        "total_polls": 500,
        "success_count": 480,
        "error_count": 20,
        # ... 类似的统计信息
    }
}
```

**使用示例：**

```python
stats = snmp_manager.get_poller_statistics()

# 查看设备轮询器状态
device_stats = stats["device_poller"]
print(f"成功率: {device_stats['success_count'] / device_stats['total_polls']:.2%}")

# 查看接口轮询器状态
interface_stats = stats["interface_poller"]
print(f"平均响应时间: {interface_stats['avg_response_time']:.2f}s")
```

## 🔄 在 main.py 中的使用

### 完整示例

```python
# main.py

from src.snmp.manager import SNMPManager
from src.database.managers.switch_manager import SwitchManager

def main():
    # ... 其他初始化代码 ...
    
    # 初始化管理器
    switch_manager = SwitchManager()
    snmp_manager = SNMPManager()
    
    # 启动SNMP轮询器（统一管理）
    logger.info("启动SNMP轮询器...")
    snmp_manager.start_pollers(
        switch_manager,
        device_poll_interval=10,      # 设备信息：10秒间隔
        device_min_workers=5,
        device_max_workers=20,
        device_timeout=30,
        interface_poll_interval=30,   # 接口信息：30秒间隔
        interface_min_workers=5,
        interface_max_workers=30,
        interface_timeout=60,
        enable_cache=True,
        cache_ttl=300,
        dynamic_adjustment=True,
    )
    
    logger.info("所有服务已启动完成")
    
    # ... 主循环 ...

def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("接收到终止信号，正在关闭服务端...")
    
    # 停止SNMP轮询器（统一停止）
    try:
        snmp_manager.stop_pollers()
    except Exception as e:
        logger.error(f"停止SNMP轮询器时出错: {e}")
    
    # ... 其他清理代码 ...
```

## 🎯 优势对比

### 旧方式（已废弃）

```python
# 需要分别导入和调用
from src.snmp.unified_poller import (
    start_device_poller,
    start_interface_poller,
    stop_device_poller,
    stop_interface_poller,
)

# 启动设备轮询器
start_device_poller(
    switch_manager,
    poll_interval=10,
    min_workers=5,
    max_workers=20,
    device_timeout=30,
    enable_cache=True,
    cache_ttl=300,
    dynamic_adjustment=True,
)

# 启动接口轮询器
start_interface_poller(
    switch_manager,
    poll_interval=30,
    min_workers=5,
    max_workers=30,
    device_timeout=60,
    enable_cache=True,
    cache_ttl=300,
    dynamic_adjustment=True,
)

# 停止需要分别调用
stop_device_poller()
stop_interface_poller()
```

### 新方式（推荐）

```python
# 只需导入SNMPManager
from src.snmp.manager import SNMPManager

snmp_manager = SNMPManager()

# 一次性启动所有轮询器
snmp_manager.start_pollers(
    switch_manager,
    device_poll_interval=10,
    device_min_workers=5,
    device_max_workers=20,
    device_timeout=30,
    interface_poll_interval=30,
    interface_min_workers=5,
    interface_max_workers=30,
    interface_timeout=60,
    enable_cache=True,
    cache_ttl=300,
    dynamic_adjustment=True,
)

# 一次性停止所有轮询器
snmp_manager.stop_pollers()
```

## ✅ 优势总结

1. **统一管理**：一个对象管理所有SNMP功能
2. **简化调用**：一个方法启动/停止所有轮询器
3. **易于维护**：集中配置，减少代码重复
4. **状态追踪**：内部保存轮询器引用，方便状态查询
5. **错误处理**：统一的异常处理和日志记录
6. **扩展性好**：未来添加新类型轮询器只需扩展此方法

## 📝 配置建议

### 生产环境配置

```python
snmp_manager.start_pollers(
    switch_manager,
    device_poll_interval=10,       # 设备信息10秒轮询
    device_min_workers=5,
    device_max_workers=20,
    device_timeout=30,
    interface_poll_interval=30,    # 接口信息30秒轮询
    interface_min_workers=5,
    interface_max_workers=30,
    interface_timeout=60,
    enable_cache=True,             # 启用缓存减少网络开销
    cache_ttl=300,
    dynamic_adjustment=True,       # 启用动态调整应对负载变化
)
```

### 开发环境配置

```python
snmp_manager.start_pollers(
    switch_manager,
    device_poll_interval=60,       # 较长间隔减少网络压力
    device_min_workers=2,          # 较小并发便于调试
    device_max_workers=5,
    device_timeout=10,
    interface_poll_interval=120,
    interface_min_workers=2,
    interface_max_workers=5,
    interface_timeout=20,
    enable_cache=False,            # 关闭缓存便于测试
    dynamic_adjustment=False,      # 关闭动态调整便于观察
)
```

### 高负载环境配置

```python
snmp_manager.start_pollers(
    switch_manager,
    device_poll_interval=5,        # 更短间隔实现更实时监控
    device_min_workers=10,         # 更高并发处理大量设备
    device_max_workers=50,
    device_timeout=20,
    interface_poll_interval=15,
    interface_min_workers=10,
    interface_max_workers=60,
    interface_timeout=30,
    enable_cache=True,
    cache_ttl=180,                 # 较短TTL保证数据新鲜度
    dynamic_adjustment=True,
)
```

## 🔍 监控和调试

### 查看轮询器状态

```python
import time

# 启动轮询器
snmp_manager.start_pollers(switch_manager)

# 定期检查状态
while True:
    time.sleep(30)
    stats = snmp_manager.get_poller_statistics()
    
    # 设备轮询器
    device_stats = stats["device_poller"]
    if device_stats.get("status") != "not_running":
        success_rate = (
            device_stats["success_count"] / device_stats["total_polls"]
            if device_stats["total_polls"] > 0
            else 0
        )
        print(f"设备轮询器 - 成功率: {success_rate:.2%}, "
              f"并发: {device_stats['current_concurrency']}, "
              f"队列: {device_stats['queue_size']}")
    
    # 接口轮询器
    interface_stats = stats["interface_poller"]
    if interface_stats.get("status") != "not_running":
        success_rate = (
            interface_stats["success_count"] / interface_stats["total_polls"]
            if interface_stats["total_polls"] > 0
            else 0
        )
        print(f"接口轮询器 - 成功率: {success_rate:.2%}, "
              f"并发: {interface_stats['current_concurrency']}, "
              f"队列: {interface_stats['queue_size']}")
```

### 日志输出示例

```
INFO - 启动SNMP统一轮询器...
INFO - 启动SNMP设备轮询器: 间隔10秒, 并发5-20, 超时30秒
INFO - SNMP设备轮询器已启动，轮询间隔: 10秒, 并发范围: 5-20
INFO - 启动SNMP接口轮询器: 间隔30秒, 并发5-30, 超时60秒
INFO - SNMP接口轮询器已启动，轮询间隔: 30秒, 并发范围: 5-30
INFO - 所有SNMP轮询器启动完成
```

## 📚 相关文档

- [统一轮询器实现](unified_poller.py)
- [轮询器合并迁移指南](UNIFIED_POLLER_MIGRATION.md)
- [SNMP监控器](snmp_monitor.py)
- [快进快出队列架构](interface_poller_queue_architecture.md)

---

**版本**: 2.0  
**更新时间**: 2025-10-17  
**状态**: ✅ 生产就绪
