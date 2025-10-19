# 设备列表 Popover 功能文档

## 功能概述

为 Network.vue 页面左上角的统计面板添加了**点击交互功能**，点击"在线"或"离线"数字时，弹出对应状态的设备列表 Popover 气泡卡片。

---

## 功能特性

### 1. 交互式统计面板

#### 点击在线设备数

- **触发：** 点击"在线: N"数字
- **弹出：** 在线设备列表 Popover
- **位置：** 统计面板下方左对齐
- **内容：** 所有在线的设备和交换机

#### 点击离线设备数

- **触发：** 点击"离线: N"数字
- **弹出：** 离线设备列表 Popover
- **位置：** 统计面板下方左对齐
- **内容：** 所有离线的设备和交换机

---

## 设备列表展示

### 列表项信息

每个设备项包含以下信息：

| 字段         | 说明              | 示例              |
| ------------ | ----------------- | ----------------- |
| **设备名称** | hostname 或 alias | Server-01         |
| **IP 地址**  | 设备 IP           | 192.168.1.100     |
| **状态标签** | 在线/离线徽章     | 🟢 在线 / 🔴 离线 |

### 空状态提示

- **无在线设备：** "暂无在线设备"
- **无离线设备：** "暂无离线设备"

---

## 技术实现

### 1. Popover 组件

使用 Ant Design Vue 的 `a-popover` 组件：

```vue
<a-popover
  v-model:open="onlinePopoverVisible"
  title="在线设备列表"
  trigger="click"
  placement="bottomLeft"
  overlayClassName="device-list-popover"
>
  <template #content>
    <!-- 设备列表内容 -->
  </template>
  <div class="stat-item clickable">
    <span class="stat-label">在线:</span>
    <span class="stat-value online">{{ stats.onlineNodes }}</span>
  </div>
</a-popover>
```

### 2. 状态管理

```javascript
// Popover 显示状态
const onlinePopoverVisible = ref(false)
const offlinePopoverVisible = ref(false)
```

### 3. 设备列表计算

#### 在线设备列表

```javascript
const onlineDevicesList = computed(() => {
  const list = []

  // 收集在线设备
  for (const device of devices.value) {
    if (device.online) {
      list.push({
        id: device.client_id || device.id,
        hostname: device.hostname,
        name: device.alias || device.hostname,
        ip: device.ip || device.networks?.[0]?.ip_address,
        type: 'device'
      })
    }
  }

  // 收集在线交换机
  for (const switchDevice of switches.value) {
    if (switchDevice.online) {
      list.push({
        id: switchDevice.switch_id || switchDevice.id,
        hostname: switchDevice.name || switchDevice.ip,
        name: switchDevice.alias || switchDevice.name,
        ip: switchDevice.ip,
        type: 'switch'
      })
    }
  }

  return list
})
```

#### 离线设备列表

```javascript
const offlineDevicesList = computed(() => {
  const list = []

  // 收集离线设备（逻辑类似在线设备）
  // ...

  return list
})
```

---

## UI 设计

### 1. 可点击样式

统计面板中的在线/离线项添加了可点击效果：

```less
.stat-item {
  &.clickable {
    cursor: pointer;
    transition: all 0.2s ease;
    padding: 4px 8px;
    margin: -4px -8px;
    border-radius: 4px;

    &:hover {
      background: rgba(24, 144, 255, 0.1);
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(0);
    }
  }
}
```

**交互反馈：**

- 鼠标悬停 → 背景色变化 + 向上浮动
- 鼠标点击 → 向下压缩效果
- 指针变为手型

### 2. Popover 卡片样式

```
┌─────────────────────────────┐
│  在线设备列表        ✕      │  ← 标题栏
├─────────────────────────────┤
│  Server-01               🟢 │
│  192.168.1.100   在线       │
├─────────────────────────────┤
│  Router-Main             🟢 │
│  192.168.1.1     在线       │
├─────────────────────────────┤
│  Switch-01               🟢 │
│  192.168.1.254   在线       │
└─────────────────────────────┘
```

**样式特点：**

- 最大宽度：400px
- 最大高度：400px（超出可滚动）
- 设备项分隔线
- 悬停高亮效果

### 3. 设备项样式

```less
.device-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f5f5f5;
  }

  .device-name {
    font-size: 14px;
    font-weight: 500;
    color: #262626;
    margin-bottom: 6px;
  }

  .device-info {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .device-ip {
      font-size: 12px;
      color: #8c8c8c;
      font-family: 'Consolas', 'Monaco', monospace;
    }

    .device-status {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;

      &.online-badge {
        background-color: #f6ffed;
        color: #52c41a;
        border: 1px solid #b7eb8f;
      }

      &.offline-badge {
        background-color: #fff2f0;
        color: #ff4d4f;
        border: 1px solid #ffccc7;
      }
    }
  }
}
```

---

## 暗黑模式适配

### 可点击项悬停效果

```less
&.dark-mode {
  .stats-panel {
    .stat-item {
      &.clickable:hover {
        background: rgba(24, 144, 255, 0.2);
      }
    }
  }
}
```

**适配说明：**

- Popover 背景色自动适配（Ant Design Vue 原生支持）
- 设备项悬停效果自动调整
- 状态徽章颜色保持一致

---

## 用户体验优化

### 1. 视觉反馈

| 交互         | 反馈                  |
| ------------ | --------------------- |
| **鼠标悬停** | 背景色变化 + 向上浮动 |
| **点击**     | 弹出 Popover          |
| **再次点击** | 关闭 Popover          |
| **点击外部** | 自动关闭 Popover      |

### 2. 信息层次

```
设备名称（加粗、较大）
    ↓
IP 地址（灰色、等宽字体）+ 状态徽章（彩色）
```

### 3. 滚动优化

- 设备列表超过 400px 高度时，自动显示滚动条
- 平滑滚动效果
- 滚动条样式优化

---

## 数据来源

### 1. 设备数据

**来源：** `devices` 数组（从 `DeviceApi.getDevicesList()` 获取）

**使用字段：**

- `client_id` / `id` - 设备 ID
- `hostname` - 主机名
- `alias` - 别名
- `ip` - IP 地址
- `networks[0].ip_address` - 网络接口 IP（备用）
- `online` - 在线状态

### 2. 交换机数据

**来源：** `switches` 数组（从 `SwitchApi.getSwitchesList()` 获取）

**使用字段：**

- `switch_id` / `id` - 交换机 ID
- `name` - 名称
- `alias` - 别名
- `ip` - IP 地址
- `online` - 在线状态

---

## 性能优化

### 1. 使用 computed 计算

```javascript
// 自动缓存，只在依赖变化时重新计算
const onlineDevicesList = computed(() => {
  // ...
})
```

**优势：**

- 依赖追踪自动化
- 避免重复计算
- 内存占用优化

### 2. 避免深拷贝

直接从原始数据提取需要的字段：

```javascript
list.push({
  id: device.client_id || device.id,
  hostname: device.hostname
  // ...
})
```

### 3. 懒加载

Popover 只在点击时渲染内容，未展开时不占用资源。

---

## 兼容性

### 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

### 功能兼容性

- ✅ 与全屏功能兼容
- ✅ 与主题切换兼容
- ✅ 与设备详情弹窗兼容
- ✅ 响应式布局适配

---

## 代码变更总结

### 修改的文件

- `dashboard/src/views/network/Network.vue`

### 新增的状态变量

```javascript
const onlinePopoverVisible = ref(false)
const offlinePopoverVisible = ref(false)
```

### 新增的计算属性

```javascript
const onlineDevicesList = computed(() => {
  /* ... */
})
const offlineDevicesList = computed(() => {
  /* ... */
})
```

### 新增的样式类

```less
.stat-item.clickable {
  /* 可点击样式 */
}
.device-list-popover {
  /* Popover 容器样式 */
}
.device-list-content {
  /* 设备列表内容样式 */
}
.device-item {
  /* 设备项样式 */
}
```

---

## 测试建议

### 功能测试

1. ✅ 点击"在线"数字，验证弹出在线设备列表
2. ✅ 点击"离线"数字，验证弹出离线设备列表
3. ✅ 验证设备信息显示正确（名称、IP、状态）
4. ✅ 验证空状态提示正常显示

### 视觉测试

1. ✅ 验证可点击项的悬停效果
2. ✅ 验证 Popover 位置正确（bottomLeft）
3. ✅ 验证设备项样式正常
4. ✅ 验证状态徽章颜色正确

### 交互测试

1. ✅ 快速点击在线/离线数字，验证 Popover 切换流畅
2. ✅ 点击 Popover 外部，验证自动关闭
3. ✅ 滚动设备列表，验证滚动条正常
4. ✅ 设备列表超过 400px 时，验证滚动功能

### 兼容性测试

1. ✅ 在明亮/暗黑模式下测试
2. ✅ 在全屏模式下测试
3. ✅ 在不同分辨率下测试
4. ✅ 测试设备数据更新时列表自动刷新

---

## 未来优化建议

### 1. 设备搜索功能（可选）

在设备列表较多时，添加搜索框：

```vue
<template #content>
  <a-input
    v-model="searchKeyword"
    placeholder="搜索设备"
    style="margin-bottom: 8px;"
  />
  <div class="device-list-content">
    <!-- 过滤后的设备列表 -->
  </div>
</template>
```

### 2. 设备分类（可选）

将设备和交换机分组显示：

```
在线设备列表
├─ 设备 (5)
│  ├─ Server-01
│  └─ PC-Main
└─ 交换机 (3)
   ├─ Switch-01
   └─ Router-Main
```

### 3. 点击设备跳转（可选）

点击设备项时，定位到拓扑图中的对应节点：

```javascript
const handleDeviceClick = (deviceId) => {
  // 关闭 Popover
  onlinePopoverVisible.value = false

  // 定位到节点
  lf.focusOn(deviceId)

  // 高亮节点
  lf.selectNodeById(deviceId)
}
```

### 4. 导出设备列表（可选）

添加导出按钮，支持 CSV/Excel 导出：

```vue
<a-button size="small" @click="exportDeviceList">
  导出列表
</a-button>
```

---

## 常见问题

### Q1: Popover 不显示怎么办？

**A:** 检查以下几点：

1. 确认设备列表数据已加载
2. 检查 Popover 的 `v-model:open` 绑定是否正确
3. 验证 CSS 样式是否被覆盖

### Q2: 设备信息显示不全怎么办？

**A:** 检查设备数据结构：

- 确认 `hostname`、`ip`、`alias` 字段存在
- 对于设备，检查 `networks` 数组
- 对于交换机，检查 `name` 字段

### Q3: 如何修改 Popover 的最大高度？

**A:** 修改样式中的 `max-height` 属性：

```less
.device-list-content {
  max-height: 500px; // 修改为需要的高度
  overflow-y: auto;
}
```

### Q4: 如何添加设备类型图标？

**A:** 在设备名称前添加图标：

```vue
<div class="device-name">
  <LaptopOutlined v-if="device.type === 'device'" />
  <RouterOutlined v-if="device.type === 'switch'" />
  {{ device.hostname }}
</div>
```

---

## 版本历史

| 版本 | 日期       | 说明                                |
| ---- | ---------- | ----------------------------------- |
| v1.0 | 2025-10-20 | 初始版本，实现设备列表 Popover 功能 |

---

**开发者：** Qoder AI  
**文档更新日期：** 2025-10-20  
**文档版本：** v1.0
