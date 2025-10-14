# 拓扑图 API 接口文档

## 概述

本文档描述了网络管理系统中拓扑图管理相关的 RESTful API 接口。

**基础 URL**: `http://localhost:8080`

## 接口列表

### 1. 创建拓扑图

创建一个新的拓扑图。

- **URL**: `/api/topologies/create`
- **方法**: `POST`
- **请求头**: `Content-Type: application/json`

#### 请求参数

| 参数名  | 类型          | 必需 | 说明                                 |
| ------- | ------------- | ---- | ------------------------------------ |
| content | String/Object | 是   | 拓扑图内容，可以是 JSON 字符串或对象 |

#### 请求示例

```json
{
  "content": {
    "nodes": [
      {
        "id": "1",
        "type": "router",
        "label": "核心路由器",
        "x": 100,
        "y": 100
      },
      { "id": "2", "type": "switch", "label": "交换机1", "x": 200, "y": 200 }
    ],
    "edges": [{ "source": "1", "target": "2" }]
  }
}
```

或者使用 JSON 字符串：

```json
{
  "content": "{\"nodes\":[{\"id\":\"1\",\"type\":\"router\"}],\"edges\":[]}"
}
```

#### 响应示例

**成功 (200)**

```json
{
  "status": "success",
  "message": "拓扑图创建成功",
  "data": {
    "id": 1
  }
}
```

**失败 (400)**

```json
{
  "status": "error",
  "message": "缺少必需的字段: content"
}
```

---

### 2. 更新拓扑图

更新现有拓扑图的内容。

- **URL**: `/api/topologies/update`
- **方法**: `POST`
- **请求头**: `Content-Type: application/json`

#### 请求参数

| 参数名  | 类型          | 必需 | 说明           |
| ------- | ------------- | ---- | -------------- |
| id      | Integer       | 是   | 拓扑图 ID      |
| content | String/Object | 是   | 新的拓扑图内容 |

#### 请求示例

```json
{
  "id": 1,
  "content": {
    "nodes": [
      {
        "id": "1",
        "type": "router",
        "label": "核心路由器",
        "x": 100,
        "y": 100
      },
      { "id": "2", "type": "switch", "label": "交换机1", "x": 200, "y": 200 },
      { "id": "3", "type": "pc", "label": "电脑1", "x": 300, "y": 300 }
    ],
    "edges": [
      { "source": "1", "target": "2" },
      { "source": "2", "target": "3" }
    ]
  }
}
```

#### 响应示例

**成功 (200)**

```json
{
  "status": "success",
  "message": "拓扑图更新成功"
}
```

**失败 (404)**

```json
{
  "status": "error",
  "message": "未找到ID为 1 的拓扑图"
}
```

---

### 3. 删除拓扑图

删除指定的拓扑图。

- **URL**: `/api/topologies/delete`
- **方法**: `POST`
- **请求头**: `Content-Type: application/json`

#### 请求参数

| 参数名 | 类型    | 必需 | 说明      |
| ------ | ------- | ---- | --------- |
| id     | Integer | 是   | 拓扑图 ID |

#### 请求示例

```json
{
  "id": 1
}
```

#### 响应示例

**成功 (200)**

```json
{
  "status": "success",
  "message": "拓扑图删除成功"
}
```

**失败 (404)**

```json
{
  "status": "error",
  "message": "未找到ID为 1 的拓扑图"
}
```

---

### 4. 获取所有拓扑图

获取所有拓扑图列表，按创建时间降序排列。

- **URL**: `/api/topologies`
- **方法**: `GET`

#### 响应示例

**成功 (200)**

```json
{
  "status": "success",
  "data": [
    {
      "id": 2,
      "content": {
        "nodes": [...],
        "edges": [...]
      },
      "created_at": "2025-10-14 14:45:30"
    },
    {
      "id": 1,
      "content": {
        "nodes": [...],
        "edges": [...]
      },
      "created_at": "2025-10-14 14:42:02"
    }
  ],
  "count": 2
}
```

---

### 5. 获取最新拓扑图

获取创建时间最新的拓扑图。

- **URL**: `/api/topologies/latest`
- **方法**: `GET`

#### 响应示例

**成功 (200)**

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "content": {
      "nodes": [
        {
          "id": "1",
          "type": "router",
          "label": "核心路由器",
          "x": 100,
          "y": 100
        }
      ],
      "edges": []
    },
    "created_at": "2025-10-14 14:45:30"
  }
}
```

**失败 (404)**

```json
{
  "status": "error",
  "message": "未找到任何拓扑图"
}
```

---

### 6. 根据 ID 获取拓扑图

根据 ID 获取指定的拓扑图。

- **URL**: `/api/topologies/{id}`
- **方法**: `GET`

#### 路径参数

| 参数名 | 类型    | 必需 | 说明      |
| ------ | ------- | ---- | --------- |
| id     | Integer | 是   | 拓扑图 ID |

#### 请求示例

```
GET /api/topologies/1
```

#### 响应示例

**成功 (200)**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "content": {
      "nodes": [
        {
          "id": "1",
          "type": "router",
          "label": "核心路由器",
          "x": 100,
          "y": 100
        }
      ],
      "edges": []
    },
    "created_at": "2025-10-14 14:42:02"
  }
}
```

**失败 (404)**

```json
{
  "status": "error",
  "message": "未找到ID为 1 的拓扑图"
}
```

---

## 错误码说明

| HTTP 状态码 | 说明                                               |
| ----------- | -------------------------------------------------- |
| 200         | 请求成功                                           |
| 400         | 请求参数错误（缺少必需字段、类型错误、格式无效等） |
| 404         | 资源不存在                                         |
| 500         | 服务器内部错误                                     |

## 数据模型

### TopologyInfo

| 字段名     | 类型          | 说明                                |
| ---------- | ------------- | ----------------------------------- |
| id         | Integer       | 拓扑图 ID（自增主键）               |
| content    | Object/String | 拓扑图内容，通常包含 nodes 和 edges |
| created_at | String        | 创建时间，格式: YYYY-MM-DD HH:MM:SS |

### Content 结构示例

```json
{
  "nodes": [
    {
      "id": "节点ID",
      "type": "节点类型（router/switch/pc/server等）",
      "label": "节点标签",
      "x": "X坐标",
      "y": "Y坐标"
    }
  ],
  "edges": [
    {
      "source": "源节点ID",
      "target": "目标节点ID"
    }
  ]
}
```

## 测试指南

### 使用 curl 测试

1. **创建拓扑图**

```bash
curl -X POST http://localhost:8080/api/topologies/create \
  -H "Content-Type: application/json" \
  -d '{"content": {"nodes": [], "edges": []}}'
```

2. **获取所有拓扑图**

```bash
curl http://localhost:8080/api/topologies
```

3. **获取最新拓扑图**

```bash
curl http://localhost:8080/api/topologies/latest
```

4. **更新拓扑图**

```bash
curl -X POST http://localhost:8080/api/topologies/update \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "content": {"nodes": [], "edges": []}}'
```

5. **删除拓扑图**

```bash
curl -X POST http://localhost:8080/api/topologies/delete \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

### 使用 Python 测试

运行测试脚本：

```bash
cd server
python examples/topology_api_test.py
```

## 注意事项

1. **CORS 支持**: 所有接口都支持跨域请求
2. **Content 格式**: content 字段可以是 JSON 字符串或对象，系统会自动处理
3. **时间格式**: created_at 字段使用服务器本地时间，格式为 `YYYY-MM-DD HH:MM:SS`
4. **ID 生成**: 拓扑图 ID 由数据库自动生成（自增）
5. **数据验证**: 创建和更新时会验证 content 是否为有效的 JSON 格式

## 版本信息

- **API 版本**: 1.0.0
- **最后更新**: 2025-10-14
