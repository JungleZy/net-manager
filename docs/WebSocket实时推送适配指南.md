# WebSocket实时推送适配指南

## 概述

后端SNMP轮询器已升级为**快进快出队列模式**，前端WebSocket已适配新的实时推送消息。

## 消息类型

### 1. 设备信息推送

``javascript
// 消息类型：snmpDeviceUpdate
// 特点：每个设备轮询完成后立即推送
{
    "type": "snmpDeviceUpdate",
    "data": {
        "type": "success",
        "ip": "192.168.1.1",
        "switch_id": 1,
        "snmp_version": "v2c",
        "device_info": {
            "sysDescr": "...",
            "sysName": "...",
            // ... 其他设备信息
        },
        "poll_time": 1697520000.123
    }
}
```

### 2. 接口信息推送

``javascript
// 消息类型：snmpInterfaceUpdate
// 特点：每个设备接口轮询完成后立即推送
{
    "type": "snmpInterfaceUpdate",
    "data": {
        "type": "success",
        "ip": "192.168.1.1",
        "switch_id": 1,
        "interface_info": [
            {
                "ifIndex": 1,
                "ifDescr": "GigabitEthernet0/1",
                "ifOperStatus": 1,
                // ... 其他接口信息
            }
        ],
        "interface_count": 24,
        "poll_time": 1697520000.123
    }
}
```

## 前端使用方法

### 订阅实时消息

``javascript
import { PubSub } from "@/common/utils/PubSub";
import { wsCode } from "@/common/ws/Ws";

export default {
    mounted() {
        // 订阅设备实时更新
        this.deviceUpdateSubscription = PubSub.subscribe(
            wsCode.SNMP_DEVICE_UPDATE, 
            this.handleDeviceUpdate
        );
        
        // 订阅接口实时更新
        this.interfaceUpdateSubscription = PubSub.subscribe(
            wsCode.SNMP_INTERFACE_UPDATE, 
            this.handleInterfaceUpdate
        );
    },
    
    beforeUnmount() {
        // 取消订阅
        if (this.deviceUpdateSubscription) {
            PubSub.unsubscribe(this.deviceUpdateSubscription);
        }
        if (this.interfaceUpdateSubscription) {
            PubSub.unsubscribe(this.interfaceUpdateSubscription);
        }
    },
    
    methods: {
        handleDeviceUpdate(deviceData) {
            console.log('设备更新:', deviceData);
            
            // 根据设备IP或ID更新界面
            const key = deviceData.ip || deviceData.switch_id;
            
            if (deviceData.type === 'success') {
                // 更新成功的设备信息
                this.updateDevice(key, deviceData);
            } else if (deviceData.type === 'error') {
                // 处理失败的设备
                this.handleDeviceError(key, deviceData.error);
            }
        },
        
        handleInterfaceUpdate(interfaceData) {
            console.log('接口更新:', interfaceData);
            
            // 根据设备IP或ID更新界面
            const key = interfaceData.ip || interfaceData.switch_id;
            
            if (interfaceData.type === 'success') {
                // 更新成功的接口信息
                this.updateInterface(key, interfaceData.interface_info);
            } else if (interfaceData.type === 'error') {
                // 处理失败的接口查询
                this.handleInterfaceError(key, interfaceData.error);
            }
        },
        
        updateDevice(key, deviceData) {
            // 实现具体的UI更新逻辑
            // 例如：更新表格行、更新状态图标等
        },
        
        updateInterface(key, interfaceInfo) {
            // 实现具体的UI更新逻辑
            // 例如：更新接口列表、更新流量图表等
        }
    }
}
```

### 2. 兼容批量消息（可选）

``javascript
export default {
    mounted() {
        // 同时订阅批量消息（向后兼容）
        this.deviceBatchSubscription = PubSub.subscribe(
            wsCode.SNMP_DEVICE_BATCH, 
            this.handleDeviceBatch
        );
        
        this.interfaceBatchSubscription = PubSub.subscribe(
            wsCode.SNMP_INTERFACE_BATCH, 
            this.handleInterfaceBatch
        );
    },
    
    methods: {
        handleDeviceBatch(devices) {
            // 批量处理设备数据
            devices.forEach(device => {
                const key = device.ip || device.switch_id;
                if (device.type === 'success') {
                    this.updateDevice(key, device);
                }
            });
        },
        
        handleInterfaceBatch(interfaces) {
            // 批量处理接口数据
            interfaces.forEach(intf => {
                const key = intf.ip || intf.switch_id;
                if (intf.type === 'success') {
                    this.updateInterface(key, intf.interface_info);
                }
            });
        }
    }
}
```

### 3. 从LocalForage读取数据

``javascript
import localforage from 'localforage';

export default {
    async mounted() {
        // 读取统一的SNMP数据（以switch_id为主键）
        const snmpData = await localforage.getItem('snmpData') || {};
        console.log('所有SNMP数据:', snmpData);
        
        // 遍历所有交换机
        Object.keys(snmpData).forEach(switchId => {
            const switchData = snmpData[switchId];
            console.log(`交换机 ${switchId}:`);
            console.log('  - IP:', switchData.ip);
            console.log('  - 设备信息:', switchData.device_info);
            console.log('  - 接口信息:', switchData.interface_info);
        });
        
        // 读取统计信息
        const snmpSummary = await localforage.getItem('snmpSummary');
        console.log('统计信息:', snmpSummary);
    },
    
    methods: {
        // 通过switch_id获取完整数据
        async getSwitchData(switchId) {
            const snmpData = await localforage.getItem('snmpData') || {};
            return snmpData[switchId];
        },
        
        // 通过switch_id获取设备信息
        async getDeviceInfo(switchId) {
            const snmpData = await localforage.getItem('snmpData') || {};
            return snmpData[switchId]?.device_info;
        },
        
        // 通过switch_id获取接口信息
        async getInterfaceInfo(switchId) {
            const snmpData = await localforage.getItem('snmpData') || {};
            return snmpData[switchId]?.interface_info;
        },
        
        // 获取所有在线的交换机
        async getOnlineSwitches() {
            const snmpData = await localforage.getItem('snmpData') || {};
            return Object.values(snmpData).filter(sw => 
                sw.device_info?.type === 'success' || 
                sw.interface_info?.type === 'success'
            );
        }
    }
}
```

## 数据结构

### LocalForage存储结构（重要）

#### snmpData（统一SNMP数据，以switch_id为主键）
``javascript
{
    // switch_id 1
    "1": {
        "switch_id": 1,
        "ip": "192.168.1.1",
        "device_info": {           // 设备信息（来自continuous_poller）
            "type": "success",
            "ip": "192.168.1.1",
            "switch_id": 1,
            "device_info": {
                "sysDescr": "Cisco IOS...",
                "sysName": "Switch-01",
                // ... 其他设备信息
            },
            "poll_time": 1697520000.123
        },
        "interface_info": {        // 接口信息（来自interface_poller）
            "type": "success",
            "ip": "192.168.1.1",
            "switch_id": 1,
            "interface_info": [
                {
                    "ifIndex": 1,
                    "ifDescr": "GigabitEthernet0/1",
                    "ifOperStatus": 1,
                    // ... 其他接口信息
                }
            ],
            "interface_count": 24,
            "poll_time": 1697520000.456
        },
        "device_update_time": "2025-10-17T10:30:00.000Z",
        "interface_update_time": "2025-10-17T10:30:30.000Z",
        "last_update_time": "2025-10-17T10:30:30.000Z"
    },
    
    // switch_id 2
    "2": {
        "switch_id": 2,
        "ip": "192.168.1.2",
        "device_info": {...},
        "interface_info": {...},
        "device_update_time": "2025-10-17T10:30:05.000Z",
        "interface_update_time": "2025-10-17T10:30:35.000Z",
        "last_update_time": "2025-10-17T10:30:35.000Z"
    },
    // ...
}
```

#### snmpSummary（统计信息）
``javascript
{
    "total": 100,
    "success": 95,
    "error": 5,
    "lastUpdateTime": "2025-10-17T10:30:00.000Z",
    "timestamp": 1697520000000
}
```

## 性能优化建议

### 1. 消息节流

对于高频更新的场景，建议使用节流处理：

``javascript
import { throttle } from 'lodash-es';

export default {
    created() {
        // 节流处理，每500ms最多更新一次
        this.throttledUpdate = throttle(this.updateUI, 500);
    },
    
    methods: {
        handleDeviceUpdate(deviceData) {
            // 先保存数据
            this.deviceDataCache.set(deviceData.ip, deviceData);
            
            // 节流更新UI
            this.throttledUpdate();
        },
        
        updateUI() {
            // 批量更新UI
            this.deviceDataCache.forEach((data, ip) => {
                this.updateDevice(ip, data);
            });
            this.deviceDataCache.clear();
        }
    }
}
```

### 2. 虚拟滚动

对于大量设备的列表展示，建议使用虚拟滚动：

``vue
<template>
    <virtual-list
        :data-key="'ip'"
        :data-sources="deviceList"
        :data-component="DeviceItem"
        :estimate-size="60"
    />
</template>
```

### 3. 增量更新

只更新变化的部分，避免全量刷新：

``javascript
methods: {
    updateDevice(key, newData) {
        const index = this.deviceList.findIndex(d => d.ip === key);
        if (index >= 0) {
            // 使用Vue响应式更新
            Object.assign(this.deviceList[index], newData);
        } else {
            // 新设备，添加到列表
            this.deviceList.push(newData);
        }
    }
}
```

## 错误处理

### 1. 处理失败消息

``javascript
methods: {
    handleDeviceUpdate(deviceData) {
        if (deviceData.type === 'error') {
            // 显示错误提示
            this.$message.error(
                `设备 ${deviceData.ip} 轮询失败: ${deviceData.error}`
            );
            
            // 标记设备为离线状态
            this.markDeviceOffline(deviceData.ip);
        }
    }
}
```

### 2. 超时处理

``javascript
data() {
    return {
        deviceTimeouts: new Map()
    }
},

methods: {
    handleDeviceUpdate(deviceData) {
        const ip = deviceData.ip;
        
        // 清除旧的超时定时器
        if (this.deviceTimeouts.has(ip)) {
            clearTimeout(this.deviceTimeouts.get(ip));
        }
        
        // 设置新的超时定时器（2分钟无更新视为离线）
        const timeoutId = setTimeout(() => {
            this.markDeviceOffline(ip);
        }, 120000);
        
        this.deviceTimeouts.set(ip, timeoutId);
    }
}
```

## 迁移指南

### 从LocalForage读取数据

``javascript
// 读取统一的SNMP数据（以switch_id为主键）
const snmpData = await localforage.getItem('snmpData') || {};

// 遍历所有交换机
Object.keys(snmpData).forEach(switchId => {
    const switchData = snmpData[switchId];
    console.log(`交换机 ${switchId}:`, switchData);
});
```

## 调试技巧

### 1. 查看消息日志

打开浏览器控制台，可以看到：
- `设备更新 - 192.168.1.1 (1.23s)` - 设备更新日志
- `接口更新 - 192.168.1.1 (2.45s)` - 接口更新日志

### 2. 监控更新频率

``javascript
let updateCount = 0;
let startTime = Date.now();

PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, () => {
    updateCount++;
    const elapsed = (Date.now() - startTime) / 1000;
    console.log(`更新频率: ${(updateCount / elapsed).toFixed(2)} 次/秒`);
});
```

### 3. 查看存储数据

``javascript
// 在浏览器控制台执行
localforage.getItem('snmpDevices').then(data => console.log(data));
localforage.getItem('snmpInterfaces').then(data => console.log(data));
```

## 常见问题

### Q1: 如何判断设备是否在线？

A: 检查消息的`type`字段：
- `type: "success"` - 设备在线
- `type: "error"` - 设备离线或轮询失败

### Q2: 如何提高UI响应速度？

A: 
1. 使用节流处理高频更新
2. 采用虚拟滚动展示大量数据
3. 只更新变化的部分
4. 使用Web Worker处理数据

### Q3: 数据会丢失吗？

A: 不会。所有消息都会保存到LocalForage，刷新页面后可以恢复。

## 总结

✅ **新特性**
- 实时推送，秒级响应
- 单设备更新，精细控制
- 自动持久化，数据安全

✅ **性能优化**
- 节流处理
- 虚拟滚动
- 增量更新

---

**更新时间**: 2025-10-17  
**适用版本**: WebSocket 2.0（队列模式）
