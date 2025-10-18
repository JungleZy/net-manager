# 网络拓扑监控页面说明

## 功能概述

Network.vue 页面实现了网络拓扑的实时监控功能，主要包括：

1. **拓扑图展示**：使用 LogicFlow 可视化展示网络拓扑结构
2. **实时状态更新**：通过 WebSocket 实时更新节点的在线/离线状态
3. **流量动画**：当连接有数据传输时，连线会显示流动动画效果
4. **统计信息**：实时显示总节点数、在线节点数、离线节点数

## 技术实现

### 1. 数据来源

- **拓扑数据**：从 `/api/topologies/latest` API 获取最新的拓扑图数据
- **设备状态**：通过 WebSocket 订阅 `deviceStatus` 事件获取实时状态
- **流量数据**：通过 WebSocket 订阅 `snmpDeviceUpdate` 事件获取接口流量信息

### 2. 核心组件

#### LogicFlow 配置

```javascript
lf = new LogicFlow({
  container: container.value,
  width,
  height,
  grid: true,
  edgeType: 'line',
  style: {
    edge: {
      stroke: '#afafaf',
      strokeWidth: 2
    }
  },
  plugins: [Control, Dagre],
  partial: true // 启用局部渲染，提升性能
})
```

#### 自定义节点

项目使用了多种自定义节点类型：

- `FirewallNode` - 防火墙节点
- `LaptopNode` - 笔记本节点
- `PCNode` - 台式机节点
- `PrinterNode` - 打印机节点
- `RouterNode` - 路由器节点
- `ServerNode` - 服务器节点
- `SwitchNode` - 交换机节点
- `GroupNode` - 分组节点

所有节点都继承自 `BaseCustomNode`，支持通过 `properties.status` 控制节点颜色：

- `status: 'online'` - 在线状态（蓝色）
- `status: 'offline'` - 离线状态（红色）

#### 动画边实现

自定义了带动画的边类型 `AnimatedEdgeView`：

```javascript
class AnimatedEdgeView extends lf.LineEdge {
  getEdgeStyle() {
    const style = super.getEdgeStyle()
    const { properties } = this.props.model

    // 当 properties.hasData 为 true 时显示流动动画
    if (properties?.hasData) {
      return {
        ...style,
        stroke: '#1890ff',
        strokeWidth: 3,
        strokeDasharray: '10 5',
        animation: 'lf-dash-flow 1s linear infinite'
      }
    }

    return style
  }
}
```

CSS 动画定义：

```scss
@keyframes lf-dash-flow {
  from {
    stroke-dashoffset: 0;
  }
  to {
    stroke-dashoffset: -15;
  }
}
```

### 3. WebSocket 数据处理

#### 设备状态更新

```javascript
// 订阅设备状态更新
PubSub.subscribe(wsCode.DEVICE_STATUS, (data) => {
  const deviceId = data.device_id || data.id
  const status = data.status || (data.online ? 'online' : 'offline')
  updateNodeStatus(deviceId, status)
})
```

#### SNMP 设备更新（包含流量数据）

```javascript
// 订阅 SNMP 设备更新
PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, (data) => {
  const deviceId = data.switch_id || data.device_id

  // 更新设备在线状态
  updateNodeStatus(deviceId, 'online')

  // 检查接口流量数据
  if (data.interface_info) {
    const interfaces = data.interface_info.interfaces || []
    interfaces.forEach((iface) => {
      // 判断是否有数据传输
      const hasData =
        (iface.in_octets_rate && iface.in_octets_rate > 0) ||
        (iface.out_octets_rate && iface.out_octets_rate > 0)

      if (hasData && iface.connected_device_id) {
        updateEdgeDataStatus(deviceId, iface.connected_device_id, hasData)
      }
    })
  }
})
```

## UI 组件

### 统计面板

显示在页面左上角，包含：

- 总节点数
- 在线节点数（绿色）
- 离线节点数（红色）

### 控制面板

显示在页面右上角，包含：

- **刷新按钮**：重新加载拓扑图数据
- **居中按钮**：将拓扑图居中显示

### LogicFlow 内置控件

- **放大/缩小**：调整画布缩放级别
- **适应画布**：自动调整缩放以显示全部内容
- **重做/撤销**：（如果启用）

## 数据结构

### 拓扑图数据格式

```javascript
{
  nodes: [
    {
      id: 'node_1',
      type: 'switch',  // 节点类型
      x: 200,
      y: 300,
      properties: {
        width: 60,
        height: 60,
        status: 'online',  // 'online' | 'offline'
        data: {
          id: 'device_123',  // 设备ID
          name: '核心交换机',
          // 其他设备数据...
        }
      },
      text: {
        x: 200,
        y: 300,
        value: '核心交换机'
      }
    }
  ],
  edges: [
    {
      id: 'edge_1',
      type: 'line',
      sourceNodeId: 'node_1',
      targetNodeId: 'node_2',
      properties: {
        hasData: false  // 是否有数据传输
      }
    }
  ]
}
```

### WebSocket 消息格式

#### 设备状态更新

```javascript
{
  type: 'deviceStatus',
  data: {
    device_id: 'device_123',
    status: 'online',  // 'online' | 'offline'
    online: true
  }
}
```

#### SNMP 设备更新

```javascript
{
  type: 'snmpDeviceUpdate',
  data: {
    switch_id: 'switch_456',
    ip: '192.168.1.1',
    interface_info: {
      interfaces: [
        {
          index: 1,
          name: 'GigabitEthernet0/1',
          in_octets_rate: 1024000,   // 入站速率（字节/秒）
          out_octets_rate: 512000,   // 出站速率（字节/秒）
          connected_device_id: 'device_789'  // 连接的设备ID
        }
      ]
    }
  }
}
```

## 性能优化

1. **局部渲染**：启用 `partial: true` 选项，只渲染可视区域内的节点
2. **状态映射**：使用 `Map` 存储设备状态，快速查找和更新
3. **资源清理**：组件卸载时正确清理 WebSocket 订阅和 LogicFlow 实例

## 使用建议

### 1. 扩展流量动画功能

如果需要根据实际流量大小调整动画速度：

```javascript
const updateEdgeDataStatus = (sourceId, targetId, hasData, trafficRate) => {
  if (edge && edgeModel) {
    // 根据流量速率计算动画速度
    const animationDuration = Math.max(0.5, 2 - trafficRate / 1000000)

    edgeModel.setProperties({
      hasData: hasData,
      trafficRate: trafficRate,
      animationDuration: `${animationDuration}s`
    })
  }
}
```

### 2. 添加边的点击事件

显示连接详情：

```javascript
lf.on('edge:click', ({ data }) => {
  // 显示连接详情模态框
  showConnectionDetails(data)
})
```

### 3. 自定义节点状态颜色

在 `nodeConfig.js` 中修改：

```javascript
export const DEFAULT_STYLES = Object.freeze({
  ONLINE_COLOR: '#0276F7', // 在线颜色
  OFFLINE_COLOR: 'red' // 离线颜色
})
```

## 常见问题

### Q1: 节点状态不更新？

**A:** 检查以下几点：

1. WebSocket 是否正常连接
2. `data.device_id` 是否与节点的 `properties.data.id` 匹配
3. 是否正确订阅了 WebSocket 事件

### Q2: 边的动画不显示？

**A:** 确保：

1. 边的 `properties.hasData` 被正确设置为 `true`
2. CSS 动画样式已加载
3. 浏览器支持 CSS 动画

### Q3: 拓扑图加载失败？

**A:** 检查：

1. `/api/topologies/latest` API 是否返回正确数据
2. 数据格式是否符合 LogicFlow 要求
3. 浏览器控制台是否有错误信息

## 未来改进

1. **双向流量显示**：区分入站和出站流量方向
2. **流量速率显示**：在边上显示实时流量速率
3. **告警提示**：当节点离线或流量异常时显示告警图标
4. **历史回放**：支持查看历史拓扑状态
5. **自定义布局**：提供多种自动布局算法选择
6. **导出功能**：支持导出为图片或 PDF

## 相关文件

- `dashboard/src/views/network/Network.vue` - 主组件
- `dashboard/src/common/node/BaseCustomNode.js` - 节点基类
- `dashboard/src/common/node/nodeConfig.js` - 节点配置
- `dashboard/src/common/api/topology.js` - 拓扑 API
- `dashboard/src/common/ws/Ws.js` - WebSocket 管理
- `dashboard/src/common/utils/PubSub.js` - 发布订阅工具
