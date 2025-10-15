# 拓扑图测试数据生成指南

## 📋 概述

为拓扑图添加了测试数据生成功能，可以快速生成三层网络架构的测试数据，用于开发、测试和演示。

## 🏗️ 三层网络架构

生成的拓扑图遵循标准的三层网络架构设计：

### 1. 核心层 (Core Layer)
- **数量**: 2台核心交换机
- **设备型号**: Cisco Nexus 9000
- **带宽**: 100Gbps
- **功能**: 提供高速骨干网络，实现不同汇聚层之间的互联

### 2. 汇聚层 (Distribution Layer)
- **数量**: 6台汇聚交换机
- **设备型号**: Cisco Catalyst 4500
- **带宽**: 40Gbps
- **功能**: 连接核心层和接入层，提供策略控制和流量汇聚

### 3. 接入层 (Access Layer)
- **数量**: 12台接入交换机（默认配置）
- **设备型号**: Cisco Catalyst 2960
- **带宽**: 10Gbps
- **功能**: 为终端设备提供网络接入

### 4. 终端设备
- **总数**: 500台设备（默认配置）
- **类型分布**:
  - 🖥️ PC (50%)
  - 💻 笔记本 (30%)
  - 🖧 服务器 (10%)
  - 🖨️ 打印机 (5%)
  - 📡 路由器 (3%)
  - 🛡️ 防火墙 (2%)

## 🎯 功能特性

### 1. 标准测试数据（20交换机 + 500设备）
```javascript
switchCount: 20
deviceCount: 500
架构: 2核心 + 6汇聚 + 12接入
```

### 2. 简化版测试数据（8交换机 + 50设备）
```javascript
switchCount: 8
deviceCount: 50
架构: 2核心 + 2汇聚 + 4接入
适用场景: 快速测试、原型演示
```

### 3. 大规模测试数据（30交换机 + 1000设备）
```javascript
switchCount: 30
deviceCount: 1000
架构: 2核心 + 8汇聚 + 20接入
适用场景: 性能测试、大规模网络模拟
```

## 🚀 使用方法

### 界面操作

1. **打开拓扑图页面**
   - 导航到 `拓扑图` 页面

2. **生成测试数据**
   - 点击顶部的测试数据面板中的按钮：
     - 🎨 **生成测试数据**: 标准三层架构（20交换机+500设备）
     - 📊 **简化版**: 小规模测试（8交换机+50设备）
     - 🚀 **大规模**: 性能测试（30交换机+1000设备）

3. **其他操作**
   - 💾 **导出JSON**: 将当前拓扑数据导出为JSON文件
   - 🗑️ **清空**: 清空当前拓扑图的所有数据

### 编程方式

```javascript
import { 
  generateThreeTierTopology,
  generateSimpleTestData,
  generateLargeScaleTestData,
  exportToJSON
} from '@/utils/topologyTestDataGenerator'

// 生成自定义规模的测试数据
const data = generateThreeTierTopology({
  switchCount: 20,
  deviceCount: 500
})

// 生成简化版
const simpleData = generateSimpleTestData()

// 生成大规模
const largeData = generateLargeScaleTestData()

// 导出为JSON
exportToJSON(data, 'my-topology.json')
```

## 📊 数据结构

生成的数据遵循 D3 拓扑图格式：

```javascript
{
  nodes: [
    {
      id: 'core-switch-1',
      type: 'switch',
      label: '核心交换机-1',
      x: 500,
      y: 375,
      status: 'online',
      properties: {
        layer: 'core',
        deviceType: 'core-switch',
        bandwidth: '100Gbps',
        model: 'Cisco Nexus 9000'
      }
    },
    // ... 更多节点
  ],
  links: [
    {
      id: 'link-core-switch-1-distribution-switch-1',
      source: 'core-switch-1',
      target: 'distribution-switch-1',
      properties: {
        bandwidth: '40Gbps',
        protocol: 'LACP'
      }
    },
    // ... 更多连线
  ],
  metadata: {
    architecture: 'three-tier',
    coreCount: 2,
    distributionCount: 6,
    accessCount: 12,
    deviceCount: 500,
    totalNodes: 520,
    totalLinks: 1046,
    generatedAt: '2025-10-15T...'
  }
}
```

## 🔗 连接关系

### 核心层 ↔ 汇聚层
- **连接方式**: 全网状连接（Full Mesh）
- **冗余性**: 每个汇聚交换机连接到所有核心交换机
- **协议**: LACP（链路聚合控制协议）

### 汇聚层 ↔ 接入层
- **连接方式**: 双上联
- **冗余性**: 每个接入交换机连接到2个汇聚交换机
  - 主连接：根据哈希分配
  - 备份连接：提供冗余保护

### 接入层 ↔ 终端设备
- **连接方式**: 单连接
- **分布**: 设备均匀分布到各接入交换机
- **位置**: 设备在接入交换机下方随机分布

## 🎨 可视化布局

生成的拓扑图采用分层布局：

```
画布尺寸: 2000 x 1500
层级间距: 375像素

   核心层 (y=375)
      ↓
   汇聚层 (y=750)
      ↓
   接入层 (y=1125)
      ↓
   终端设备 (y=1125+)
```

## ⚡ 性能优化

1. **渐进式加载**: 使用 setTimeout 避免 UI 阻塞
2. **自适应视图**: 生成后自动调整视图适应所有节点
3. **状态模拟**: 5% 的设备随机设置为离线状态

## 🛠️ 文件说明

### 核心文件
- `dashboard/src/utils/topologyTestDataGenerator.js`: 测试数据生成器
- `dashboard/src/views/topology/Topology.vue`: 拓扑图主页面（含UI控制）
- `dashboard/src/components/topology/D3Topology.vue`: D3拓扑图组件

### 功能函数

#### generateThreeTierTopology(config)
生成三层网络架构测试数据

**参数**:
- `config.switchCount`: 交换机总数（默认20）
- `config.deviceCount`: 设备总数（默认500）

**返回**: `{ nodes, links, metadata }`

#### generateSimpleTestData()
生成简化版测试数据（8交换机+50设备）

#### generateLargeScaleTestData()
生成大规模测试数据（30交换机+1000设备）

#### exportToJSON(data, filename)
导出数据为JSON文件

## 📝 注意事项

1. **性能考虑**: 
   - 大规模数据（1000+设备）可能影响渲染性能
   - 建议在性能较好的设备上测试大规模数据

2. **数据持久化**: 
   - 测试数据仅在内存中，刷新页面会丢失
   - 使用"保存"按钮可将数据持久化到数据库

3. **设备状态**: 
   - 95% 设备状态为 online
   - 5% 设备状态为 offline（模拟真实场景）

4. **IP/MAC地址**: 
   - IP地址: 192.168.x.x 格式随机生成
   - MAC地址: 标准格式随机生成

## 🔍 调试信息

生成数据后，控制台会输出详细统计信息：

```
===== 拓扑图生成完成 =====
核心层交换机: 2
汇聚层交换机: 6
接入层交换机: 12
总交换机数: 20
终端设备数: 500
总节点数: 520
总连线数: 1046
==========================
```

## 🎯 应用场景

1. **开发测试**: 快速生成测试数据，验证功能
2. **性能测试**: 使用大规模数据测试渲染性能
3. **演示展示**: 使用标准数据展示系统能力
4. **培训教学**: 展示三层网络架构设计
5. **原型验证**: 快速验证布局算法和交互功能

## 🚧 未来扩展

- [ ] 支持自定义网络架构（如二层、扁平化等）
- [ ] 支持导入JSON数据
- [ ] 支持VLAN配置
- [ ] 支持设备故障模拟
- [ ] 支持流量可视化

## 📚 相关文档

- [D3拓扑图重构报告](./D3_REFACTOR_REPORT.md)
- [性能优化文档](./PERFORMANCE_OPTIMIZATION.md)
- [D3拓扑图使用说明](./D3_TOPOLOGY_README.md)
