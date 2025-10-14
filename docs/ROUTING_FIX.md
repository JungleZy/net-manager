# 路由顺序修复说明

## 问题描述

在 Tornado 框架中，路由是按照定义顺序进行匹配的。当访问 `/api/topologies/latest` 时，如果通配符路由 `/api/topologies/(?P<topology_id>[^/]+)` 在前面，会首先匹配到该路由，将 "latest" 当作 `topology_id` 处理，导致 404 错误。

## 错误路由顺序（修复前）

```python
(r"/api/topologies", TopologiesHandler),           # 正确
(r"/api/topologies/latest", TopologyLatestHandler), # ❌ 永远不会匹配
(r"/api/topologies/create", TopologyCreateHandler), # ❌ 永远不会匹配
(r"/api/topologies/update", TopologyUpdateHandler), # ❌ 永远不会匹配
(r"/api/topologies/delete", TopologyDeleteHandler), # ❌ 永远不会匹配
(r"/api/topologies/(?P<topology_id>[^/]+)", TopologyHandler), # ⚠️ 会匹配所有
```

### 问题分析

访问 `/api/topologies/latest` 时：

1. 第一个路由 `/api/topologies` 不匹配（缺少后缀）
2. 跳过第二个路由 `/api/topologies/latest`
3. 直接被第六个路由 `/api/topologies/(?P<topology_id>[^/]+)` 匹配
4. 将 "latest" 作为 `topology_id` 传递给 `TopologyHandler`
5. `TopologyHandler` 尝试将 "latest" 转换为整数失败或查询不到数据
6. 返回 404 错误

## 正确路由顺序（修复后）

```python
# 拓扑图相关路由（注意：具体路径必须放在通配符路由之前）
(r"/api/topologies/latest", TopologyLatestHandler),  # ✅ 最具体的路径
(r"/api/topologies/create", TopologyCreateHandler),  # ✅
(r"/api/topologies/update", TopologyUpdateHandler),  # ✅
(r"/api/topologies/delete", TopologyDeleteHandler),  # ✅
(r"/api/topologies", TopologiesHandler),             # ✅
(r"/api/topologies/(?P<topology_id>[^/]+)", TopologyHandler), # ✅ 通配符放最后
```

### 匹配流程

访问 `/api/topologies/latest` 时：

1. 第一个路由 `/api/topologies/latest` **完全匹配** ✅
2. 调用 `TopologyLatestHandler` 处理请求
3. 返回最新的拓扑图数据

访问 `/api/topologies/123` 时：

1. 前面的具体路径都不匹配
2. 最后的通配符路由 `/api/topologies/(?P<topology_id>[^/]+)` 匹配
3. 将 "123" 作为 `topology_id` 传递给 `TopologyHandler`
4. 返回 ID 为 123 的拓扑图数据

## Tornado 路由匹配规则

### 1. 按顺序匹配

路由按照在列表中定义的顺序进行匹配，**第一个匹配的路由生效**。

### 2. 优先级原则

- **具体路径优先**：`/api/topologies/latest` 应该在 `/api/topologies/(?P<id>[^/]+)` 之前
- **精确匹配优先**：完全匹配的路由应该在正则表达式路由之前
- **通配符最后**：包含参数的通配符路由应该放在最后

### 3. 路由排序建议

正确的排序顺序：

```
1. 完全精确的路径（如 /api/topologies/latest）
2. 带固定前缀的路径（如 /api/topologies/create）
3. 不带参数的路径（如 /api/topologies）
4. 带参数的路径（如 /api/topologies/{id}）
5. 通配符路径（如 /api/topologies/(.*)）
```

## 其他路由示例

### Devices 路由（正确示例）

```python
(r"/api/devices/create", DeviceCreateHandler),  # ✅ 具体路径在前
(r"/api/devices/update", DeviceUpdateHandler),
(r"/api/devices/delete", DeviceDeleteHandler),
(r"/api/devices", DevicesHandler),
(r"/api/devices/(?P<device_id>[^/]+)/type", DeviceTypeHandler), # 更具体的参数路由
(r"/api/devices/(?P<device_id>[^/]+)", DeviceHandler),  # 通配符在最后
```

### Switches 路由（正确示例）

```python
(r"/api/switches/create", SwitchCreateHandler),
(r"/api/switches/update", SwitchUpdateHandler),
(r"/api/switches/delete", SwitchDeleteHandler),
(r"/api/switches/scan", SNMPScanHandler),
(r"/api/switches/scan/simple", SNMPScanHandlerSimple),
(r"/api/switches", SwitchesHandler),
(r"/api/switches/([^/]+)", SwitchHandler),  # 通配符在最后
```

## 测试验证

修复后，所有路由应该正常工作：

```bash
# 测试获取最新拓扑图
curl http://localhost:8080/api/topologies/latest

# 测试创建拓扑图
curl -X POST http://localhost:8080/api/topologies/create \
  -H "Content-Type: application/json" \
  -d '{"content": {"nodes": [], "edges": []}}'

# 测试根据ID获取拓扑图
curl http://localhost:8080/api/topologies/1

# 测试获取所有拓扑图
curl http://localhost:8080/api/topologies
```

## 总结

在 Tornado（以及大多数 Web 框架）中配置路由时：

1. ✅ **具体路径放在前面**
2. ✅ **通配符路由放在后面**
3. ✅ **测试所有路由确保正确匹配**
4. ✅ **添加注释说明路由顺序的重要性**

## 相关文件

- API 服务器配置: `server/src/network/api/api_server.py`
- 拓扑图处理器: `server/src/network/api/handlers/topology_handlers.py`
- API 文档: `server/src/network/api/handlers/TOPOLOGY_API.md`
