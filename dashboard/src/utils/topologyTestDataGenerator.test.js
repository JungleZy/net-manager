/**
 * 拓扑图测试数据生成器 - 单元测试
 */

import {
  generateThreeTierTopology,
  generateSimpleTestData,
  generateLargeScaleTestData
} from '../utils/topologyTestDataGenerator.js'

console.log('🧪 开始测试拓扑图数据生成器...\n')

// 测试1: 标准测试数据
console.log('📋 测试1: 生成标准测试数据 (20交换机 + 500设备)')
try {
  const standardData = generateThreeTierTopology({
    switchCount: 20,
    deviceCount: 500
  })

  console.log('✅ 测试通过!')
  console.log(`   节点数: ${standardData.nodes.length}`)
  console.log(`   连线数: ${standardData.links.length}`)
  console.log(`   核心层: ${standardData.metadata.coreCount}`)
  console.log(`   汇聚层: ${standardData.metadata.distributionCount}`)
  console.log(`   接入层: ${standardData.metadata.accessCount}`)
  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

// 测试2: 简化版数据
console.log('📋 测试2: 生成简化版测试数据 (8交换机 + 50设备)')
try {
  const simpleData = generateSimpleTestData()

  console.log('✅ 测试通过!')
  console.log(`   节点数: ${simpleData.nodes.length}`)
  console.log(`   连线数: ${simpleData.links.length}`)
  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

// 测试3: 大规模数据
console.log('📋 测试3: 生成大规模测试数据 (30交换机 + 1000设备)')
try {
  const largeData = generateLargeScaleTestData()

  console.log('✅ 测试通过!')
  console.log(`   节点数: ${largeData.nodes.length}`)
  console.log(`   连线数: ${largeData.links.length}`)
  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

// 测试4: 数据结构验证
console.log('📋 测试4: 验证数据结构')
try {
  const testData = generateThreeTierTopology({
    switchCount: 10,
    deviceCount: 50
  })

  // 检查节点结构
  const sampleNode = testData.nodes[0]
  const requiredNodeFields = ['id', 'type', 'label', 'x', 'y', 'status', 'properties']
  const hasAllFields = requiredNodeFields.every(field => field in sampleNode)

  if (!hasAllFields) {
    throw new Error('节点缺少必需字段')
  }

  // 检查连线结构
  const sampleLink = testData.links[0]
  const requiredLinkFields = ['id', 'source', 'target']
  const hasAllLinkFields = requiredLinkFields.every(field => field in sampleLink)

  if (!hasAllLinkFields) {
    throw new Error('连线缺少必需字段')
  }

  // 检查元数据
  if (!testData.metadata || !testData.metadata.architecture) {
    throw new Error('缺少元数据')
  }

  console.log('✅ 数据结构验证通过!')
  console.log(`   节点字段: ${Object.keys(sampleNode).join(', ')}`)
  console.log(`   连线字段: ${Object.keys(sampleLink).join(', ')}`)
  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

// 测试5: 连接关系验证
console.log('📋 测试5: 验证连接关系')
try {
  const testData = generateThreeTierTopology({
    switchCount: 10,
    deviceCount: 50
  })

  const nodeIds = new Set(testData.nodes.map(n => n.id))

  // 验证所有连线的source和target都存在于节点中
  const allLinksValid = testData.links.every(link => {
    return nodeIds.has(link.source) && nodeIds.has(link.target)
  })

  if (!allLinksValid) {
    throw new Error('存在无效的连线引用')
  }

  // 统计不同层级的连接数
  const coreNodes = testData.nodes.filter(n => n.properties?.layer === 'core')
  const distNodes = testData.nodes.filter(n => n.properties?.layer === 'distribution')
  const accessSwitches = testData.nodes.filter(n => n.properties?.layer === 'access' && n.type === 'switch')

  console.log('✅ 连接关系验证通过!')
  console.log(`   核心层节点: ${coreNodes.length}`)
  console.log(`   汇聚层节点: ${distNodes.length}`)
  console.log(`   接入层交换机: ${accessSwitches.length}`)
  console.log(`   有效连线: ${testData.links.length}`)
  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

// 测试6: 设备类型分布
console.log('📋 测试6: 验证设备类型分布')
try {
  const testData = generateThreeTierTopology({
    switchCount: 10,
    deviceCount: 100
  })

  const deviceTypeCounts = {}
  testData.nodes.forEach(node => {
    if (node.properties?.layer === 'access' && node.type !== 'switch') {
      deviceTypeCounts[node.type] = (deviceTypeCounts[node.type] || 0) + 1
    }
  })

  console.log('✅ 设备类型分布:')
  Object.entries(deviceTypeCounts).forEach(([type, count]) => {
    const percentage = ((count / 100) * 100).toFixed(1)
    console.log(`   ${type}: ${count} (${percentage}%)`)
  })
  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

// 测试7: 边界条件测试
console.log('📋 测试7: 边界条件测试')
try {
  // 测试最小配置
  const minData = generateThreeTierTopology({
    switchCount: 8,
    deviceCount: 10
  })
  console.log('✅ 最小配置测试通过')
  console.log(`   节点数: ${minData.nodes.length}`)

  // 测试异常情况：交换机数量太少
  try {
    generateThreeTierTopology({
      switchCount: 5,
      deviceCount: 10
    })
    console.log('❌ 应该抛出错误但没有')
  } catch (error) {
    console.log('✅ 正确处理异常情况:', error.message)
  }

  console.log('')
} catch (error) {
  console.error('❌ 测试失败:', error.message)
}

console.log('🎉 所有测试完成!\n')
