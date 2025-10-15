/**
 * 拓扑图测试数据生成器
 * 生成三层网络架构：核心层、汇聚层、接入层
 */

/**
 * 生成三层网络拓扑测试数据
 * @param {Object} config - 配置选项
 * @param {Number} config.switchCount - 交换机总数（默认20）
 * @param {Number} config.deviceCount - 设备总数（默认500）
 * @returns {Object} { nodes: [], links: [] }
 */
export function generateThreeTierTopology(config = {}) {
  const {
    switchCount = 20,
    deviceCount = 500
  } = config

  // 三层架构配置
  const coreCount = 2 // 核心层交换机数量
  const distributionCount = 6 // 汇聚层交换机数量
  const accessCount = switchCount - coreCount - distributionCount // 接入层交换机数量

  if (accessCount < 0) {
    throw new Error('交换机总数太少，无法构建三层架构')
  }

  const nodes = []
  const links = []
  let nodeIdCounter = 1

  // 画布配置
  const canvasWidth = 2000
  const canvasHeight = 1500
  const layerHeight = canvasHeight / 4

  // =============== 1. 创建核心层交换机 ===============
  const coreNodes = []
  const coreY = layerHeight
  const coreSpacing = canvasWidth / (coreCount + 1)

  for (let i = 0; i < coreCount; i++) {
    const node = {
      id: `core-switch-${i + 1}`,
      type: 'switch',
      label: `核心交换机-${i + 1}`,
      x: coreSpacing * (i + 1),
      y: coreY,
      status: 'online',
      properties: {
        layer: 'core',
        deviceType: 'core-switch',
        bandwidth: '100Gbps',
        model: 'Cisco Nexus 9000'
      }
    }
    nodes.push(node)
    coreNodes.push(node)
  }

  // =============== 2. 创建汇聚层交换机 ===============
  const distributionNodes = []
  const distributionY = layerHeight * 2
  const distributionSpacing = canvasWidth / (distributionCount + 1)

  for (let i = 0; i < distributionCount; i++) {
    const node = {
      id: `distribution-switch-${i + 1}`,
      type: 'switch',
      label: `汇聚交换机-${i + 1}`,
      x: distributionSpacing * (i + 1),
      y: distributionY,
      status: 'online',
      properties: {
        layer: 'distribution',
        deviceType: 'distribution-switch',
        bandwidth: '40Gbps',
        model: 'Cisco Catalyst 4500'
      }
    }
    nodes.push(node)
    distributionNodes.push(node)
  }

  // 核心层与汇聚层连接（全网状连接）
  coreNodes.forEach(coreNode => {
    distributionNodes.forEach(distNode => {
      links.push({
        id: `link-${coreNode.id}-${distNode.id}`,
        source: coreNode.id,
        target: distNode.id,
        properties: {
          bandwidth: '40Gbps',
          protocol: 'LACP'
        }
      })
    })
  })

  // =============== 3. 创建接入层交换机 ===============
  const accessNodes = []
  const accessY = layerHeight * 3
  const accessSpacing = canvasWidth / (accessCount + 1)

  for (let i = 0; i < accessCount; i++) {
    const node = {
      id: `access-switch-${i + 1}`,
      type: 'switch',
      label: `接入交换机-${i + 1}`,
      x: accessSpacing * (i + 1),
      y: accessY,
      status: 'online',
      properties: {
        layer: 'access',
        deviceType: 'access-switch',
        bandwidth: '10Gbps',
        model: 'Cisco Catalyst 2960'
      }
    }
    nodes.push(node)
    accessNodes.push(node)
  }

  // 汇聚层与接入层连接（每个接入层交换机连接到两个汇聚层交换机实现冗余）
  accessNodes.forEach((accessNode, index) => {
    // 连接到主汇聚交换机
    const primaryDist = distributionNodes[index % distributionCount]
    links.push({
      id: `link-${accessNode.id}-${primaryDist.id}`,
      source: accessNode.id,
      target: primaryDist.id,
      properties: {
        bandwidth: '10Gbps',
        type: 'primary'
      }
    })

    // 连接到备份汇聚交换机（实现冗余）
    const backupDist = distributionNodes[(index + 1) % distributionCount]
    links.push({
      id: `link-${accessNode.id}-${backupDist.id}`,
      source: accessNode.id,
      target: backupDist.id,
      properties: {
        bandwidth: '10Gbps',
        type: 'backup'
      }
    })
  })

  // =============== 4. 创建终端设备 ===============
  const devicesPerSwitch = Math.floor(deviceCount / accessCount)
  const remainingDevices = deviceCount % accessCount

  // 设备类型分布
  const deviceTypes = [
    { type: 'pc', label: 'PC', weight: 50, icon: '🖥️' },
    { type: 'laptop', label: '笔记本', weight: 30, icon: '💻' },
    { type: 'server', label: '服务器', weight: 10, icon: '🖧' },
    { type: 'printer', label: '打印机', weight: 5, icon: '🖨️' },
    { type: 'router', label: '路由器', weight: 3, icon: '📡' },
    { type: 'firewall', label: '防火墙', weight: 2, icon: '🛡️' }
  ]

  let deviceCounter = 1

  accessNodes.forEach((accessSwitch, switchIndex) => {
    // 计算当前交换机应该连接的设备数量
    let devicesForThisSwitch = devicesPerSwitch
    if (switchIndex < remainingDevices) {
      devicesForThisSwitch += 1
    }

    // 为每个接入交换机创建设备
    for (let i = 0; i < devicesForThisSwitch; i++) {
      // 根据权重随机选择设备类型
      const deviceType = weightedRandomChoice(deviceTypes)

      // 设备位置（在接入交换机周围随机分布）
      const angle = (Math.PI / 2) + (Math.random() * Math.PI) // 下半圆
      const radius = 80 + Math.random() * 100
      const deviceX = accessSwitch.x + Math.cos(angle) * radius
      const deviceY = accessSwitch.y + Math.sin(angle) * radius

      const device = {
        id: `device-${deviceCounter}`,
        type: deviceType.type,
        label: `${deviceType.label}-${deviceCounter}`,
        x: deviceX,
        y: deviceY,
        status: Math.random() > 0.95 ? 'offline' : 'online', // 5% 概率离线
        properties: {
          layer: 'access',
          deviceType: deviceType.type,
          ip: generateRandomIP(),
          mac: generateRandomMAC(),
          hostname: `${deviceType.type}-${deviceCounter}`
        }
      }

      nodes.push(device)

      // 连接到接入层交换机
      links.push({
        id: `link-${device.id}-${accessSwitch.id}`,
        source: device.id,
        target: accessSwitch.id,
        properties: {
          bandwidth: '1Gbps',
          type: 'access'
        }
      })

      deviceCounter++
    }
  })

  console.log(`
  ===== 拓扑图生成完成 =====
  核心层交换机: ${coreCount}
  汇聚层交换机: ${distributionCount}
  接入层交换机: ${accessCount}
  总交换机数: ${coreCount + distributionCount + accessCount}
  终端设备数: ${deviceCounter - 1}
  总节点数: ${nodes.length}
  总连线数: ${links.length}
  ==========================
  `)

  return {
    nodes,
    links,
    metadata: {
      architecture: 'three-tier',
      coreCount,
      distributionCount,
      accessCount,
      deviceCount: deviceCounter - 1,
      totalNodes: nodes.length,
      totalLinks: links.length,
      generatedAt: new Date().toISOString()
    }
  }
}

/**
 * 根据权重随机选择设备类型
 * @param {Array} choices - 选择数组
 * @returns {Object} 选中的设备类型
 */
function weightedRandomChoice(choices) {
  const totalWeight = choices.reduce((sum, choice) => sum + choice.weight, 0)
  let random = Math.random() * totalWeight

  for (const choice of choices) {
    random -= choice.weight
    if (random <= 0) {
      return choice
    }
  }

  return choices[0] // 默认返回第一个
}

/**
 * 生成随机IP地址
 * @returns {String} IP地址
 */
function generateRandomIP() {
  const subnet = '192.168'
  const thirdOctet = Math.floor(Math.random() * 255)
  const fourthOctet = Math.floor(Math.random() * 254) + 1
  return `${subnet}.${thirdOctet}.${fourthOctet}`
}

/**
 * 生成随机MAC地址
 * @returns {String} MAC地址
 */
function generateRandomMAC() {
  const hexDigits = '0123456789ABCDEF'
  let mac = ''
  for (let i = 0; i < 6; i++) {
    if (i > 0) mac += ':'
    mac += hexDigits[Math.floor(Math.random() * 16)]
    mac += hexDigits[Math.floor(Math.random() * 16)]
  }
  return mac
}

/**
 * 导出为JSON文件
 * @param {Object} data - 拓扑数据
 * @param {String} filename - 文件名
 */
export function exportToJSON(data, filename = 'topology-test-data.json') {
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()

  URL.revokeObjectURL(url)
}

/**
 * 生成简化版测试数据（用于快速测试）
 * @returns {Object} { nodes: [], links: [] }
 */
export function generateSimpleTestData() {
  return generateThreeTierTopology({
    switchCount: 8,
    deviceCount: 50
  })
}

/**
 * 生成大规模测试数据
 * @returns {Object} { nodes: [], links: [] }
 */
export function generateLargeScaleTestData() {
  return generateThreeTierTopology({
    switchCount: 30,
    deviceCount: 1000
  })
}
