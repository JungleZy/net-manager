# SNMP Manager 使用说明

## 概述

本项目提供了一个用于管理华为交换机的SNMP管理器，支持SNMP v1/v2c和SNMP v3协议。

## 支持的SNMP版本

- SNMP v1
- SNMP v2c
- SNMP v3 (支持noAuthNoPriv, authNoPriv, authPriv三种安全级别)

## SNMP v3配置说明

### 路由器端配置

根据您提供的路由器配置：

```
# 创建v3组（安全名）
[HUAWEI] snmp-agent group v3 managev3group privacy 

# 创建用户并关联组
[HUAWEI] snmp-agent usm-user v3 managev3user managev3group
```

这个配置使用了`privacy`参数，意味着需要同时配置认证和加密密钥。

### 客户端配置

在使用SNMP v3时，需要提供以下参数：

1. `ip`: 设备IP地址
2. `snmp_version`: 设置为"v3"
3. `user`: SNMP v3用户名 (managev3user)
4. `auth_key`: 认证密钥
5. `priv_key`: 隐私(加密)密钥

### 安全级别说明

SNMP v3支持三种安全级别：

1. **noAuthNoPriv**: 无认证无加密
   - 只需要提供用户名
   - 最低安全级别

2. **authNoPriv**: 有认证无加密
   - 需要提供用户名和认证密钥
   - 数据经过认证但不加密

3. **authPriv**: 有认证有加密
   - 需要提供用户名、认证密钥和隐私密钥
   - 数据经过认证和加密
   - 最高安全级别

### 认证和加密算法说明

华为设备支持多种认证和加密算法：

**认证算法：**
- MD5 (较弱，但兼容性好)
- SHA (推荐，更安全)

**加密算法：**
- DES56 (较弱，但兼容性好)
- AES128 (推荐，更安全)

在实际使用中，建议使用SHA+AES128组合以获得更好的安全性。

项目现在支持MD5和SHA两种认证协议，其中SHA认证协议提供更高的安全性。详细信息请参阅 [SHA_AUTH_SUPPORT.md](SHA_AUTH_SUPPORT.md)。

## 使用示例

### SNMP v2c示例

```python
snmp_manager = HuaWeiSwitchSNMPManager(
    ip="192.168.1.1",
    community="public",     # 团体名
    snmp_version="v2c"      # SNMP版本
)
```

### SNMP v3示例 (authNoPriv)

```python
snmp_manager = HuaWeiSwitchSNMPManager(
    ip="192.168.43.195",           # 设备IP地址
    snmp_version="v3",             # 使用SNMP v3
    user="wjkjv3user",             # SNMP v3用户名
    auth_key="Wjkj6912",           # 认证密钥 (不需要隐私密钥)
    auth_protocol="sha"            # 认证协议，支持'md5'或'sha'，默认为'md5'
)
```

### SNMP v3示例 (authNoPriv)

```python
snmp_manager = HuaWeiSwitchSNMPManager(
    ip="192.168.1.1",              # 设备IP地址
    snmp_version="v3",             # 使用SNMP v3
    user="managev3user",           # SNMP v3用户名
    auth_key="your_auth_key"       # 认证密钥 (不需要隐私密钥)
)
```

### SNMP v3示例 (noAuthNoPriv)

```python
snmp_manager = HuaWeiSwitchSNMPManager(
    ip="192.168.1.1",              # 设备IP地址
    snmp_version="v3",             # 使用SNMP v3
    user="managev3user"            # SNMP v3用户名 (不需要认证和隐私密钥)
)
```

有关详细的路由器配置指南，请参阅 [ROUTER_CONFIG_GUIDE.md](ROUTER_CONFIG_GUIDE.md) 文件。

## 路由器端SNMP v3完整配置示例

```
# 配置SNMP v3组（使用authnopriv安全级别）
[HUAWEI] snmp-agent group v3 managev3group authnopriv

# 配置SNMP v3用户（关联到组）
[HUAWEI] snmp-agent usm-user v3 wjkjv3user managev3group

# 配置认证密钥
[HUAWEI] snmp-agent usm-user v3 wjkjv3user authentication-mode sha Wjkj6912

# 开启SNMP服务
[HUAWEI] snmp-agent
```

### 认证和加密算法说明

华为设备支持多种认证和加密算法：

**认证算法：**
- MD5 (较弱，但兼容性好)
- SHA (推荐，更安全)

**加密算法：**
- DES56 (较弱，但兼容性好)
- AES128 (推荐，更安全)

在实际使用中，建议使用SHA+AES128组合以获得更好的安全性。

### 重要配置说明

1. **配置验证**：配置完成后，可以使用以下命令验证配置是否正确：
   ```
   [HUAWEI] display snmp-agent usm-user
   ```

2. **故障排除**：如果出现authorizationError错误，请检查以下几点：
   - 路由器上的用户名是否与代码中配置的用户名一致
   - 路由器上是否正确配置了用户组和用户
   - 对于authentication安全级别，还需检查：
     - 认证密钥是否与路由器配置一致
     - 认证协议是否与路由器配置一致

## 华为设备OID信息

本项目使用以下华为设备OID来获取监控数据：

- CPU使用率: `1.3.6.1.4.1.2011.5.25.31.1.1.1.1.11`
- 内存使用率: `1.3.6.1.4.1.2011.5.25.31.1.1.1.1.7`
- 设备温度: `1.3.6.1.4.1.2011.5.25.31.1.1.1.1.6`

这些OID是根据华为设备的MIB定义确定的，适用于大多数华为交换机设备。

## 测试脚本使用

运行测试脚本：

```bash
python test_snmp_async.py
```

请根据实际情况修改测试脚本中的参数。

## 注意事项

1. 确保网络连接正常
2. 确保设备上的SNMP服务已启用
3. 确保防火墙允许SNMP端口通信（默认161）
4. 不同型号的华为设备可能使用不同的OID，请根据实际情况调整