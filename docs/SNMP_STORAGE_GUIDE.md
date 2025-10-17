# SNMP设备数据本地存储使用指南

## 概述

通过localforage实现SNMP设备数据的本地持久化存储，支持离线查看和快速访问。

---

## 数据结构

### 存储的数据

#### 1. snmpDevices（设备数据）

存储格式：
```javascript
{
  "192.168.1.1": {
    "type": "success",
    "ip": "192.168.1.1",
    "switch_id": 1,
    "snmp_version": "v2c",
    "device_info": {
      "description": "Cisco Switch",
      "name": "SW-Core-01",
      "location": "Server Room",
      "uptime": "12345678",
      "object_id": "1.3.6.1.4.1.9.1.1"
    },
    "poll_time": 1760670956.123,
    "updateTime": "2025-10-17T12:00:00.000Z",
    "timestamp": 1760670956000
  },
  "192.168.1.2": {
    "type": "error",
    "ip": "192.168.1.2",
    "switch_id": 2,
    "error": "轮询超时(5秒)",
    "poll_time": 1760670956.456,
    "updateTime": "2025-10-17T12:00:00.000Z",
    "timestamp": 1760670956000
  }
}
```

#### 2. snmpSummary（统计信息）

存储格式：
```javascript
{
  "total": 100,
  "success": 92,
  "error": 8,
  "lastUpdateTime": "2025-10-17T12:00:00.000Z",
  "timestamp": 1760670956000
}
```

---

## API使用指南

### 导入工具类

```javascript
import SNMPStorage from '@/common/utils/SNMPStorage';
```

### 常用方法

#### 1. 获取所有设备

```javascript
// 获取所有设备数据（对象格式）
const devices = await SNMPStorage.getAllDevices();
console.log(devices);
// 输出: { "192.168.1.1": {...}, "192.168.1.2": {...} }
```

#### 2. 获取单个设备

```javascript
// 根据IP获取设备
const device = await SNMPStorage.getDevice('192.168.1.1');
if (device) {
  console.log('设备名称:', device.device_info.name);
  console.log('设备状态:', device.type);
}
```

#### 3. 获取在线/离线设备

```javascript
// 获取所有在线设备（数组格式）
const onlineDevices = await SNMPStorage.getOnlineDevices();
console.log(`在线设备数: ${onlineDevices.length}`);

// 获取所有离线设备
const offlineDevices = await SNMPStorage.getOfflineDevices();
console.log(`离线设备数: ${offlineDevices.length}`);
```

#### 4. 获取统计信息

```javascript
// 获取汇总统计
const summary = await SNMPStorage.getSummary();
console.log(`总设备数: ${summary.total}`);
console.log(`在线: ${summary.success}, 离线: ${summary.error}`);

// 或者实时计算统计
const count = await SNMPStorage.getDeviceCount();
console.log(count);
// 输出: { total: 100, online: 92, offline: 8 }
```

#### 5. 搜索设备

```javascript
// 根据IP、名称、描述搜索
const results = await SNMPStorage.searchDevices('192.168');
console.log(`找到 ${results.length} 个匹配的设备`);
```

#### 6. 检查设备状态

```javascript
// 检查设备是否在线
const isOnline = await SNMPStorage.isDeviceOnline('192.168.1.1');
if (isOnline) {
  console.log('设备在线');
} else {
  console.log('设备离线');
}

// 获取设备最后更新时间
const updateTime = await SNMPStorage.getDeviceUpdateTime('192.168.1.1');
console.log('最后更新:', updateTime);
```

#### 7. 清除数据

```javascript
// 清除所有SNMP设备数据
await SNMPStorage.clearAll();
```

---

## Vue组件中使用示例

### 示例1：设备列表页面

```vue
<template>
  <div class="device-list">
    <div class="stats">
      <span>总数: {{ stats.total }}</span>
      <span>在线: {{ stats.online }}</span>
      <span>离线: {{ stats.offline }}</span>
    </div>
    
    <div class="search">
      <input 
        v-model="searchText" 
        @input="handleSearch"
        placeholder="搜索设备..."
      />
    </div>
    
    <table>
      <thead>
        <tr>
          <th>IP地址</th>
          <th>设备名称</th>
          <th>状态</th>
          <th>更新时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="device in filteredDevices" :key="device.ip">
          <td>{{ device.ip }}</td>
          <td>{{ device.device_info?.name || '-' }}</td>
          <td>
            <span :class="device.type === 'success' ? 'online' : 'offline'">
              {{ device.type === 'success' ? '在线' : '离线' }}
            </span>
          </td>
          <td>{{ formatTime(device.updateTime) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SNMPStorage from '@/common/utils/SNMPStorage';
import { PubSub } from '@/common/utils/PubSub';
import { wsCode } from '@/common/ws/Ws';

const stats = ref({ total: 0, online: 0, offline: 0 });
const filteredDevices = ref([]);
const searchText = ref('');

// 加载数据
const loadDevices = async () => {
  // 加载统计信息
  stats.value = await SNMPStorage.getDeviceCount();
  
  // 加载设备列表
  const devices = await SNMPStorage.getAllDevices();
  filteredDevices.value = Object.values(devices);
};

// 搜索处理
const handleSearch = async () => {
  const results = await SNMPStorage.searchDevices(searchText.value);
  filteredDevices.value = results;
};

// 监听WebSocket更新
onMounted(() => {
  // 初始加载
  loadDevices();
  
  // 订阅SNMP设备更新
  PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, async (data) => {
    console.log('收到SNMP设备更新');
    // 数据已由Ws.js自动保存到localforage
    // 重新加载显示
    await loadDevices();
  });
});

const formatTime = (time) => {
  return time ? new Date(time).toLocaleString('zh-CN') : '-';
};
</script>

<style scoped>
.online { color: #52c41a; }
.offline { color: #ff4d4f; }
</style>
```

### 示例2：设备详情页面

```vue
<template>
  <div v-if="device" class="device-detail">
    <h2>{{ device.device_info?.name || device.ip }}</h2>
    
    <div class="status">
      <span :class="isOnline ? 'online' : 'offline'">
        {{ isOnline ? '在线' : '离线' }}
      </span>
    </div>
    
    <div v-if="isOnline" class="info">
      <p><strong>IP地址:</strong> {{ device.ip }}</p>
      <p><strong>描述:</strong> {{ device.device_info.description }}</p>
      <p><strong>位置:</strong> {{ device.device_info.location }}</p>
      <p><strong>运行时间:</strong> {{ formatUptime(device.device_info.uptime) }}</p>
      <p><strong>最后更新:</strong> {{ formatTime(device.updateTime) }}</p>
    </div>
    
    <div v-else class="error">
      <p>错误信息: {{ device.error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import SNMPStorage from '@/common/utils/SNMPStorage';

const route = useRoute();
const device = ref(null);
const isOnline = ref(false);

onMounted(async () => {
  const ip = route.params.ip;
  device.value = await SNMPStorage.getDevice(ip);
  isOnline.value = await SNMPStorage.isDeviceOnline(ip);
});

const formatUptime = (uptime) => {
  // 格式化运行时间逻辑
  return uptime;
};

const formatTime = (time) => {
  return time ? new Date(time).toLocaleString('zh-CN') : '-';
};
</script>
```

---

## 自动更新机制

### WebSocket接收到数据时自动保存

在 [`Ws.js`](e:\workspace\project\net-manager\dashboard\src\common\ws\Ws.js) 中已实现自动保存：

```javascript
case "snmpDeviceBatch":
  // 自动保存到localforage
  this.saveSNMPDeviceData(data.data, data.summary);
  // 发布事件通知订阅者
  PubSub.publish(wsCode.SNMP_DEVICE_BATCH, data.data);
  break;
```

### 前端监听更新

```javascript
import { PubSub } from '@/common/utils/PubSub';
import { wsCode } from '@/common/ws/Ws';

PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, async (devices) => {
  console.log('收到设备更新，数据已自动保存');
  // 重新加载页面数据
  await refreshData();
});
```

---

## 性能优化建议

### 1. 大数据量优化

如果设备数量超过1000个，建议：

```javascript
// 使用虚拟滚动只渲染可见区域
import { RecycleScroller } from 'vue-virtual-scroller';

// 或者分页加载
const pageSize = 50;
const currentPage = ref(1);

const loadPage = async (page) => {
  const allDevices = await SNMPStorage.getAllDevices();
  const deviceArray = Object.values(allDevices);
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  return deviceArray.slice(start, end);
};
```

### 2. 缓存优化

```javascript
// 缓存经常访问的数据
let cachedDevices = null;
let cacheTime = 0;
const CACHE_TTL = 5000; // 5秒缓存

const getDevicesWithCache = async () => {
  const now = Date.now();
  if (cachedDevices && (now - cacheTime < CACHE_TTL)) {
    return cachedDevices;
  }
  
  cachedDevices = await SNMPStorage.getAllDevices();
  cacheTime = now;
  return cachedDevices;
};
```

### 3. 索引优化

```javascript
// 为常用查询建立索引
const buildIndex = (devices) => {
  const byIP = {};
  const byName = {};
  
  Object.values(devices).forEach(device => {
    byIP[device.ip] = device;
    if (device.device_info?.name) {
      byName[device.device_info.name] = device;
    }
  });
  
  return { byIP, byName };
};
```

---

## 数据管理

### 定期清理旧数据

```javascript
// 清理7天前的数据
const cleanOldData = async () => {
  const devices = await SNMPStorage.getAllDevices();
  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
  
  const cleanedDevices = {};
  Object.entries(devices).forEach(([key, device]) => {
    if (device.timestamp > sevenDaysAgo) {
      cleanedDevices[key] = device;
    }
  });
  
  await localforage.setItem('snmpDevices', cleanedDevices);
};
```

### 导出数据

```javascript
// 导出为JSON
const exportData = async () => {
  const devices = await SNMPStorage.getAllDevices();
  const summary = await SNMPStorage.getSummary();
  
  const exportData = {
    devices,
    summary,
    exportTime: new Date().toISOString()
  };
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: 'application/json'
  });
  
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `snmp-devices-${Date.now()}.json`;
  a.click();
};
```

---

## 注意事项

1. **浏览器兼容性**: localforage支持所有现代浏览器
2. **存储限制**: 浏览器IndexedDB通常有50MB-250MB的限制
3. **隐私模式**: 无痕模式下数据可能不会持久化
4. **跨域限制**: 不同域名下的数据互相隔离

---

## 版本历史

- **v1.0** (2025-10): 初始版本，支持SNMP设备数据本地存储
