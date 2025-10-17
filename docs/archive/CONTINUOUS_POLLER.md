# SNMP 持续轮询器文档

## 概述

SNMP持续轮询器（`SNMPContinuousPoller`）是一个后台服务，用于定期从数据库获取所有交换机配置信息，并通过SNMP协议获取每个交换机的设备信息。

## 功能特性

- ✅ **自动轮询**：定期从数据库读取交换机配置并获取设备信息
- ✅ **并发处理**：支持并发轮询多个设备，可配置最大并发数
- ✅ **多版本支持**：支持SNMP v1、v2c、v3所有版本
- ✅ **异步架构**：基于asyncio实现，高效利用系统资源
- ✅ **线程安全**：在独立线程中运行，不影响主程序
- ✅ **可扩展性**：提供回调机制，方便自定义处理逻辑
- ✅ **优雅退出**：支持安全停止，正确释放资源

## 工作流程

```
启动轮询器
    ↓
等待轮询间隔
    ↓
从数据库获取所有交换机配置
    ↓
并发轮询每个交换机（限制并发数）
    ↓
获取设备信息（名称、描述、运行时间等）
    ↓
调用回调函数处理设备信息
    ↓
记录日志和统计信息
    ↓
返回等待下一次轮询
```

## 快速开始

### 1. 在项目启动时自动启动

轮询器已集成到 `main.py` 中，服务端启动时会自动启动：

```python
# 在 main.py 中已自动配置
from src.snmp.continuous_poller import start_snmp_poller

# 启动轮询器（60秒轮询一次，最多10个并发）
start_snmp_poller(switch_manager, poll_interval=60, max_workers=10)
```

### 2. 手动使用轮询器

```python
from src.database.managers.switch_manager import SwitchManager
from src.snmp.continuous_poller import SNMPContinuousPoller

# 创建交换机管理器
switch_manager = SwitchManager()

# 创建轮询器实例
poller = SNMPContinuousPoller(
    switch_manager=switch_manager,
    poll_interval=60,  # 每60秒轮询一次
    max_workers=10,    # 最多10个并发任务
)

# 启动轮询器
poller.start()

# ... 程序运行 ...

# 停止轮询器
poller.stop()
```

### 3. 使用全局函数

```python
from src.database.managers.switch_manager import SwitchManager
from src.snmp.continuous_poller import start_snmp_poller, stop_snmp_poller

# 创建交换机管理器
switch_manager = SwitchManager()

# 启动全局轮询器
poller = start_snmp_poller(switch_manager, poll_interval=60, max_workers=10)

# ... 程序运行 ...

# 停止全局轮询器
stop_snmp_poller()
```

## 配置参数

### SNMPContinuousPoller 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `switch_manager` | SwitchManager | 必需 | 交换机管理器实例 |
| `poll_interval` | int | 60 | 轮询间隔（秒） |
| `max_workers` | int | 10 | 最大并发工作数 |

### 性能建议

- **轮询间隔**：
  - 小型网络（<50设备）：30-60秒
  - 中型网络（50-200设备）：60-120秒
  - 大型网络（>200设备）：120-300秒

- **并发数**：
  - 根据网络带宽和设备响应速度调整
  - 建议范围：5-20
  - 过高可能导致网络拥塞或SNMP超时

## 自定义回调

通过继承 `SNMPContinuousPoller` 并重写 `_on_device_info_received` 方法来实现自定义处理：

```python
from src.snmp.continuous_poller import SNMPContinuousPoller

class CustomSNMPPoller(SNMPContinuousPoller):
    """自定义SNMP轮询器"""
    
    def _on_device_info_received(self, device_data):
        """自定义设备信息接收回调"""
        ip = device_data.get("ip")
        
        if "error" in device_data:
            # 处理错误
            self._handle_error(device_data)
        else:
            # 处理成功
            self._process_device_info(device_data)
    
    def _handle_error(self, device_data):
        """处理错误情况"""
        # 发送告警、记录日志等
        pass
    
    def _process_device_info(self, device_data):
        """处理设备信息"""
        # 更新缓存、发送WebSocket通知等
        pass
```

### 回调数据格式

成功时的 `device_data` 格式：

```python
{
    "ip": "192.168.1.1",
    "switch_id": 1,
    "snmp_version": "v2c",
    "device_info": {
        "name": "Switch-Core-01",
        "description": "Cisco IOS Software...",
        "location": "Building A, Floor 3",
        "uptime": "123456789",
        "object_id": "1.3.6.1.4.1.9.1.516"
    },
    "poll_time": 1634567890.123
}
```

失败时的 `device_data` 格式：

```python
{
    "ip": "192.168.1.1",
    "switch_id": 1,
    "error": "连接超时",
    "poll_time": 1634567890.123
}
```

## 日志输出

轮询器会输出以下日志：

```
INFO: SNMP轮询器已启动，轮询间隔: 60秒
INFO: SNMP轮询循环已启动
INFO: 开始轮询 10 个交换机设备
DEBUG: 成功获取设备信息: IP=192.168.1.1, 名称=Switch-Core-01, 版本=v2c
ERROR: 轮询交换机失败: IP=192.168.1.2, 错误=连接超时
INFO: 轮询完成: 成功 8 个, 失败 2 个
```

## 使用示例

查看 `continuous_poller_example.py` 获取完整的使用示例：

```bash
cd server/src/snmp
python continuous_poller_example.py
```

示例包括：
1. 使用类方式创建轮询器
2. 使用全局函数方式管理轮询器
3. 使用自定义回调

## 注意事项

### 1. 数据库连接

- 轮询器使用同步方式访问数据库（`get_all_switches()`）
- 确保数据库连接池有足够的连接数

### 2. SNMP超时

- 默认SNMP超时时间为2秒
- 网络不稳定时可能需要增加超时时间
- 在 `SNMPMonitor._get_snmp_v2c` 中配置：`timeout=2.0, retries=3`

### 3. 内存使用

- 并发数越高，内存占用越大
- 建议根据实际情况调整 `max_workers`

### 4. 线程安全

- 轮询器在独立线程中运行
- 回调函数中的操作需要考虑线程安全

## 集成建议

### 1. WebSocket通知

在 `_on_device_info_received` 中发送实时更新：

```python
def _on_device_info_received(self, device_data):
    # 通过WebSocket发送设备状态更新
    from src.network.api.websocket_handler import broadcast_message
    broadcast_message({
        "type": "device_update",
        "data": device_data
    })
```

### 2. 缓存更新

使用Redis或内存缓存存储最新设备信息：

```python
def _on_device_info_received(self, device_data):
    # 更新Redis缓存
    import redis
    r = redis.Redis()
    r.set(f"device:{device_data['ip']}", json.dumps(device_data))
```

### 3. 告警触发

基于设备状态触发告警：

```python
def _on_device_info_received(self, device_data):
    if "error" in device_data:
        # 发送告警
        send_alert(f"设备 {device_data['ip']} 无法访问")
```

## 故障排查

### 问题1：轮询器不工作

**检查项**：
- 确认数据库中有交换机配置数据
- 检查日志输出是否有错误信息
- 验证 `switch_manager` 实例是否正确初始化

### 问题2：SNMP超时

**解决方案**：
- 检查网络连接
- 验证SNMP配置（版本、community等）
- 增加轮询间隔或减少并发数

### 问题3：内存占用过高

**解决方案**：
- 减少 `max_workers` 数量
- 增加 `poll_interval` 间隔
- 检查是否有内存泄漏

## API参考

### SNMPContinuousPoller

#### 方法

- `start()`: 启动轮询器
- `stop()`: 停止轮询器
- `is_running`: 属性，检查轮询器是否正在运行

#### 内部方法（可重写）

- `_on_device_info_received(device_data)`: 设备信息接收回调

### 全局函数

- `start_snmp_poller(switch_manager, poll_interval, max_workers)`: 启动全局轮询器
- `stop_snmp_poller()`: 停止全局轮询器
- `get_snmp_poller()`: 获取全局轮询器实例

## 更新日志

### v1.0.0 (2025-10-17)
- ✅ 初始版本发布
- ✅ 支持基本的轮询功能
- ✅ 支持SNMP v1/v2c/v3
- ✅ 并发控制
- ✅ 可自定义回调

## 许可证

该模块遵循项目整体许可证。
