# SNMP设备表格状态字段实现说明

## 功能概述

在SNMP设备表格中添加状态字段，通过从localforage读取SNMP设备数据来实时更新和显示设备的在线/离线状态。

---

## 实现细节

### 1. 修改的文件

- [`src/views/devices/SNMPDevicesTab.vue`](e:\workspace\project\net-manager\dashboard\src\views\devices\SNMPDevicesTab.vue)

### 2. 新增的功能

#### 2.1 状态数据管理

```javascript
// SNMP设备状态数据
const snmpDevicesStatus = ref({})

// 加载SNMP设备状态
const loadSNMPDevicesStatus = async () => {
  try {
    const devices = await SNMPStorage.getAllDevices()
    snmpDevicesStatus.value = devices
  } catch (error) {
    console.error('加载SNMP设备状态失败:', error)
  }
}
```

#### 2.2 设备列表增强

使用计算属性为每个设备添加状态信息：

```javascript
const switchesWithStatus = computed(() => {
  return props.switches.map(sw => {
    const snmpData = snmpDevicesStatus.value[sw.ip]
    return {
      ...sw,
      status: snmpData?.type || 'unknown',      // success/error/unknown
      statusText: getStatusText(snmpData?.type), // 在线/离线/未知
      lastUpdate: snmpData?.updateTime || null, // 最后更新时间
      errorMsg: snmpData?.error || null          // 错误信息
    }
  })
})
```

#### 2.3 状态过滤

新增状态筛选条件：

```javascript
const filters = ref({
  deviceName: '',
  alias: '',
  deviceType: undefined,
  status: undefined  // 新增状态筛选
})

// 状态筛选逻辑
if (filters.value.status) {
  result = result.filter(
    (item) => item.status === filters.value.status
  )
}
```

#### 2.4 表格列定义

添加状态列：

```javascript
{
  title: '状态',
  dataIndex: 'status',
  align: 'center',
  key: 'status',
  width: 80
}
```

#### 2.5 状态显示（Tag组件）

```vue
<template #bodyCell="{ column, record }">
  <template v-if="column.dataIndex === 'status'">
    <!-- 在线状态 -->
    <a-tag
      v-if="record.status === 'success'"
      color="success"
      :title="最后更新时间提示"
    >
      在线
    </a-tag>
    
    <!-- 离线状态 -->
    <a-tag
      v-else-if="record.status === 'error'"
      color="error"
      :title="错误信息"
    >
      离线
    </a-tag>
    
    <!-- 未知状态 -->
    <a-tag v-else color="default">
      未知
    </a-tag>
  </template>
</template>
```

#### 2.6 实时更新

监听WebSocket消息，自动更新状态：

```javascript
onMounted(async () => {
  // 初始加载SNMP状态
  await loadSNMPDevicesStatus()
  
  // 订阅SNMP设备批量更新
  unsubscribe = PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, async (data) => {
    console.log('收到SNMP设备批量更新')
    await loadSNMPDevicesStatus()
  })
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
})
```

---

## 数据流程

### 1. 数据来源

```
服务器SNMP轮询 → WebSocket推送 → Ws.js自动保存到localforage
                                   ↓
                           SNMPDevicesTab.vue读取
```

### 2. 状态匹配

```javascript
// 通过IP地址匹配设备状态
后端设备列表 (props.switches) + localforage中的SNMP状态数据
          ↓
    switchesWithStatus (带状态的设备列表)
          ↓
     filteredSwitches (过滤后的列表)
          ↓
      表格渲染显示
```

### 3. 实时更新

```
WebSocket收到snmpDeviceBatch消息
          ↓
   PubSub发布事件通知
          ↓
  SNMPDevicesTab订阅者触发
          ↓
   重新加载localforage数据
          ↓
    计算属性自动更新
          ↓
      表格UI刷新
```

---

## UI界面变化

### 1. 筛选区域新增状态下拉框

```vue
<a-select
  v-model:value="filters.status"
  placeholder="状态"
  allow-clear
  style="width: 120px"
>
  <a-select-option value="success">在线</a-select-option>
  <a-select-option value="error">离线</a-select-option>
  <a-select-option value="unknown">未知</a-select-option>
</a-select>
```

### 2. 表格新增状态列

| 列名 | 位置 | 宽度 | 说明 |
|------|------|------|------|
| 状态 | IP地址后 | 80px | 显示在线/离线/未知状态 |

### 3. 状态标签样式

| 状态 | 颜色 | 文本 | Tooltip |
|------|------|------|---------|
| success | 绿色 | 在线 | 最后更新时间 |
| error | 红色 | 离线 | 错误信息 |
| unknown | 灰色 | 未知 | 无 |

---

## 状态说明

### success（在线）

- **含义**: SNMP轮询成功，设备可达
- **数据来源**: localforage中type='success'的记录
- **显示**: 绿色Tag，鼠标悬停显示最后更新时间
- **示例**: "最后更新: 2025-10-17 14:30:25"

### error（离线）

- **含义**: SNMP轮询失败，设备不可达
- **数据来源**: localforage中type='error'的记录
- **显示**: 红色Tag，鼠标悬停显示错误信息
- **示例**: "轮询超时(5秒)" 或 "SNMP连接超时或配置错误"

### unknown（未知）

- **含义**: 
  1. 新添加的设备，还未进行SNMP轮询
  2. localforage中没有该IP的记录
- **数据来源**: snmpDevicesStatus中找不到对应IP
- **显示**: 灰色Tag

---

## 代码示例

### 完整的状态处理流程

```javascript
// 1. 从localforage加载状态
const snmpDevicesStatus = ref({})

const loadSNMPDevicesStatus = async () => {
  const devices = await SNMPStorage.getAllDevices()
  // 结构: { "192.168.1.1": { type: "success", ... }, ... }
  snmpDevicesStatus.value = devices
}

// 2. 为设备添加状态
const switchesWithStatus = computed(() => {
  return props.switches.map(sw => {
    const snmpData = snmpDevicesStatus.value[sw.ip]
    return {
      ...sw,
      status: snmpData?.type || 'unknown',
      statusText: getStatusText(snmpData?.type),
      lastUpdate: snmpData?.updateTime,
      errorMsg: snmpData?.error
    }
  })
})

// 3. 状态筛选
const filteredSwitches = computed(() => {
  let result = switchesWithStatus.value
  
  // ... 其他筛选条件 ...
  
  if (filters.value.status) {
    result = result.filter(item => item.status === filters.value.status)
  }
  
  return result
})

// 4. 监听更新
onMounted(async () => {
  await loadSNMPDevicesStatus()
  
  PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, async () => {
    await loadSNMPDevicesStatus()
  })
})
```

---

## 使用场景

### 1. 查看所有在线设备

```
1. 点击"状态"下拉框
2. 选择"在线"
3. 表格自动过滤，只显示在线设备
```

### 2. 查看离线设备

```
1. 点击"状态"下拉框
2. 选择"离线"
3. 表格显示所有离线设备及错误原因
```

### 3. 查看设备最后更新时间

```
1. 找到在线设备（绿色Tag）
2. 鼠标悬停在"在线"Tag上
3. 显示提示: "最后更新: 2025-10-17 14:30:25"
```

### 4. 查看离线原因

```
1. 找到离线设备（红色Tag）
2. 鼠标悬停在"离线"Tag上
3. 显示错误信息: "轮询超时(5秒)"
```

### 5. 组合筛选

```
筛选条件:
- 设备类型: 交换机
- 状态: 离线

结果: 显示所有离线的交换机设备
```

---

## 性能优化

### 1. 使用计算属性

```javascript
// 自动缓存，只在依赖变化时重新计算
const switchesWithStatus = computed(() => {
  // ...
})
```

### 2. 避免重复加载

```javascript
// 只在必要时加载
onMounted(async () => {
  await loadSNMPDevicesStatus() // 初始加载一次
})

// WebSocket更新时才重新加载
PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, async () => {
  await loadSNMPDevicesStatus()
})
```

### 3. 快速查找

```javascript
// 使用对象而非数组，O(1)查找
const snmpDevicesStatus = ref({})  // { ip: data }
const snmpData = snmpDevicesStatus.value[sw.ip]  // 快速查找
```

---

## 注意事项

### 1. IP地址必须匹配

后端设备的IP地址必须与SNMP轮询的IP地址完全一致，否则无法匹配状态。

### 2. 新设备状态为"未知"

新添加的设备需要等待一轮SNMP轮询后才会有状态（默认60秒轮询间隔）。

### 3. localforage数据持久化

即使刷新页面，设备状态也会从localforage中恢复，无需等待新的轮询。

### 4. 状态更新延迟

WebSocket推送是实时的，但表格刷新可能有短暂延迟（通常<100ms）。

---

## 故障排查

### 1. 状态一直显示"未知"

**可能原因**:
- SNMP轮询器未启动
- IP地址不匹配
- localforage数据为空

**解决方法**:
```javascript
// 检查localforage数据
localforage.getItem('snmpDevices').then(console.log)

// 检查WebSocket连接
console.log(PubSub)
```

### 2. 状态不更新

**可能原因**:
- WebSocket未连接
- PubSub订阅失败
- 轮询器未运行

**解决方法**:
```javascript
// 手动触发更新
await loadSNMPDevicesStatus()

// 检查订阅
console.log('订阅状态:', unsubscribe)
```

### 3. 状态与实际不符

**可能原因**:
- 缓存数据过期
- SNMP配置错误
- 网络延迟

**解决方法**:
```javascript
// 清除缓存重新加载
await SNMPStorage.clearAll()
await loadSNMPDevicesStatus()
```

---

## 未来扩展

### 1. 状态历史记录

```javascript
// 记录状态变化历史
const statusHistory = ref([])

const trackStatusChange = (device, oldStatus, newStatus) => {
  statusHistory.value.push({
    ip: device.ip,
    oldStatus,
    newStatus,
    timestamp: Date.now()
  })
}
```

### 2. 状态告警

```javascript
// 设备离线时弹出通知
if (record.status === 'error') {
  notification.error({
    message: '设备离线',
    description: `${record.ip} (${record.device_name}) 已离线`
  })
}
```

### 3. 批量操作

```vue
<!-- 批量重启离线设备 -->
<a-button @click="restartOfflineDevices">
  重启所有离线设备
</a-button>
```

---

## 版本历史

- **v1.0** (2025-10): 初始实现，支持基本的状态显示和筛选
