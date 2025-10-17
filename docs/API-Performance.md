# 服务器性能监控 API

## 概述

提供服务器性能数据的 HTTP 接口，用于首次加载时获取当前性能数据，避免等待 WebSocket 推送。

## 接口信息

### 获取当前性能数据

**接口地址**: `/api/performance`

**请求方法**: `GET`

**请求参数**: 无

**响应格式**: JSON

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "timestamp": 1760711603.0975797,
    "cpu": {
      "usage_percent": 8.8,
      "cores": 16,
      "physical_cores": 8,
      "current_frequency": 4700.0,
      "max_frequency": 4700.0,
      "load_average": [0.0, 0.0, 0.0],
      "per_cpu_percent": [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 16.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0
      ]
    },
    "memory": {
      "total": 33451163648,
      "available": 15360217088,
      "used": 18090946560,
      "free": 15360217088,
      "usage_percent": 54.1,
      "swap_total": 10200547328,
      "swap_used": 104906752,
      "swap_free": 10095640576,
      "swap_percent": 1.0
    },
    "disk": {
      "partitions": [
        {
          "device": "C:\\",
          "mountpoint": "C:\\",
          "fstype": "NTFS",
          "total": 213968220160,
          "used": 161404657664,
          "free": 52563562496,
          "usage_percent": 75.4
        }
      ],
      "total": 999090544640,
      "used": 791749566464,
      "free": 207340978176,
      "usage_percent": 79.25,
      "io": {
        "read_bytes": 21886261760,
        "write_bytes": 12043543552,
        "read_count": 360443,
        "write_count": 263292
      }
    },
    "network": [
      {
        "name": "WLAN",
        "bytes_sent": 232762936,
        "bytes_recv": 2129879705,
        "packets_sent": 1082430,
        "packets_recv": 1839871,
        "upload_rate": 167546.82,
        "download_rate": 868649.65,
        "mac_address": "28-D0-43-5D-96-0A",
        "ip_address": "192.168.31.249",
        "netmask": "255.255.255.0"
      }
    ]
  }
}
```

**错误响应示例**:

```json
{
  "code": 500,
  "message": "获取性能数据失败: [错误信息]",
  "data": null
}
```

## 字段说明

### 响应字段

| 字段    | 类型    | 说明               |
| ------- | ------- | ------------------ |
| code    | Integer | 状态码，0 表示成功 |
| message | String  | 响应消息           |
| data    | Object  | 性能数据对象       |

### 性能数据字段 (data)

| 字段      | 类型   | 说明             |
| --------- | ------ | ---------------- |
| timestamp | Float  | 数据采集时间戳   |
| cpu       | Object | CPU 性能数据     |
| memory    | Object | 内存使用数据     |
| disk      | Object | 磁盘使用数据     |
| network   | Array  | 网络接口数据数组 |

### CPU 数据字段 (cpu)

| 字段              | 类型    | 说明                             |
| ----------------- | ------- | -------------------------------- |
| usage_percent     | Float   | CPU 总使用率(%)                  |
| cores             | Integer | 逻辑核心数                       |
| physical_cores    | Integer | 物理核心数                       |
| current_frequency | Float   | 当前频率(MHz)                    |
| max_frequency     | Float   | 最大频率(MHz)                    |
| load_average      | Array   | 负载平均值(1/5/15 分钟，仅 Unix) |
| per_cpu_percent   | Array   | 每个核心的使用率(%)              |

### 内存数据字段 (memory)

| 字段          | 类型    | 说明               |
| ------------- | ------- | ------------------ |
| total         | Integer | 总内存(字节)       |
| available     | Integer | 可用内存(字节)     |
| used          | Integer | 已用内存(字节)     |
| free          | Integer | 空闲内存(字节)     |
| usage_percent | Float   | 使用率(%)          |
| swap_total    | Integer | 交换空间总量(字节) |
| swap_used     | Integer | 交换空间已用(字节) |
| swap_free     | Integer | 交换空间空闲(字节) |
| swap_percent  | Float   | 交换空间使用率(%)  |

### 磁盘数据字段 (disk)

| 字段          | 类型    | 说明           |
| ------------- | ------- | -------------- |
| partitions    | Array   | 分区数组       |
| total         | Integer | 总容量(字节)   |
| used          | Integer | 已用容量(字节) |
| free          | Integer | 空闲容量(字节) |
| usage_percent | Float   | 使用率(%)      |
| io            | Object  | 磁盘 IO 统计   |

### 网络接口数据字段 (network[])

| 字段          | 类型    | 说明              |
| ------------- | ------- | ----------------- |
| name          | String  | 接口名称          |
| bytes_sent    | Integer | 累计发送字节数    |
| bytes_recv    | Integer | 累计接收字节数    |
| packets_sent  | Integer | 累计发送数据包数  |
| packets_recv  | Integer | 累计接收数据包数  |
| upload_rate   | Float   | 上传速率(字节/秒) |
| download_rate | Float   | 下载速率(字节/秒) |
| mac_address   | String  | MAC 地址          |
| ip_address    | String  | IP 地址           |
| netmask       | String  | 子网掩码          |

## 使用示例

### JavaScript (Axios)

```javascript
import axios from 'axios'

async function loadPerformanceData() {
  try {
    const response = await axios.get('/api/performance')
    if (response.data.code === 0) {
      const performanceData = response.data.data
      console.log('CPU使用率:', performanceData.cpu.usage_percent + '%')
      console.log('内存使用率:', performanceData.memory.usage_percent + '%')
    }
  } catch (error) {
    console.error('获取性能数据失败:', error)
  }
}
```

### Python

```python
import requests

response = requests.get('http://localhost:5000/api/performance')
data = response.json()

if data['code'] == 0:
    perf = data['data']
    print(f"CPU使用率: {perf['cpu']['usage_percent']}%")
    print(f"内存使用率: {perf['memory']['usage_percent']}%")
```

### cURL

```bash
curl http://localhost:5000/api/performance
```

## 注意事项

1. **数据一致性**: 该接口返回的数据格式与 WebSocket 推送的数据格式完全一致
2. **首次加载优化**: 建议在组件挂载时调用此接口获取初始数据，然后订阅 WebSocket 接收实时更新
3. **网络速率**: 网络速率 (upload_rate/download_rate) 在首次请求时可能为 0，需要至少两次采集才能计算速率
4. **跨平台差异**: 某些字段在不同操作系统上可能不可用（如 load_average 仅在 Unix 系统有效）

## 相关接口

- WebSocket 推送: `ws://host:port/ws` (消息类型: `server_performance`)
- 健康检查: `GET /health` 或 `GET /healthz`
