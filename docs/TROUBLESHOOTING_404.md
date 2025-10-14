# 拓扑图 API 404 问题排查指南

## 问题描述

前端请求 `/api/topologies/latest` 返回 404 错误。

## 排查步骤

### 1. 确认服务器是否运行

**检查方法**：

```bash
# Windows PowerShell
Get-NetTCPConnection -LocalPort 12344 -State Listen
```

**预期结果**：

- 如果服务器运行中，会显示监听 12344 端口的进程
- 如果没有输出，说明服务器未启动

**解决方案**：

```bash
cd server
python main.py
```

### 2. 确认服务器已重启应用路由修改

**重要提示**：修改路由配置后**必须重启服务器**才能生效！

**操作步骤**：

1. 停止当前运行的服务器（Ctrl+C）
2. 重新启动服务器：
   ```bash
   cd d:\workspace\net-manager\server
   python main.py
   ```

### 3. 测试后端路由是否正确

**运行测试脚本**：

```bash
cd server
python test_topology_routes.py
```

**预期结果**：

```
✅ 通过 - /api/topologies/latest
✅ 通过 - /api/topologies
✅ 通过 - /api/topologies/create
```

**如果测试失败**：

- 检查服务器是否正在运行
- 检查端口 12344 是否被其他程序占用
- 查看服务器控制台的错误日志

### 4. 使用 curl 直接测试 API

**测试获取最新拓扑图**：

```bash
curl http://127.0.0.1:12344/api/topologies/latest
```

**预期结果**：

- **首次访问**（没有拓扑图）：

  ```json
  {
    "status": "error",
    "message": "未找到任何拓扑图"
  }
  ```

  这是**正常的**！因为还没有创建任何拓扑图。

- **有拓扑图后**：
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "content": {...},
      "created_at": "2025-10-14 14:42:02"
    }
  }
  ```

**测试创建拓扑图**：

```bash
curl -X POST http://127.0.0.1:12344/api/topologies/create \
  -H "Content-Type: application/json" \
  -d "{\"content\": {\"nodes\": [], \"edges\": []}}"
```

**预期结果**：

```json
{
  "status": "success",
  "message": "拓扑图创建成功",
  "data": {
    "id": 1
  }
}
```

### 5. 检查前端配置

**查看浏览器控制台**：

1. 打开浏览器开发者工具（F12）
2. 切换到 Network（网络）标签
3. 刷新页面，查看请求详情

**检查请求 URL**：

- 正确的 URL：`http://127.0.0.1:12344/api/topologies/latest`
- 如果 URL 不对，检查 `dashboard/index.html` 中的 `window.httpUrl` 配置

**检查请求头**：

- Content-Type: `application/json`

### 6. 查看服务器日志

**服务器启动成功的标志**：

```
2025-10-14 22:42:02,214 - net_manager - INFO - API服务端启动，监听端口 12344
2025-10-14 22:42:02,214 - net_manager - INFO - 拓扑图信息表初始化成功
```

**路由请求日志**：

```
200 GET /api/topologies/latest (127.0.0.1) 0.54ms
```

**如果看到 404**：

```
404 GET /api/topologies/latest (127.0.0.1) 0.54ms
```

说明路由配置有问题或服务器未重启。

## 常见问题和解决方案

### 问题 1: 服务器未重启

**症状**：修改了代码，但仍然 404

**解决**：

1. 停止服务器（Ctrl+C）
2. 重新启动：`python main.py`

### 问题 2: 端口被占用

**症状**：

```
OSError: [WinError 10048] 通常每个套接字地址只允许使用一次
```

**解决**：

1. 查找占用端口的进程：
   ```powershell
   Get-NetTCPConnection -LocalPort 12344 | Select-Object OwningProcess
   ```
2. 结束该进程：
   ```powershell
   Stop-Process -Id <进程ID>
   ```
3. 重新启动服务器

### 问题 3: 路由顺序错误

**症状**：所有 `/api/topologies/*` 路径都返回 404 或错误

**检查**：查看 `server/src/network/api/api_server.py` 中路由定义顺序

**正确顺序**：

```python
(r"/api/topologies/latest", TopologyLatestHandler),    # 具体路径在前
(r"/api/topologies/create", TopologyCreateHandler),
(r"/api/topologies/update", TopologyUpdateHandler),
(r"/api/topologies/delete", TopologyDeleteHandler),
(r"/api/topologies", TopologiesHandler),
(r"/api/topologies/(?P<topology_id>[^/]+)", TopologyHandler), # 通配符在后
```

### 问题 4: 数据库未初始化

**症状**：

```
sqlite3.OperationalError: no such table: topology_info
```

**解决**：
TopologyManager 会在初始化时自动创建表，确保服务器正常启动即可。

### 问题 5: 前端请求方式错误

**症状**：POST 请求返回 404

**检查**：

- `/api/topologies/create` 应该是 POST
- `/api/topologies/latest` 应该是 GET
- `/api/topologies` 应该是 GET

## 验证清单

在报告问题前，请确认以下项目：

- [ ] 服务器正在运行（端口 12344 监听中）
- [ ] 修改代码后已重启服务器
- [ ] 运行 `test_topology_routes.py` 全部通过
- [ ] curl 测试可以正常访问
- [ ] 前端配置的 baseURL 是 `http://127.0.0.1:12344`
- [ ] 浏览器控制台 Network 标签显示完整请求信息
- [ ] 服务器控制台没有错误日志

## 快速诊断命令

```bash
# 1. 测试服务器是否运行
curl http://127.0.0.1:12344/health

# 2. 测试拓扑图API
curl http://127.0.0.1:12344/api/topologies/latest

# 3. 创建测试拓扑图
curl -X POST http://127.0.0.1:12344/api/topologies/create \
  -H "Content-Type: application/json" \
  -d "{\"content\": {\"nodes\": [], \"edges\": []}}"

# 4. 再次获取最新拓扑图
curl http://127.0.0.1:12344/api/topologies/latest
```

## 成功标志

当一切正常时，前端加载拓扑图页面应该：

1. **首次访问**（无拓扑图）：

   - 控制台显示：404 错误是正常的
   - 页面显示默认的示例拓扑图

2. **保存后**：

   - 显示"拓扑图创建成功"消息
   - 刷新页面能看到保存的拓扑图

3. **后续访问**：
   - 自动加载最新的拓扑图
   - 没有 404 错误

## 联系支持

如果以上步骤都无法解决问题，请提供：

1. 服务器启动日志
2. 浏览器控制台 Network 请求详情
3. `test_topology_routes.py` 运行结果
4. 服务器版本信息
