# Network.vue 功能测试指南

## 快速测试步骤

### 1. 启动开发服务器

```bash
cd dashboard
npm run dev
```

### 2. 访问网络监控页面

打开浏览器访问：`http://localhost:5173` (或你配置的端口)

导航到"网络"菜单项，进入 Network.vue 页面

### 3. 验证基本功能

#### 3.1 拓扑图加载

- ✅ 页面加载后应自动从 `/api/topologies/latest` 获取拓扑数据
- ✅ 拓扑图应在画布中居中显示
- ✅ 左上角应显示统计信息（总节点、在线、离线）
- ✅ 右上角应显示刷新和居中按钮

#### 3.2 节点状态显示

节点颜色应根据状态变化：

- 🟦 **在线设备**：蓝色图标 (`status: 'online'`)
- 🟥 **离线设备**：红色图标 (`status: 'offline'`)

#### 3.3 控制按钮

- **刷新按钮**：点击应重新加载拓扑数据
- **居中按钮**：点击应将拓扑图居中显示
- **缩放按钮**：LogicFlow 内置的放大/缩小按钮应正常工作

### 4. 测试 WebSocket 实时更新

#### 方法一：使用浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 在控制台输入以下命令：

```javascript
// 导入测试工具
import('/src/utils/networkTestHelper.js').then((module) => {
  const helper = module.default

  // 获取 WebSocket 实例
  const wsInstance = window.Ws?.getInstance()

  // 测试设备状态变化
  helper.simulateDeviceStatus(wsInstance, 'device_001', true) // 设备上线

  // 3秒后设备离线
  setTimeout(() => {
    helper.simulateDeviceStatus(wsInstance, 'device_001', false)
  }, 3000)
})
```

#### 方法二：从后端发送实际数据

确保后端 WebSocket 服务正在运行，然后：

1. 使用 Python 脚本发送测试数据：

```python
import asyncio
import websockets
import json

async def send_test_data():
    uri = "ws://localhost:12344/ws"
    async with websockets.connect(uri) as websocket:
        # 发送设备状态更新
        await websocket.send(json.dumps({
            "type": "deviceStatus",
            "data": {
                "device_id": "device_001",
                "status": "online",
                "online": True
            }
        }))

        # 等待3秒
        await asyncio.sleep(3)

        # 发送 SNMP 设备更新（包含流量）
        await websocket.send(json.dumps({
            "type": "snmpDeviceUpdate",
            "data": {
                "switch_id": "switch_001",
                "ip": "192.168.1.1",
                "interface_info": {
                    "interfaces": [
                        {
                            "index": 1,
                            "name": "GigabitEthernet0/1",
                            "in_octets_rate": 5000000,
                            "out_octets_rate": 3000000,
                            "connected_device_id": "device_002"
                        }
                    ]
                }
            }
        }))

asyncio.run(send_test_data())
```

### 5. 验证连线动画

要查看连线的流动动画效果：

1. **确保拓扑图中有连接**：两个节点之间需要有边（edge）
2. **发送流量数据**：通过 WebSocket 发送包含流量信息的 SNMP 更新
3. **观察动画**：有流量的连线应该：
   - 颜色变为蓝色 (`#1890ff`)
   - 线宽增加到 3px
   - 显示虚线流动动画

#### 使用控制台测试连线动画：

```javascript
import('/src/utils/networkTestHelper.js').then((module) => {
  const helper = module.default
  const wsInstance = window.Ws?.getInstance()

  // 模拟交换机接口流量（假设 switch_001 连接到 device_002）
  helper.simulateSnmpDeviceUpdate(wsInstance, 'switch_001', [
    {
      name: 'GigabitEthernet0/1',
      inRate: 10000000, // 10 Mbps 入站
      outRate: 5000000, // 5 Mbps 出站
      connectedDeviceId: 'device_002'
    }
  ])
})
```

### 6. 测试场景

#### 场景 1: 设备从离线到在线

```javascript
import('/src/utils/networkTestHelper.js').then((module) => {
  const helper = module.default
  const wsInstance = window.Ws?.getInstance()

  helper.simulateDeviceOnlineScenario(wsInstance, 'device_001')
})
```

预期结果：

- 设备节点初始为红色（离线）
- 2 秒后变为蓝色（在线）
- 统计面板中的在线/离线数量相应更新

#### 场景 2: 流量波动

```javascript
import('/src/utils/networkTestHelper.js').then((module) => {
  const helper = module.default
  const wsInstance = window.Ws?.getInstance()

  helper.simulateTrafficFlowScenario(wsInstance, 'switch_001', 'device_002')
})
```

预期结果：

- 连线的颜色和粗细随流量变化
- 有流量时显示流动动画
- 无流量时动画消失

#### 场景 3: 多设备状态变化

```javascript
import('/src/utils/networkTestHelper.js').then((module) => {
  const helper = module.default
  const wsInstance = window.Ws?.getInstance()

  helper.simulateMultiDeviceScenario(wsInstance, [
    'device_001',
    'device_002',
    'device_003',
    'device_004',
    'device_005'
  ])
})
```

预期结果：

- 多个设备状态依次变化
- 统计面板实时更新
- 每个设备的颜色根据状态改变

### 7. 检查控制台输出

打开浏览器控制台，应该能看到：

```
设备状态更新: {device_id: "device_001", status: "online", ...}
SNMP设备更新: {switch_id: "switch_001", ...}
```

### 8. 验证 API 调用

在开发者工具的 Network 标签中，检查：

- ✅ `GET /api/topologies/latest` - 加载拓扑数据
- ✅ `WebSocket /ws` - WebSocket 连接建立

### 9. 性能测试

对于大型拓扑（100+ 节点）：

1. 生成大型测试拓扑（在 Topology.vue 页面使用调试面板）
2. 保存拓扑
3. 切换到 Network.vue 页面
4. 观察：
   - 加载时间应 < 2 秒
   - 画布操作（缩放、平移）应流畅
   - 状态更新应实时响应

### 10. 常见问题排查

#### 问题：拓扑图不显示

检查：

1. 控制台是否有错误
2. `/api/topologies/latest` 是否返回数据
3. 返回的数据格式是否正确

#### 问题：节点状态不更新

检查：

1. WebSocket 是否连接成功
2. 控制台是否收到 WebSocket 消息
3. `device_id` 是否与节点的 `properties.data.id` 匹配

#### 问题：连线动画不显示

检查：

1. 边的 `properties.hasData` 是否为 `true`
2. CSS 动画是否正确加载
3. 浏览器是否支持 CSS 动画

#### 问题：统计数据不准确

检查：

1. `deviceStatusMap` 是否正确更新
2. 节点的 `status` 属性是否正确设置

## 调试技巧

### 1. 启用详细日志

在 Network.vue 中添加更多 console.log：

```javascript
// 在 updateNodeStatus 函数中
console.log('更新节点状态:', deviceId, status, '节点数据:', node)

// 在 updateEdgeDataStatus 函数中
console.log('更新边状态:', sourceId, targetId, hasData, '边数据:', edge)
```

### 2. 查看 LogicFlow 内部状态

在控制台中：

```javascript
// 获取当前图数据
const graphData = lf.getGraphData()
console.log('节点数:', graphData.nodes.length)
console.log('边数:', graphData.edges.length)
console.log('所有节点:', graphData.nodes)

// 查看特定节点
const node = lf.getNodeModelById('node_id')
console.log('节点属性:', node.properties)
```

### 3. 监控 WebSocket 消息

```javascript
const wsInstance = window.Ws?.getInstance()
const originalOnMessage = wsInstance.socket.onmessage

wsInstance.socket.onmessage = (e) => {
  console.log('收到 WebSocket 消息:', JSON.parse(e.data))
  originalOnMessage(e)
}
```

## 测试清单

- [ ] 拓扑图正常加载
- [ ] 节点按状态显示不同颜色
- [ ] 统计面板显示正确的数量
- [ ] 刷新按钮工作正常
- [ ] 居中按钮工作正常
- [ ] WebSocket 连接成功
- [ ] 设备状态实时更新
- [ ] 连线动画正常显示
- [ ] 多设备同时更新正常
- [ ] 性能表现良好（无卡顿）

## 下一步

测试通过后，可以：

1. 将功能部署到生产环境
2. 添加更多自定义功能（告警、历史回放等）
3. 优化性能（如使用虚拟滚动处理超大拓扑）
4. 添加用户配置选项（颜色主题、动画速度等）
