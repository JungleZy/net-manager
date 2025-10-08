# SNMP v3 SHA认证协议支持说明

## 概述

本文档详细说明了项目对SNMP v3 SHA认证协议的支持情况，包括实现细节、使用方法和测试验证。

## 实现细节

### 1. pysnmp库支持

项目使用的pysnmp库版本(>=7.1.21)已支持SHA认证协议，通过`usmHMACSHAAuthProtocol`常量标识。

### 2. 代码实现

在`snmp_monitor.py`文件中，我们对以下方法进行了修改以支持SHA认证协议：

1. `_get_snmp_v3_auth`方法：
   - 添加了`auth_protocol`参数，默认值为'md5'
   - 根据参数值选择认证协议：
     - 'sha'对应`usmHMACSHAAuthProtocol`
     - 其他值对应`usmHMACMD5AuthProtocol`

2. `_get_snmp_v3_privacy`方法：
   - 添加了`auth_protocol`参数，默认值为'md5'
   - 实现了与`_get_snmp_v3_auth`方法相同的协议选择逻辑

3. `get_data`方法：
   - 添加了`auth_protocol`参数的处理
   - 将该参数传递给相应的v3认证方法

### 3. 向后兼容性

为了保持向后兼容性，所有新增的`auth_protocol`参数都设置了默认值'md5'，确保现有代码无需修改即可继续工作。

## 使用方法

### 1. 配置参数

在使用SNMP v3时，可以通过`auth_protocol`参数指定认证协议：

```python
# 使用SHA认证协议
snmp_manager = HuaWeiSwitchSNMPManager(
    ip="192.168.43.195",
    snmp_version="v3",
    user="wjkjv3user",
    auth_key="Wjkj6912",
    auth_protocol="sha"  # 指定使用SHA认证协议
)

# 使用MD5认证协议（默认）
snmp_manager = HuaWeiSwitchSNMPManager(
    ip="192.168.43.195",
    snmp_version="v3",
    user="wjkjv3user",
    auth_key="Wjkj6912",
    auth_protocol="md5"  # 或者省略此参数
)
```

### 2. 测试脚本

项目提供了`test_sha_auth.py`测试脚本来验证SHA和MD5认证协议的功能：

```bash
cd server/src/snmp
python test_sha_auth.py
```

## 路由器端配置

为了使用SHA认证协议，需要在路由器上进行相应配置：

```
# 配置认证密钥（SHA算法）
[HUAWEI] snmp-agent usm-user v3 wjkjv3user authentication-mode sha Wjkj6912
```

## 测试验证

### 1. 功能测试

通过`test_sha_auth.py`脚本验证了SHA和MD5认证协议的功能，测试结果显示两种协议均能正常工作。

### 2. 兼容性测试

通过`continuous_monitor.py`脚本验证了持续监控功能，确认SHA认证协议能够正常获取设备数据。

## 注意事项

1. 确保路由器端正确配置了SHA认证密钥
2. 客户端和路由器端的认证协议必须保持一致
3. 如果遇到认证错误，请检查用户名、认证密钥和认证协议是否正确配置