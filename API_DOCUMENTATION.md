# Net Manager API 文档

## 概述

Net Manager API 提供了对网络中客户端系统信息的查询接口。API基于Tornado框架构建，提供了RESTful风格的接口。

## 基础URL

```
http://localhost:12344
```

## API端点

### 1. 主页信息

**请求URL**: `GET /`

**描述**: 获取API服务器的基本信息和可用端点列表

**响应示例**:
```json
{
  "message": "Net Manager API Server",
  "version": "1.0.0",
  "endpoints": {
    "GET /api/systems": "获取所有系统信息",
    "GET /api/systems/{mac_address}": "根据MAC地址获取特定系统信息",
    "GET /health": "健康检查"
  }
}
```

### 2. 健康检查

**请求URL**: `GET /health` 或 `GET /healthz`

**描述**: 检查API服务器的健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Net Manager API Server"
}
```

### 3. 获取所有系统信息

**请求URL**: `GET /api/systems`

**描述**: 获取所有已连接客户端的系统信息

**响应示例**:
```json
{
  "status": "success",
  "data": [
    {
      "mac_address": "f0-2f-74-db-87-1f",
      "hostname": "DESKTOP-ABC123",
      "ip_address": "192.168.1.100",
      "services": [...],
      "processes": [...],
      "timestamp": "2025-10-05 14:54:59"
    }
  ],
  "count": 1
}
```

### 4. 根据MAC地址获取特定系统信息

**请求URL**: `GET /api/systems/{mac_address}`

**描述**: 根据MAC地址获取特定客户端的系统信息

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "mac_address": "f0-2f-74-db-87-1f",
    "hostname": "DESKTOP-ABC123",
    "ip_address": "192.168.1.100",
    "services": [...],
    "processes": [...],
    "timestamp": "2025-10-05 14:54:59"
  }
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "未找到MAC地址为 f0-2f-74-db-87-1f 的系统信息"
}
```

## 数据结构说明

### 系统信息(System Info)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| mac_address | string | 客户端MAC地址 |
| hostname | string | 客户端主机名 |
| ip_address | string | 客户端IP地址 |
| services | array | 客户端运行的服务列表 |
| processes | array | 客户端运行的进程列表 |
| timestamp | string | 信息收集时间 |

### 服务信息(Service)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| name | string | 服务名称 |
| status | string | 服务状态 |
| pid | integer | 进程ID |

### 进程信息(Process)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| name | string | 进程名称 |
| status | string | 进程状态 |
| pid | integer | 进程ID |
| cpu_percent | float | CPU使用率 |
| memory_percent | float | 内存使用率 |

## 错误处理

API使用标准HTTP状态码来表示请求结果：

- `200` - 请求成功
- `404` - 请求的资源未找到
- `500` - 服务器内部错误

## 使用示例

### 使用curl

```bash
# 获取所有系统信息
curl http://localhost:12344/api/systems

# 根据MAC地址获取特定系统信息
curl http://localhost:12344/api/systems/f0-2f-74-db-87-1f
```

### 使用Python requests

```python
import requests

# 获取所有系统信息
response = requests.get('http://localhost:12344/api/systems')
data = response.json()

# 根据MAC地址获取特定系统信息
response = requests.get('http://localhost:12344/api/systems/f0-2f-74-db-87-1f')
data = response.json()
```