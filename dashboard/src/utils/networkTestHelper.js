/**
 * 网络拓扑监控页面测试示例
 * 
 * 本文件演示如何模拟 WebSocket 数据以测试 Network.vue 的功能
 */

// 模拟设备状态更新
export function simulateDeviceStatus(wsInstance, deviceId, isOnline) {
  const statusData = {
    type: 'deviceStatus',
    data: {
      device_id: deviceId,
      status: isOnline ? 'online' : 'offline',
      online: isOnline,
      timestamp: new Date().toISOString()
    }
  }

  // 模拟 WebSocket 消息
  if (wsInstance && wsInstance.socket) {
    const event = new MessageEvent('message', {
      data: JSON.stringify(statusData)
    })
    wsInstance.socket.onmessage(event)
  }

  console.log('模拟设备状态更新:', statusData)
}

// 模拟 SNMP 设备更新（包含流量数据）
export function simulateSnmpDeviceUpdate(wsInstance, switchId, interfaces) {
  const snmpData = {
    type: 'snmpDeviceUpdate',
    data: {
      switch_id: switchId,
      ip: '192.168.1.1',
      device_info: {
        sysName: '核心交换机',
        sysUpTime: 86400000,
        sysDescr: 'Cisco Switch'
      },
      interface_info: {
        interfaces: interfaces.map((iface, index) => ({
          index: index + 1,
          name: iface.name || `GigabitEthernet0/${index + 1}`,
          in_octets_rate: iface.inRate || 0,
          out_octets_rate: iface.outRate || 0,
          connected_device_id: iface.connectedDeviceId || null,
          status: 'up'
        }))
      },
      timestamp: new Date().toISOString()
    }
  }

  // 模拟 WebSocket 消息
  if (wsInstance && wsInstance.socket) {
    const event = new MessageEvent('message', {
      data: JSON.stringify(snmpData)
    })
    wsInstance.socket.onmessage(event)
  }

  console.log('模拟 SNMP 设备更新:', snmpData)
}

// 模拟场景：设备从离线到在线
export function simulateDeviceOnlineScenario(wsInstance, deviceId) {
  console.log(`\n=== 场景: 设备 ${deviceId} 上线 ===`)

  // 1. 初始状态：离线
  simulateDeviceStatus(wsInstance, deviceId, false)

  // 2. 2秒后上线
  setTimeout(() => {
    simulateDeviceStatus(wsInstance, deviceId, true)
  }, 2000)
}

// 模拟场景：交换机接口流量变化
export function simulateTrafficFlowScenario(wsInstance, switchId, connectedDeviceId) {
  console.log(`\n=== 场景: 交换机 ${switchId} 流量变化 ===`)

  let trafficLevel = 0
  const interval = setInterval(() => {
    // 模拟流量波动：0 -> 高流量 -> 低流量 -> 0
    trafficLevel = (trafficLevel + 1) % 4

    let inRate = 0
    let outRate = 0

    switch (trafficLevel) {
      case 0:
        inRate = 0
        outRate = 0
        console.log('无流量')
        break
      case 1:
        inRate = 5000000  // 5 Mbps
        outRate = 3000000  // 3 Mbps
        console.log('低流量')
        break
      case 2:
        inRate = 50000000  // 50 Mbps
        outRate = 30000000  // 30 Mbps
        console.log('中等流量')
        break
      case 3:
        inRate = 100000000  // 100 Mbps
        outRate = 80000000  // 80 Mbps
        console.log('高流量')
        break
    }

    simulateSnmpDeviceUpdate(wsInstance, switchId, [
      {
        name: 'GigabitEthernet0/1',
        inRate: inRate,
        outRate: outRate,
        connectedDeviceId: connectedDeviceId
      }
    ])
  }, 3000)

  // 20秒后停止
  setTimeout(() => {
    clearInterval(interval)
    console.log('场景结束')
  }, 20000)
}

// 模拟场景：多设备状态变化
export function simulateMultiDeviceScenario(wsInstance, deviceIds) {
  console.log(`\n=== 场景: 多设备状态变化 ===`)

  deviceIds.forEach((deviceId, index) => {
    setTimeout(() => {
      // 随机在线或离线
      const isOnline = Math.random() > 0.3
      simulateDeviceStatus(wsInstance, deviceId, isOnline)
    }, index * 1000)
  })
}

// 使用示例（在浏览器控制台运行）
export function runTestScenarios() {
  console.log('开始测试场景...')
  console.log('请确保已经打开 Network.vue 页面')

  // 获取 WebSocket 实例（需要在实际环境中获取）
  // const wsInstance = Ws.getInstance()

  // 场景 1: 单个设备上线
  // simulateDeviceOnlineScenario(wsInstance, 'device_001')

  // 场景 2: 流量变化
  // simulateTrafficFlowScenario(wsInstance, 'switch_001', 'device_002')

  // 场景 3: 多设备状态变化
  // simulateMultiDeviceScenario(wsInstance, [
  //   'device_001',
  //   'device_002',
  //   'device_003',
  //   'device_004',
  //   'device_005'
  // ])
}

// 在浏览器控制台使用的便捷方法
if (typeof window !== 'undefined') {
  window.NetworkTestHelper = {
    simulateDeviceStatus,
    simulateSnmpDeviceUpdate,
    simulateDeviceOnlineScenario,
    simulateTrafficFlowScenario,
    simulateMultiDeviceScenario,
    runTestScenarios
  }

  console.log('测试工具已加载！使用 window.NetworkTestHelper 访问测试方法')
}

export default {
  simulateDeviceStatus,
  simulateSnmpDeviceUpdate,
  simulateDeviceOnlineScenario,
  simulateTrafficFlowScenario,
  simulateMultiDeviceScenario,
  runTestScenarios
}
