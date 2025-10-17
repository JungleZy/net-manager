# WebSocket实时推送快速参考

## 📡 消息类型

### 设备信息
```javascript
// 实时更新
wsCode.SNMP_DEVICE_UPDATE → 单设备立即推送
```

### 接口信息
```javascript
// 实时更新
wsCode.SNMP_INTERFACE_UPDATE → 单接口立即推送
```

## 🚀 快速使用

### 订阅实时消息
```javascript
import { PubSub } from "@/common/utils/PubSub";
import { wsCode } from "@/common/ws/Ws";

// 设备更新
PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, (data) => {
    console.log('设备:', data.ip, data.device_info);
});

// 接口更新
PubSub.subscribe(wsCode.SNMP_INTERFACE_UPDATE, (data) => {
    console.log('接口:', data.ip, data.interface_info);
});
```

### 处理消息
```javascript
handleDeviceUpdate(deviceData) {
    if (deviceData.type === 'success') {
        // 更新设备
        this.updateDevice(deviceData.ip, deviceData);
    } else {
        // 处理错误
        this.handleError(deviceData.ip, deviceData.error);
    }
}
```

### 读取存储数据
```javascript
// 统一的SNMP数据（以switch_id为主键）
const snmpData = await localforage.getItem('snmpData');

// 获取指定交换机的完整数据
const switchData = snmpData[switchId];
const deviceInfo = switchData.device_info;      // 设备信息
const interfaceInfo = switchData.interface_info; // 接口信息

// 统计信息
const summary = await localforage.getItem('snmpSummary');
```

## 📊 数据结构

### 实时消息
```json
{
    "type": "snmpDeviceUpdate",
    "data": {
        "type": "success",
        "ip": "192.168.1.1",
        "switch_id": 1,
        "device_info": {...}
    }
}
```

### 存储格式（以switch_id为主键）
```javascript
{
    "1": {  // switch_id
        "switch_id": 1,
        "ip": "192.168.1.1",
        "device_info": {        // 设备信息
            "type": "success",
            "device_info": {...}
        },
        "interface_info": {     // 接口信息
            "type": "success",
            "interface_info": [...]
        },
        "device_update_time": "2025-10-17T10:30:00.000Z",
        "interface_update_time": "2025-10-17T10:30:30.000Z",
        "last_update_time": "2025-10-17T10:30:30.000Z"
    }
}
```

## ⚡ 性能优化

### 节流处理
```javascript
import { throttle } from 'lodash-es';

this.throttledUpdate = throttle(this.updateUI, 500);
```

### 增量更新
```javascript
updateDevice(ip, data) {
    const index = this.list.findIndex(d => d.ip === ip);
    if (index >= 0) {
        Object.assign(this.list[index], data);
    } else {
        this.list.push(data);
    }
}
```

## 🔧 常用代码

### 完整组件示例
```javascript
export default {
    data() {
        return {
            switchList: [],  // 交换机列表
            subscriptions: []
        }
    },
    
    async mounted() {
        // 加载已保存的数据
        await this.loadSavedData();
        
        // 订阅实时更新
        this.subscriptions.push(
            PubSub.subscribe(
                wsCode.SNMP_DEVICE_UPDATE, 
                this.handleDeviceUpdate
            ),
            PubSub.subscribe(
                wsCode.SNMP_INTERFACE_UPDATE, 
                this.handleInterfaceUpdate
            )
        );
    },
    
    beforeUnmount() {
        this.subscriptions.forEach(sub => {
            PubSub.unsubscribe(sub);
        });
    },
    
    methods: {
        async loadSavedData() {
            const snmpData = await localforage.getItem('snmpData') || {};
            this.switchList = Object.values(snmpData);
        },
        
        handleDeviceUpdate(data) {
            const switchId = data.switch_id;
            const index = this.switchList.findIndex(s => s.switch_id === switchId);
            
            if (data.type === 'success') {
                if (index >= 0) {
                    // 更新已存在的交换机
                    this.switchList[index].device_info = data;
                    this.switchList[index].device_update_time = new Date().toISOString();
                } else {
                    // 添加新的交换机
                    this.switchList.push({
                        switch_id: switchId,
                        ip: data.ip,
                        device_info: data,
                        interface_info: null,
                        device_update_time: new Date().toISOString(),
                        interface_update_time: null
                    });
                }
            }
        },
        
        handleInterfaceUpdate(data) {
            const switchId = data.switch_id;
            const index = this.switchList.findIndex(s => s.switch_id === switchId);
            
            if (data.type === 'success') {
                if (index >= 0) {
                    // 更新已存在的交换机
                    this.switchList[index].interface_info = data;
                    this.switchList[index].interface_update_time = new Date().toISOString();
                } else {
                    // 添加新的交换机
                    this.switchList.push({
                        switch_id: switchId,
                        ip: data.ip,
                        device_info: null,
                        interface_info: data,
                        device_update_time: null,
                        interface_update_time: new Date().toISOString()
                    });
                }
            }
        }
    }
}
```

## 🐛 调试

### 查看日志
```javascript
// 控制台会显示：
// 设备更新 - 192.168.1.1 (1.23s)
// 接口更新 - 192.168.1.1 (2.45s)
```

### 查看存储
```javascript
// 浏览器控制台执行
localforage.getItem('snmpData').then(console.log);
localforage.getItem('snmpSummary').then(console.log);
```

### 监控频率
```javascript
let count = 0;
PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, () => {
    console.log('更新次数:', ++count);
});
```

## ⚠️ 注意事项

1. **主键**: 使用`switch_id`而非`ip`作为主键
2. **数据结构**: 每个交换机包含`device_info`和`interface_info`两部分
3. **错误处理**: 检查`data.type`判断成功或失败
4. **性能**: 高频更新时使用节流
5. **存储**: 数据自动持久化到LocalForage的`snmpData`中

## 📚 文档

详细文档: `WebSocket实时推送适配指南.md`

---

**版本**: 2.0  
**更新**: 2025-10-17
