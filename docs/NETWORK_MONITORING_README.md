# 网络拓扑实时监控功能

## 概述

Network.vue 页面实现了基于 LogicFlow 的网络拓扑实时监控功能，提供可视化的网络状态监控和流量动画展示。

## 功能特性

### ✨ 核心功能

1. **拓扑可视化**

   - 使用 LogicFlow 渲染网络拓扑图
   - 支持多种设备类型（交换机、路由器、服务器、PC 等）
   - 自动布局和居中显示
   - 支持缩放、拖拽操作

2. **实时状态监控**

   - WebSocket 实时推送设备状态
   - 节点颜色动态变化（在线/离线）
   - 实时统计面板（总数、在线、离线）
   - 多设备并发更新

3. **流量动画**

   - 根据接口流量显示连线动画
   - 流动虚线效果
   - 颜色和粗细区分有无流量
   - 自动启停动画

4. **交互控制**
   - 刷新按钮：重新加载拓扑
   - 居中按钮：画布居中显示
   - 缩放控制：放大/缩小/适应画布

## 快速开始

### 1. 前置条件

- Node.js 16+
- Python 3.7+
- 已配置的后端服务器
- 已创建的拓扑数据

### 2. 启动服务

```bash
# 启动后端（包含 WebSocket）
cd server
python main.py

# 启动前端
cd dashboard
npm run dev
```

### 3. 访问页面

浏览器访问 `http://localhost:5173`，导航到"网络"菜单

## 数据要求

### 拓扑数据格式

API: `GET /api/topologies/latest`

```json
{
  "id": 1,
  "content": {
    "nodes": [
      {
        "id": "node_1",
        "type": "switch",
        "x": 200,
        "y": 300,
        "properties": {
          "width": 60,
          "height": 60,
          "status": "online",
          "data": {
            "id": "switch_001",
            "name": "核心交换机"
          }
        },
        "text": {
          "value": "核心交换机"
        }
      }
    ],
    "edges": [
      {
        "id": "edge_1",
        "type": "line",
        "sourceNodeId": "node_1",
        "targetNodeId": "node_2"
      }
    ]
  }
}
```

### WebSocket 消息格式

#### 设备状态更新

```json
{
  "type": "deviceStatus",
  "data": {
    "device_id": "switch_001",
    "status": "online",
    "online": true
  }
}
```

#### SNMP 设备更新（含流量）

```json
{
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
}
```

## 状态颜色说明

- 🟦 **蓝色** - 设备在线 (`status: 'online'`)
- 🟥 **红色** - 设备离线 (`status: 'offline'`)

## 流量动画说明

- **灰色细线** - 无流量传输
- **蓝色粗线 + 流动动画** - 有数据传输
- 动画速度：1 秒一个循环
- 自动根据流量状态启停

## 文档索引

- **[详细技术文档](./Network-Topology-Monitor.md)** - 完整技术实现说明
- **[测试指南](./Network-Testing-Guide.md)** - 测试方法和示例
- **[实现总结](./Network-Implementation-Summary.md)** - 开发总结和优化建议

## 测试工具

使用内置测试工具模拟数据：

```javascript
// 浏览器控制台
import('/src/utils/networkTestHelper.js').then((module) => {
  const helper = module.default
  const ws = window.Ws?.getInstance()

  // 模拟设备上线
  helper.simulateDeviceStatus(ws, 'device_001', true)

  // 模拟流量
  helper.simulateSnmpDeviceUpdate(ws, 'switch_001', [
    {
      name: 'GigabitEthernet0/1',
      inRate: 10000000,
      outRate: 5000000,
      connectedDeviceId: 'device_002'
    }
  ])
})
```

## 注意事项

### 1. 设备 ID 匹配

确保 WebSocket 消息中的设备 ID 与拓扑节点 ID 一致：

```javascript
// 拓扑节点
node.properties.data.id === 'switch_001'

// WebSocket 消息
data.device_id === 'switch_001' // ✅ 必须匹配
```

### 2. 接口连接关系

要显示边的动画，需要提供接口连接的目标设备 ID：

```javascript
interface.connected_device_id = 'target_device_id'
```

### 3. WebSocket 连接

确保后端 WebSocket 服务运行在 `ws://localhost:12344/ws`

## 性能优化

- 启用局部渲染（`partial: true`）
- 使用 Map 存储设备状态
- 避免频繁的完整图更新
- 支持大规模拓扑（1000+ 节点）

## 常见问题

### Q: 拓扑图不显示？

检查：

1. `/api/topologies/latest` 是否返回数据
2. 数据格式是否正确
3. 控制台是否有错误

### Q: 节点状态不更新？

检查：

1. WebSocket 是否连接
2. 设备 ID 是否匹配
3. 是否正确订阅事件

### Q: 动画不显示？

检查：

1. 接口流量是否 > 0
2. `connected_device_id` 是否提供
3. 浏览器是否支持 CSS 动画

## 扩展建议

- 添加流量速率显示
- 支持双向流量动画
- 添加告警节点提示
- 实现历史状态回放
- 支持自定义配色

## 相关文件

```
dashboard/
├── src/
│   ├── views/
│   │   └── network/
│   │       └── Network.vue          # 主组件
│   ├── common/
│   │   ├── api/
│   │   │   └── topology.js          # API
│   │   ├── node/
│   │   │   ├── BaseCustomNode.js    # 节点基类
│   │   │   └── nodeConfig.js        # 节点配置
│   │   └── ws/
│   │       └── Ws.js                # WebSocket
│   └── utils/
│       └── networkTestHelper.js     # 测试工具
└── docs/
    ├── Network-Topology-Monitor.md  # 技术文档
    ├── Network-Testing-Guide.md     # 测试指南
    └── Network-Implementation-Summary.md  # 总结
```

## 版本信息

- 实现日期：2025-10-18
- LogicFlow 版本：2.1.2
- Vue 版本：3.5.22

## 许可证

本功能遵循项目主许可证
