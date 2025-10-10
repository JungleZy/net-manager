# 交换机管理API文档

本文档描述了用于管理交换机配置信息的RESTful API接口。

## API端点

所有交换机相关的API端点都以 `/api/switches` 为前缀。

### 获取所有交换机配置

**请求**
```
GET /api/switches
```

**响应**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "ip": "192.168.1.10",
      "snmp_version": "2c",
      "community": "public",
      "user": "",
      "auth_key": "",
      "auth_protocol": "",
      "priv_key": "",
      "priv_protocol": "",
      "description": "核心交换机",
      "created_at": "2023-01-01T10:00:00",
      "updated_at": "2023-01-01T10:00:00"
    }
  ],
  "count": 1
}
```

### 根据ID获取交换机配置

**请求**
```
GET /api/switches/{id}
```

**响应**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "ip": "192.168.1.10",
    "snmp_version": "2c",
    "community": "public",
    "user": "",
    "auth_key": "",
    "auth_protocol": "",
    "priv_key": "",
    "priv_protocol": "",
    "description": "核心交换机",
    "created_at": "2023-01-01T10:00:00",
    "updated_at": "2023-01-01T10:00:00"
  }
}
```

### 创建交换机配置

**请求**
```
POST /api/switches/create
Content-Type: application/json

{
  "ip": "192.168.1.20",
  "snmp_version": "3",
  "community": "public",
  "user": "admin",
  "auth_key": "authkey123",
  "auth_protocol": "SHA",
  "priv_key": "privkey123",
  "priv_protocol": "AES",
  "description": "接入层交换机"
}
```

**响应**
```json
{
  "status": "success",
  "message": "交换机配置添加成功"
}
```

### 更新交换机配置

**请求**
```
POST /api/switches/update
Content-Type: application/json

{
  "id": 1,
  "ip": "192.168.1.20",
  "snmp_version": "3",
  "community": "private",
  "user": "admin",
  "auth_key": "newauthkey123",
  "auth_protocol": "SHA",
  "priv_key": "newprivkey123",
  "priv_protocol": "AES",
  "description": "更新后的接入层交换机"
}
```

**响应**
```json
{
  "status": "success",
  "message": "交换机配置更新成功"
}
```

### 删除交换机配置

**请求**
```
POST /api/switches/delete
Content-Type: application/json

{
  "id": 1
}
```

**响应**
```json
{
  "status": "success",
  "message": "交换机配置删除成功"
}
```

## 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 否(仅更新/删除时) | 交换机ID |
| ip | string | 是 | 交换机IP地址 |
| snmp_version | string | 是 | SNMP版本('1', '2c', '3') |
| community | string | 否 | SNMP community字符串(v1/v2c) |
| user | string | 否 | SNMPv3用户名 |
| auth_key | string | 否 | SNMPv3认证密钥 |
| auth_protocol | string | 否 | SNMPv3认证协议('MD5', 'SHA') |
| priv_key | string | 否 | SNMPv3隐私密钥 |
| priv_protocol | string | 否 | SNMPv3隐私协议('DES', 'AES') |
| description | string | 否 | 交换机描述信息 |

## 错误响应

所有错误响应都遵循以下格式：

```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

常见的HTTP状态码：
- 200: 请求成功
- 400: 请求参数错误
- 404: 资源未找到
- 500: 服务器内部错误