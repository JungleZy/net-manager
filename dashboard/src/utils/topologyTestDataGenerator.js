/**
 * 拓扑图测试数据生成器
 * 用于生成不同规模的网络拓扑测试数据
 */

/**
 * 生成随机ID
 */
const generateId = () => {
  return `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 生成随机设备类型
 */
const getRandomDeviceType = () => {
  const types = ['pc', 'laptop', 'server', 'printer', 'router', 'firewall']
  return types[Math.floor(Math.random() * types.length)]
}

/**
 * 生成随机状态
 */
const getRandomStatus = () => {
  return Math.random() > 0.3 ? 'online' : 'offline'
}

/**
 * 生成随机IP地址
 */
const generateRandomIP = (subnet = '192.168') => {
  const third = Math.floor(Math.random() * 255)
  const fourth = Math.floor(Math.random() * 255) + 1
  return `${subnet}.${third}.${fourth}`
}

/**
 * 生成三层网络拓扑结构
 * @param {number} deviceCount - 设备数量
 * @param {number} switchCount - 交换机数量
 * @returns {Object} 拓扑图数据
 */
export const generateThreeLayerTopology = (deviceCount = 20, switchCount = 2) => {
  const nodes = []
  const edges = []

  // 层次配置
  const layers = {
    core: { y: 100, switches: [] },      // 核心层
    distribution: { y: 300, switches: [] }, // 汇聚层
    access: { y: 500, switches: [] }     // 接入层
  }

  // 1. 生成核心交换机（1个）
  const coreSwitch = {
    id: generateId(),
    type: 'switch',
    x: 400,
    y: layers.core.y,
    properties: {
      width: 60,
      height: 60,
      status: 'online',
      data: {
        id: generateId(),
        name: '核心交换机',
        ip: '10.0.0.1'
      }
    },
    text: {
      x: 400,
      y: layers.core.y,
      value: '核心交换机'
    }
  }
  nodes.push(coreSwitch)
  layers.core.switches.push(coreSwitch)

  // 2. 生成汇聚层交换机（switchCount的1/3，至少1个）
  const distributionCount = Math.max(1, Math.floor(switchCount / 3))
  const distributionSpacing = 600 / (distributionCount + 1)

  for (let i = 0; i < distributionCount; i++) {
    const x = (i + 1) * distributionSpacing + 100
    const distributionSwitch = {
      id: generateId(),
      type: 'switch',
      x,
      y: layers.distribution.y,
      properties: {
        width: 60,
        height: 60,
        status: getRandomStatus(),
        data: {
          id: generateId(),
          name: `汇聚交换机${i + 1}`,
          ip: `10.0.1.${i + 1}`
        }
      },
      text: {
        x,
        y: layers.distribution.y,
        value: `汇聚交换机${i + 1}`
      }
    }
    nodes.push(distributionSwitch)
    layers.distribution.switches.push(distributionSwitch)

    // 连接到核心交换机
    edges.push({
      id: generateId(),
      type: 'line',
      sourceNodeId: coreSwitch.id,
      targetNodeId: distributionSwitch.id,
      properties: {}
    })
  }

  // 3. 生成接入层交换机（剩余的交换机）
  const accessCount = switchCount - distributionCount - 1 // 减去核心层的1个
  const accessSpacing = 800 / (accessCount + 1)

  for (let i = 0; i < accessCount; i++) {
    const x = (i + 1) * accessSpacing + 50
    const accessSwitch = {
      id: generateId(),
      type: 'switch',
      x,
      y: layers.access.y,
      properties: {
        width: 60,
        height: 60,
        status: getRandomStatus(),
        data: {
          id: generateId(),
          name: `接入交换机${i + 1}`,
          ip: `10.0.2.${i + 1}`
        }
      },
      text: {
        x,
        y: layers.access.y,
        value: `接入交换机${i + 1}`
      }
    }
    nodes.push(accessSwitch)
    layers.access.switches.push(accessSwitch)

    // 连接到汇聚层交换机（轮流连接）
    const distributionSwitch = layers.distribution.switches[i % distributionCount]
    edges.push({
      id: generateId(),
      type: 'line',
      sourceNodeId: distributionSwitch.id,
      targetNodeId: accessSwitch.id,
      properties: {}
    })
  }

  // 4. 生成终端设备并连接到接入层交换机
  const devicesPerSwitch = Math.ceil(deviceCount / accessCount)
  let deviceIndex = 0

  for (let switchIdx = 0; switchIdx < accessCount; switchIdx++) {
    const accessSwitch = layers.access.switches[switchIdx]
    const devicesForThisSwitch = Math.min(
      devicesPerSwitch,
      deviceCount - deviceIndex
    )

    const deviceSpacing = 120
    const totalWidth = devicesForThisSwitch * deviceSpacing
    const startX = accessSwitch.x - totalWidth / 2 + deviceSpacing / 2

    for (let i = 0; i < devicesForThisSwitch; i++) {
      const deviceType = getRandomDeviceType()
      const x = startX + i * deviceSpacing
      const y = 700 + Math.random() * 100 // 随机y坐标，增加自然感

      const device = {
        id: generateId(),
        type: deviceType,
        x,
        y,
        properties: {
          width: 60,
          height: 60,
          status: getRandomStatus(),
          data: {
            id: generateId(),
            name: `${deviceType}-${deviceIndex + 1}`,
            ip: generateRandomIP()
          }
        },
        text: {
          x,
          y,
          value: `${deviceType}-${deviceIndex + 1}`
        }
      }
      nodes.push(device)

      // 连接到接入层交换机
      edges.push({
        id: generateId(),
        type: 'line',
        sourceNodeId: accessSwitch.id,
        targetNodeId: device.id,
        properties: {}
      })

      deviceIndex++
      if (deviceIndex >= deviceCount) break
    }

    if (deviceIndex >= deviceCount) break
  }

  return { nodes, edges }
}

/**
 * 生成预定义规模的拓扑数据
 * @param {string} scale - 规模类型: 'micro' | 'standard' | 'large' | 'huge'
 * @returns {Object} 拓扑图数据
 */
export const generateTopologyByScale = (scale) => {
  const scaleConfig = {
    micro: { devices: 20, switches: 2 },
    standard: { devices: 100, switches: 5 },
    large: { devices: 500, switches: 10 },
    huge: { devices: 1000, switches: 50 }
  }

  const config = scaleConfig[scale] || scaleConfig.micro
  return generateThreeLayerTopology(config.devices, config.switches)
}

/**
 * 生成拓扑数据的统计信息
 * @param {Object} topology - 拓扑图数据
 * @returns {Object} 统计信息
 */
export const getTopologyStats = (topology) => {
  const stats = {
    totalNodes: topology.nodes?.length || 0,
    totalEdges: topology.edges?.length || 0,
    switches: 0,
    devices: 0,
    online: 0,
    offline: 0,
    deviceTypes: {}
  }

  if (topology.nodes) {
    topology.nodes.forEach((node) => {
      if (node.type === 'switch') {
        stats.switches++
      } else {
        stats.devices++
        stats.deviceTypes[node.type] = (stats.deviceTypes[node.type] || 0) + 1
      }

      if (node.properties?.status === 'online') {
        stats.online++
      } else if (node.properties?.status === 'offline') {
        stats.offline++
      }
    })
  }

  return stats
}
