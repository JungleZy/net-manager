# SNMP 监控模块

## 概述

本模块提供了完整的 SNMP 监控功能，支持 SNMP v1、v2c 和 v3 版本，具备以下特性：

1. 支持 SNMP v1、v2c、v3 版本
2. SNMP v3 支持三种安全级别：privacy、authentication、noauthentication
3. 智能 OID 分类和识别
4. 获取设备信息、CPU 占用率、内存占用率、网口上传下载流量等信息

## 模块结构

- `snmp_monitor.py`: 核心 SNMP 监控类
- `oid_classifier.py`: OID 分类和识别工具
- `manager.py`: 高级管理接口，整合监控和分类功能

## 安装依赖

项目已包含所需依赖：
- pysnmp>=7.1.21
- pysmi>=1.6.2

## 使用方法

### 1. 基本使用

```python
from src.snmp.manager import SNMPManager
import asyncio

async def main():
    # 创建SNMP管理器
    manager = SNMPManager()
    
    # 设备信息
    ip = "192.168.43.195"
    version = "v3"
    
    # 获取设备概览
    device_info = await manager.get_device_overview(
        ip, version,
        user="wjkjv3user",
        auth_key="Wjkj6912"
    )
    
    print("设备信息:", device_info)

# 运行
asyncio.run(main())
```

### 2. SNMP v1/v2c 使用

```python
# SNMP v1
data, success = await manager.monitor.get_data(
    ip, "v1", "1.3.6.1.2.1.1.1.0",
    community="public"
)

# SNMP v2c
data, success = await manager.monitor.get_data(
    ip, "v2c", "1.3.6.1.2.1.1.1.0",
    community="public"
)
```

### 3. SNMP v3 不同安全级别

```python
# 无认证无加密
data, success = await manager.monitor.get_data(
    ip, "v3", "1.3.6.1.2.1.1.1.0",
    user="username"
)

# 认证无加密
data, success = await manager.monitor.get_data(
    ip, "v3", "1.3.6.1.2.1.1.1.0",
    user="username",
    auth_key="auth_password"
)

# 认证并加密
data, success = await manager.monitor.get_data(
    ip, "v3", "1.3.6.1.2.1.1.1.0",
    user="username",
    auth_key="auth_password",
    priv_key="priv_password"
)
```

### 4. 获取特定信息

```python
# 获取CPU使用率
cpu_info = await manager.get_cpu_usage(
    ip, version,
    user="wjkjv3user",
    auth_key="Wjkj6912"
)

# 获取内存使用率
memory_info = await manager.get_memory_usage(
    ip, version,
    user="wjkjv3user",
    auth_key="Wjkj6912"
)

# 获取接口统计信息
interface_stats = await manager.get_interface_statistics(
    ip, version,
    user="wjkjv3user",
    auth_key="Wjkj6912"
)
```

## 测试

运行测试用例：

```bash
cd server
python -m unittest tests.test_snmp_monitor
```

## API 参考

### SNMPManager 类

#### `get_device_overview(ip, version, **kwargs)`
获取设备概览信息

#### `get_cpu_usage(ip, version, **kwargs)`
获取CPU使用率

#### `get_memory_usage(ip, version, **kwargs)`
获取内存使用率

#### `get_interface_statistics(ip, version, **kwargs)`
获取接口统计信息

#### `get_custom_oids(ip, version, oids, **kwargs)`
批量获取自定义OID数据

#### `scan_network_devices(ip_list, version, **kwargs)`
扫描多个网络设备

### SNMPMonitor 类

#### `get_data(ip, version, oid, **kwargs)`
根据SNMP版本获取指定OID的数据

### OIDClassifier 类

#### `classify_oid(oid)`
对OID进行分类

#### `get_oid_name(oid)`
获取OID的名称

#### `parse_oid_value(oid, value)`
解析OID值

#### `identify_device_type(sys_object_id)`
识别设备类型