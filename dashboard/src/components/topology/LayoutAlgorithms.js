/**
 * 高级布局算法
 * 实现层次布局和优化的力导向布局
 */
import * as d3 from 'd3'

export class LayoutAlgorithms {
  /**
   * 检测网络层级结构
   * @param {Array} nodes - 节点数组
   * @param {Array} links - 连线数组
   * @returns {Object} { nodeHierarchy, maxLevel }
   */
  static detectHierarchy(nodes, links) {
    const nodeMap = new Map()
    const visited = new Set()

    // 初始化节点信息
    nodes.forEach((node) => {
      nodeMap.set(node.id, {
        level: -1,
        inDegree: 0,
        outDegree: 0,
        children: [],
        parents: []
      })
    })

    // 构建连接关系
    links.forEach((link) => {
      const sourceId = link.source.id || link.source
      const targetId = link.target.id || link.target
      const sourceInfo = nodeMap.get(sourceId)
      const targetInfo = nodeMap.get(targetId)

      if (sourceInfo && targetInfo) {
        sourceInfo.children.push(targetId)
        sourceInfo.outDegree++
        targetInfo.parents.push(sourceId)
        targetInfo.inDegree++
      }
    })

    // 找出根节点（入度为0）
    const rootNodes = []
    nodeMap.forEach((info, nodeId) => {
      if (info.inDegree === 0) {
        rootNodes.push(nodeId)
      }
    })

    // 如果没有根节点（存在环），选择出度最大的节点作为根
    if (rootNodes.length === 0) {
      let maxOutDegree = -1
      nodeMap.forEach((info, nodeId) => {
        if (info.outDegree > maxOutDegree) {
          maxOutDegree = info.outDegree
          rootNodes.length = 0
          rootNodes.push(nodeId)
        } else if (info.outDegree === maxOutDegree) {
          rootNodes.push(nodeId)
        }
      })
    }

    // BFS 分配层级
    const queue = rootNodes.map((id) => ({ id, level: 0 }))

    while (queue.length > 0) {
      const { id, level } = queue.shift()

      if (visited.has(id)) continue
      visited.add(id)

      const nodeInfo = nodeMap.get(id)
      nodeInfo.level = level

      // 将子节点加入队列
      nodeInfo.children.forEach((childId) => {
        if (!visited.has(childId)) {
          queue.push({ id: childId, level: level + 1 })
        }
      })
    }

    // 处理未访问的节点（孤立节点）
    nodeMap.forEach((info, nodeId) => {
      if (info.level === -1) {
        info.level = 0
      }
    })

    const maxLevel = Math.max(...Array.from(nodeMap.values()).map((n) => n.level))
    return { nodeHierarchy: nodeMap, maxLevel }
  }

  /**
   * 混合布局算法（层次 + 力导向）
   * 适用于大规模网络，超过100节点时使用Barnes-Hut优化
   * @param {Array} nodes - 节点数组
   * @param {Array} links - 连线数组
   * @param {Object} options - 布局选项
   */
  static hybridLayout(nodes, links, options = {}) {
    const {
      width = 800,
      height = 600,
      nodeRadius = 30,  // 节点半径
      useBarnesHut = nodes.length > 100
    } = options

    // 计算实际节点占用空间（包括文本标签）
    const nodeIconSize = nodeRadius * 2          // 节点图标大小: 60px
    const textHeight = 30                         // 文本高度(15 dy + 15 行高)
    const estimatedTextWidth = 120               // 估算文本宽度(中文约6-8个字)

    const nodeHeight = nodeIconSize + textHeight  // 90px
    const nodeWidth = Math.max(nodeIconSize, estimatedTextWidth)  // 120px

    // 根据节点大小计算间距，确保文本不重叠
    const levelHeight = Math.max(nodeHeight + 50, 150)    // 层级间隙: 至少140px
    const nodeSpacing = Math.max(nodeWidth + 60, 160)     // 水平间距: 至少180px
    const minDistance = Math.max(nodeWidth * 1.1, 130)    // 最小距离: 至少132px

    // 检测层次结构
    const { nodeHierarchy, maxLevel } = this.detectHierarchy(nodes, links)

    // 按层级分组
    const levelGroups = new Map()
    nodes.forEach((node) => {
      const info = nodeHierarchy.get(node.id)
      if (!levelGroups.has(info.level)) {
        levelGroups.set(info.level, [])
      }
      levelGroups.get(info.level).push(node)
    })

    // 初始化位置（基于层级）
    const positions = new Map()
    const velocities = new Map()

    levelGroups.forEach((levelNodes, level) => {
      levelNodes.forEach((node, index) => {
        const x = width / 2 + (index - levelNodes.length / 2) * nodeSpacing
        const y = level * levelHeight + 100
        positions.set(node.id, { x, y })
        velocities.set(node.id, { vx: 0, vy: 0 })
      })
    })

    // 力导向参数
    const iterations = useBarnesHut ? 200 : 150
    const repulsionStrength = useBarnesHut ? 6000 : 4000  // 增加排斥力，让节点分开更远
    const attractionStrength = 0.01
    const damping = 0.85
    const levelConstraintStrength = 0.15

    // 迭代计算力
    for (let iter = 0; iter < iterations; iter++) {
      const temperature = 1 - iter / iterations

      // 对每个节点计算受力
      nodes.forEach((node1) => {
        const pos1 = positions.get(node1.id)
        const info1 = nodeHierarchy.get(node1.id)
        let fx = 0,
          fy = 0

        // 排斥力（所有节点对之间）
        nodes.forEach((node2) => {
          if (node1.id === node2.id) return

          const pos2 = positions.get(node2.id)
          const dx = pos1.x - pos2.x
          const dy = pos1.y - pos2.y
          const distance = Math.max(Math.sqrt(dx * dx + dy * dy), minDistance)

          const force = repulsionStrength / (distance * distance)
          fx += (dx / distance) * force
          fy += (dy / distance) * force
        })

        // 吸引力（连接的节点之间）
        info1.children.forEach((childId) => {
          const childNode = nodes.find((n) => n.id === childId)
          if (!childNode) return

          const pos2 = positions.get(childId)
          if (!pos2) return

          const dx = pos2.x - pos1.x
          const dy = pos2.y - pos1.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          const force = distance * attractionStrength
          fx += (dx / distance) * force
          fy += (dy / distance) * force
        })

        // 层级约束力（保持y轴层次结构）
        const targetY = info1.level * levelHeight + 100
        const yDiff = targetY - pos1.y
        fy += yDiff * levelConstraintStrength

        // 更新速度和位置
        const vel = velocities.get(node1.id)
        vel.vx = (vel.vx + fx) * damping
        vel.vy = (vel.vy + fy) * damping

        pos1.x += vel.vx * temperature
        pos1.y += vel.vy * temperature
      })
    }

    // 解决节点重叠（使用实际节点大小）
    this.resolveOverlaps(nodes, positions, nodeWidth, nodeHeight)

    // 更新节点位置
    nodes.forEach((node) => {
      const pos = positions.get(node.id)
      if (pos) {
        node.x = pos.x
        node.y = pos.y
        node.fx = pos.x
        node.fy = pos.y
      }
    })

    return { positions, nodeHierarchy, maxLevel }
  }

  /**
   * 解决节点重叠（考虑节点实际大小和文本标签）
   * @param {Array} nodes - 节点数组
   * @param {Map} positions - 位置映射
   * @param {Number} nodeWidth - 节点宽度
   * @param {Number} nodeHeight - 节点高度（包括文本）
   */
  static resolveOverlaps(nodes, positions, nodeWidth, nodeHeight) {
    const maxIterations = 25  // 增加迭代次数
    // 使用更大的安全距离，确保文本不重叠
    const minHorizontalDistance = nodeWidth * 1.1   // 水平距离增加10%
    const minVerticalDistance = nodeHeight * 0.95   // 垂直距离95%

    for (let iter = 0; iter < maxIterations; iter++) {
      let hasOverlap = false

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const pos1 = positions.get(nodes[i].id)
          const pos2 = positions.get(nodes[j].id)

          if (!pos1 || !pos2) continue

          const dx = pos2.x - pos1.x
          const dy = pos2.y - pos1.y

          // 使用椭圆形碰撞检测（考虑不同的水平和垂直间距）
          const normalizedDx = dx / minHorizontalDistance
          const normalizedDy = dy / minVerticalDistance
          const normalizedDistance = Math.sqrt(normalizedDx * normalizedDx + normalizedDy * normalizedDy)

          if (normalizedDistance < 1) {
            hasOverlap = true

            // 计算推开方向和距离
            const pushDistance = (1 - normalizedDistance) / 2
            const angle = Math.atan2(dy, dx)

            // 水平和垂直方向分别计算推开，水平方向推开更多
            const pushX = Math.cos(angle) * pushDistance * minHorizontalDistance * 1.3  // 水平多推30%
            const pushY = Math.sin(angle) * pushDistance * minVerticalDistance

            pos1.x -= pushX
            pos1.y -= pushY
            pos2.x += pushX
            pos2.y += pushY
          }
        }
      }

      if (!hasOverlap) break
    }
  }

  /**
   * 圆形布局
   */
  static circularLayout(nodes, width, height) {
    const radius = Math.min(width, height) / 2 - 100
    const angleStep = (2 * Math.PI) / nodes.length

    nodes.forEach((node, index) => {
      const angle = index * angleStep
      node.x = width / 2 + radius * Math.cos(angle)
      node.y = height / 2 + radius * Math.sin(angle)
      node.fx = node.x
      node.fy = node.y
    })
  }

  /**
   * 网格布局
   */
  static gridLayout(nodes, width, height) {
    const cols = Math.ceil(Math.sqrt(nodes.length))
    const spacing = Math.min(width / cols, height / cols) * 0.8

    nodes.forEach((node, index) => {
      const col = index % cols
      const row = Math.floor(index / cols)
      node.x = (col + 1) * spacing + 50
      node.y = (row + 1) * spacing + 50
      node.fx = node.x
      node.fy = node.y
    })
  }

  /**
   * 径向布局
   */
  static radialLayout(nodes, links, width, height) {
    const { nodeHierarchy, maxLevel } = this.detectHierarchy(nodes, links)

    const centerX = width / 2
    const centerY = height / 2
    const maxRadius = Math.min(width, height) / 2 - 100

    // 按层级分组
    const levelGroups = new Map()
    nodes.forEach((node) => {
      const info = nodeHierarchy.get(node.id)
      if (!levelGroups.has(info.level)) {
        levelGroups.set(info.level, [])
      }
      levelGroups.get(info.level).push(node)
    })

    levelGroups.forEach((levelNodes, level) => {
      const radius = (level / (maxLevel + 1)) * maxRadius
      const angleStep = (2 * Math.PI) / levelNodes.length

      levelNodes.forEach((node, index) => {
        const angle = index * angleStep
        node.x = centerX + radius * Math.cos(angle)
        node.y = centerY + radius * Math.sin(angle)
        node.fx = node.x
        node.fy = node.y
      })
    })
  }
}

export default LayoutAlgorithms
