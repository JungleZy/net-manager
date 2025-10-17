# SNMP设备数据LocalForage存储实现

## 实现概述

通过localforage实现SNMP设备数据的本地持久化存储，支持离线访问和快速查询。

---

## 文件清单

### 1. 核心文件

| 文件 | 说明 |
|------|------|
| [`src/common/ws/Ws.js`](e:\workspace\project\net-manager\dashboard\src\common\ws\Ws.js) | WebSocket处理，自动保存SNMP数据 |
| [`src/common/utils/SNMPStorage.js`](e:\workspace\project\net-manager\dashboard\src\common\utils\SNMPStorage.js) | SNMP存储工具类 |

### 2. 文档文件

| 文件 | 说明 |
|------|------|
| [`SNMP_STORAGE_GUIDE.md`](e:\workspace\project\net-manager\dashboard\src\common\utils\SNMP_STORAGE_GUIDE.md) | 详细使用指南 |
| `SNMP_LOCALFORAGE_IMPLEMENTATION.md` | 本文档 |

### 3. 测试文件

| 文件 | 说明 |
|------|------|
| [`src/views/test/SNMPStorageTest.vue`](e:\workspace\project\net-manager\dashboard\src\views\test\SNMPStorageTest.vue) | 功能测试页面 |

---

## 实现细节

### 1. WebSocket自动保存 ([Ws.js](e:\workspace\project\net-manager\dashboard\src\common\ws\Ws.js))

#### 修改内容

在接收到 `snmpDeviceBatch` 消息时，自动保存到localforage：

```javascript
case "snmpDeviceBatch":
  console.log("snmpDeviceBatch", data.data);
  // 保存SNMP设备数据到localforage
  this.saveSNMPDeviceData(data.data, data.summary);
  PubSub.publish(wsCode.SNMP_DEVICE_BATCH, data.data);
  break;
```

#### 保存方法

```javascript
async saveSNMPDeviceData(devices, summary) {
  try {
    // 获取现有数据
    let snmpDevices = await localforage.getItem('snmpDevices') || {};
    
    // 更新每个设备
    devices.forEach(device => {
      const key = device.ip || device.switch_id;
      if (key) {
        snmpDevices[key] = {
          ...device,
          updateTime: new Date().toISOString(),
          timestamp: Date.now()
        };
      }
    });
    
    // 保存设备数据
    await localforage.setItem('snmpDevices', snmpDevices);
    
    // 保存统计信息
    if (summary) {
      await localforage.setItem('snmpSummary', {
        ...summary,
        lastUpdateTime: new Date().toISOString(),
        timestamp: Date.now()
      });
    }
    
    console.log(`SNMP设备数据已保存: ${devices.length}个设备`);
  } catch (error) {
    console.error('SNMP设备数据保存失败:', error);
  }
}
```

### 2. 存储工具类 ([SNMPStorage.js](e:\workspace\project\net-manager\dashboard\src\common\utils\SNMPStorage.js))

#### 主要方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `getAllDevices()` | 获取所有设备 | `Promise<Object>` |
| `getDevice(key)` | 获取单个设备 | `Promise<Object\|null>` |
| `getOnlineDevices()` | 获取在线设备 | `Promise<Array>` |
| `getOfflineDevices()` | 获取离线设备 | `Promise<Array>` |
| `getSummary()` | 获取统计信息 | `Promise<Object\|null>` |
| `getDeviceCount()` | 获取设备数量统计 | `Promise<Object>` |
| `searchDevices(text)` | 搜索设备 | `Promise<Array>` |
| `isDeviceOnline(key)` | 检查设备是否在线 | `Promise<boolean>` |
| `clearAll()` | 清除所有数据 | `Promise<void>` |

#### 使用示例

```javascript
import SNMPStorage from '@/common/utils/SNMPStorage';

// 获取所有设备
const devices = await SNMPStorage.getAllDevices();

// 获取在线设备
const onlineDevices = await SNMPStorage.getOnlineDevices();

// 搜索设备
const results = await SNMPStorage.searchDevices('192.168');

// 获取统计
const count = await SNMPStorage.getDeviceCount();
// { total: 100, online: 92, offline: 8 }
```

---

## 数据结构

### snmpDevices（设备数据）

```javascript
{
  "192.168.1.1": {
    "type": "success",              // 设备状态: success/error
    "ip": "192.168.1.1",           // IP地址
    "switch_id": 1,                // 交换机ID
    "snmp_version": "v2c",         // SNMP版本
    "device_info": {               // 设备信息（仅在线时有）
      "description": "...",
      "name": "...",
      "location": "...",
      "uptime": "...",
      "object_id": "..."
    },
    "poll_time": 1760670956.123,   // 轮询时间
    "updateTime": "2025-10-17...", // ISO格式更新时间
    "timestamp": 1760670956000     // 时间戳
  },
  "192.168.1.2": {
    "type": "error",               // 离线设备
    "ip": "192.168.1.2",
    "switch_id": 2,
    "error": "轮询超时(5秒)",      // 错误信息
    "poll_time": 1760670956.456,
    "updateTime": "2025-10-17...",
    "timestamp": 1760670956000
  }
}
```

### snmpSummary（统计信息）

```javascript
{
  "total": 100,                    // 总设备数
  "success": 92,                   // 在线数
  "error": 8,                      // 离线数
  "lastUpdateTime": "2025-10-17...", // 最后更新时间
  "timestamp": 1760670956000       // 时间戳
}
```

---

## 工作流程

### 1. 数据接收和保存

```
服务器轮询 → WebSocket推送 → Ws.js接收
           ↓
    saveSNMPDeviceData()
           ↓
    LocalForage存储
           ↓
    PubSub发布事件
```

### 2. 前端读取

```
组件挂载 → SNMPStorage.getAllDevices()
        ↓
   LocalForage读取
        ↓
     渲染展示
```

### 3. 实时更新

```
WebSocket消息 → PubSub订阅者
             ↓
        自动重新加载
             ↓
          更新UI
```

---

## 使用场景

### 场景1：设备列表页面

```vue
<script setup>
import { ref, onMounted } from 'vue';
import SNMPStorage from '@/common/utils/SNMPStorage';
import { PubSub } from '@/common/utils/PubSub';
import { wsCode } from '@/common/ws/Ws';

const devices = ref([]);

const loadDevices = async () => {
  const data = await SNMPStorage.getAllDevices();
  devices.value = Object.values(data);
};

onMounted(() => {
  loadDevices();
  
  // 监听更新
  PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, () => {
    loadDevices();
  });
});
</script>
```

### 场景2：设备状态监控

```vue
<script setup>
import { ref, onMounted } from 'vue';
import SNMPStorage from '@/common/utils/SNMPStorage';

const stats = ref({ total: 0, online: 0, offline: 0 });

const updateStats = async () => {
  stats.value = await SNMPStorage.getDeviceCount();
};

onMounted(() => {
  updateStats();
  // 每10秒更新一次
  setInterval(updateStats, 10000);
});
</script>
```

### 场景3：设备搜索

```vue
<template>
  <input v-model="searchText" @input="handleSearch" />
  <div v-for="device in results" :key="device.ip">
    {{ device.ip }} - {{ device.device_info?.name }}
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SNMPStorage from '@/common/utils/SNMPStorage';

const searchText = ref('');
const results = ref([]);

const handleSearch = async () => {
  results.value = await SNMPStorage.searchDevices(searchText.value);
};
</script>
```

---

## 性能优化

### 1. 数据量优化

- **设备数 < 100**: 直接全量加载
- **设备数 100-500**: 使用虚拟滚动
- **设备数 > 500**: 分页加载

### 2. 缓存策略

```javascript
// 组件内缓存
let cachedDevices = null;
let cacheTime = 0;

const getDevicesWithCache = async () => {
  const now = Date.now();
  if (cachedDevices && (now - cacheTime < 5000)) {
    return cachedDevices;
  }
  cachedDevices = await SNMPStorage.getAllDevices();
  cacheTime = now;
  return cachedDevices;
};
```

### 3. 异步加载

```javascript
// 先加载统计，再加载详细数据
const loadData = async () => {
  // 快速显示统计
  const summary = await SNMPStorage.getSummary();
  updateSummary(summary);
  
  // 后台加载详细数据
  setTimeout(async () => {
    const devices = await SNMPStorage.getAllDevices();
    updateDevices(devices);
  }, 0);
};
```

---

## 测试方法

### 1. 访问测试页面

```
http://localhost:5173/test/snmp-storage
```

### 2. 浏览器控制台测试

```javascript
// 打开浏览器开发者工具
import SNMPStorage from '@/common/utils/SNMPStorage';

// 测试各种方法
const devices = await SNMPStorage.getAllDevices();
console.log('设备数量:', Object.keys(devices).length);

const online = await SNMPStorage.getOnlineDevices();
console.log('在线设备:', online.length);

const summary = await SNMPStorage.getSummary();
console.log('统计信息:', summary);
```

### 3. LocalForage调试

```javascript
// 查看存储的原始数据
localforage.getItem('snmpDevices').then(console.log);
localforage.getItem('snmpSummary').then(console.log);

// 查看所有keys
localforage.keys().then(console.log);

// 清除数据
localforage.clear();
```

---

## 注意事项

### 1. 浏览器存储限制

- **IndexedDB**: 通常50MB-250MB
- **隐私模式**: 数据不会持久化
- **清除缓存**: 会删除所有数据

### 2. 数据同步

- 数据由WebSocket自动更新
- 刷新页面会从本地读取
- 不支持多标签同步（可以考虑使用BroadcastChannel）

### 3. 错误处理

所有方法都有 try-catch，失败时返回默认值：
- `getAllDevices()`: 返回 `{}`
- `getOnlineDevices()`: 返回 `[]`
- `getSummary()`: 返回 `null`

---

## 未来扩展

### 1. 数据导入导出

```javascript
// 导入
const importData = async (jsonFile) => {
  const data = JSON.parse(await jsonFile.text());
  await localforage.setItem('snmpDevices', data.devices);
  await localforage.setItem('snmpSummary', data.summary);
};

// 导出
const exportData = async () => {
  const devices = await SNMPStorage.getAllDevices();
  const summary = await SNMPStorage.getSummary();
  return { devices, summary };
};
```

### 2. 历史数据记录

```javascript
// 保存历史快照
const saveSnapshot = async () => {
  const devices = await SNMPStorage.getAllDevices();
  const timestamp = Date.now();
  await localforage.setItem(`snmp_snapshot_${timestamp}`, devices);
};

// 加载历史快照
const loadSnapshot = async (timestamp) => {
  return await localforage.getItem(`snmp_snapshot_${timestamp}`);
};
```

### 3. 数据同步到后端

```javascript
// 定期同步到服务器
const syncToServer = async () => {
  const devices = await SNMPStorage.getAllDevices();
  await fetch('/api/snmp/sync', {
    method: 'POST',
    body: JSON.stringify({ devices })
  });
};
```

---

## 版本历史

- **v1.0** (2025-10): 初始实现，支持基本的存储和查询功能
