# 华为交换机SNMP监控系统

## 项目概述

本项目是一个专门用于监控华为交换机的SNMP管理系统，支持通过SNMPv3协议获取设备的系统信息、接口状态、CPU使用率、内存使用情况和温度等关键监控指标。

## 功能特性

1. **系统信息获取**
   - 设备型号和描述
   - 系统运行时间
   - 系统名称

2. **网络接口监控**
   - 接口数量统计

3. **性能监控**
   - CPU使用率
   - 内存使用情况
   - 设备温度

4. **持续监控**
   - 实时监控设备状态
   - 定期刷新监控数据

## 技术特点

- 支持SNMPv3协议（authNoPriv安全级别）
- 支持MD5和SHA认证协议
- 使用异步编程提高性能
- 自动实体索引发现机制
- 错误处理和日志记录
- 易于扩展的模块化设计

## 认证协议支持

项目现在支持MD5和SHA两种认证协议，其中SHA认证协议提供更高的安全性。详细信息请参阅 [SHA_AUTH_SUPPORT.md](docs/SHA_AUTH_SUPPORT.md)。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基本测试

运行基本功能测试：

```bash
cd server/src
python final_test.py
```

### 2. 持续监控

启动持续监控（默认30秒刷新一次）：

```bash
cd server/src
python continuous_monitor.py
```

持续监控脚本会定期获取设备的系统信息、CPU使用率、内存使用情况和接口流量等关键监控指标，并在控制台显示。

### 3. 配置修改

在脚本中修改以下SNMP配置参数以匹配您的设备：

```python
snmp_config = {
    'ip': '192.168.43.195',      # 设备IP地址
    'snmp_version': 'v3',        # SNMP版本
    'user': 'your_username',     # SNMP用户名
    'auth_key': 'your_auth_key', # 认证密钥
    'auth_protocol': 'sha'       # 认证协议 ('md5' 或 'sha')
}
```

默认使用MD5认证协议，如果需要使用SHA认证协议，请将`auth_protocol`设置为`sha`。

## 项目结构

```
net-manager/
├── server/
│   └── src/
│       ├── snmp/
│       │   ├── __init__.py       # SNMP模块初始化文件
│       │   ├── snmp_monitor.py   # 核心SNMP监控类
│       │   ├── oid_classifier.py # OID分类和识别工具
│       │   ├── manager.py        # 高级管理接口
│       │   ├── example.py        # 使用示例
│       │   └── test_sha_auth.py  # SHA认证测试脚本
│       ├── continuous_monitor.py # 持续监控脚本
│       ├── final_test.py        # 功能测试脚本
│       └── snmp_manager.py      # 核心SNMP管理类（向后兼容）
├── requirements.txt              # 项目依赖
└── README.md                    # 项目说明文档
```

## 核心类说明

### HuaWeiSwitchSNMPManager

主要的SNMP管理类，提供以下方法：

- `get_system_info()`: 获取系统信息
- `get_interface_count()`: 获取接口数量
- `get_cpu_usage()`: 获取CPU使用率
- `get_memory_usage()`: 获取内存使用情况
- `get_temperature_info()`: 获取温度信息
- `get_all_monitoring_data()`: 获取所有监控数据

## 故障排除

### 1. 连接问题

确保以下几点：
- 设备IP地址正确
- SNMP服务已在设备上启用
- 用户名和认证密钥正确
- 网络连接正常

### 2. 权限问题

确保SNMP用户具有足够的权限访问所需OID。

### 3. OID不匹配

如果获取不到数据，可能是设备型号不同导致OID有所差异，需要根据具体设备调整OID配置。

## 扩展开发

可以通过以下方式扩展功能：

1. 添加更多监控指标
2. 实现数据持久化存储
3. 添加告警功能
4. 开发Web界面
5. 支持更多厂商设备

## 许可证

本项目仅供学习和参考使用。