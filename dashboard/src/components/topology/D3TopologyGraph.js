/**
 * D3拓扑图核心类
 * 使用 D3.js 实现网络拓扑图的可视化、交互和布局
 * 纯手动布局模式，不使用力导向模拟
 */
import * as d3 from 'd3'
import NodeIconRenderer from './NodeIconRenderer'
import LayoutAlgorithms from './LayoutAlgorithms'

export class D3TopologyGraph {
  constructor(container, options = {}) {
    this.container = container
    this.options = {
      width: options.width || 800,
      height: options.height || 600,
      nodeRadius: options.nodeRadius || 30,
      linkDistance: options.linkDistance || 120,
      chargeStrength: options.chargeStrength || -500,
      ...options
    }

    // 数据存储
    this.nodes = []
    this.links = []
    this.nodeMap = new Map() // 用于快速查找节点

    // SVG 元素
    this.svg = null
    this.g = null
    this.linkGroup = null
    this.nodeGroup = null

    // 缩放行为
    this.zoom = null

    // 拖拽相关
    this.dragLine = null // 正在拖拽的连线
    this.selectedNode = null // 当前选中的节点
    this.sourceNode = null // 连线的源节点
    this.isDrawingLink = false // 是否正在绘制连线

    // 事件回调
    this.callbacks = {
      onNodeClick: null,
      onNodeDblClick: null,
      onLinkCreated: null,
      onNodeDeleted: null,
      onLinkDeleted: null,
      onSelectionChanged: null
    }

    this.init()
  }

  /**
   * 初始化 SVG 和基础元素
   */
  init() {
    // 清空容器
    d3.select(this.container).selectAll('*').remove()

    // 创建 SVG
    this.svg = d3
      .select(this.container)
      .append('svg')
      .attr('width', this.options.width)
      .attr('height', this.options.height)
      .style('background', 'transparent')

    // 定义箭头标记
    this.svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 8)
      .attr('markerHeight', 8)
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#afafaf')

    // 创建缩放容器
    this.g = this.svg.append('g').attr('class', 'zoom-container')

    // 连线组（在节点组下方）
    this.linkGroup = this.g.append('g').attr('class', 'links')

    // 节点组
    this.nodeGroup = this.g.append('g').attr('class', 'nodes')

    // 拖拽连线（临时线条）
    this.dragLine = this.g
      .append('line')
      .attr('class', 'drag-line')
      .attr('stroke', '#1890ff')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .style('display', 'none')

    // 设置缩放行为
    this.setupZoom()
  }

  /**
   * 设置缩放行为
   */
  setupZoom() {
    this.zoom = d3
      .zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        this.g.attr('transform', event.transform)
      })

    this.svg.call(this.zoom)

    // 点击空白处取消选中
    this.svg.on('click', () => {
      if (this.selectedNode) {
        this.nodes.forEach((n) => (n.selected = false))
        this.selectedNode = null
        this.render()
      }
    })
  }

  /**
   * 更新视图（手动布局模式）
   */
  updatePositions() {
    // 更新节点位置
    this.nodeGroup
      .selectAll('.node')
      .attr('transform', (d) => `translate(${d.x},${d.y})`)

    // 更新连线位置
    this.updateLinks()
  }

  /**
   * 加载数据
   * @param {Object} data - { nodes: [], links: [] }
   */
  loadData(data) {
    this.nodes = data.nodes || []
    this.links = data.links || []

    // 构建节点映射
    this.nodeMap.clear()
    this.nodes.forEach((node, index) => {
      this.nodeMap.set(node.id, node)
      // 确保节点有位置，如果没有则分配随机位置
      if (node.x === undefined || node.x === null) {
        // 使用圆形分布避免重叠
        const angle = (index / this.nodes.length) * 2 * Math.PI
        const radius = Math.min(this.options.width, this.options.height) / 3
        node.x = this.options.width / 2 + radius * Math.cos(angle)
      }
      if (node.y === undefined || node.y === null) {
        const angle = (index / this.nodes.length) * 2 * Math.PI
        const radius = Math.min(this.options.width, this.options.height) / 3
        node.y = this.options.height / 2 + radius * Math.sin(angle)
      }
    })

    // 处理连线的source和target
    this.processLinks()

    this.render()
  }

  /**
   * 渲染图形
   */
  render() {
    this.renderLinks()
    this.renderNodes()
    // 更新节点和连线的位置
    this.updatePositions()
  }

  /**
   * 处理连线数据，将ID转换为节点对象引用
   */
  processLinks() {
    this.links = this.links.map((link) => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source
      const targetId = typeof link.target === 'object' ? link.target.id : link.target

      return {
        source: this.nodeMap.get(sourceId),
        target: this.nodeMap.get(targetId)
      }
    }).filter(link => link.source && link.target) // 过滤掉无效连线
  }

  /**
   * 渲染连线
   */
  renderLinks() {
    const links = this.linkGroup.selectAll('.link').data(this.links, (d) => `${d.source.id}-${d.target.id}`)

    // 移除旧元素
    links.exit().remove()

    // 添加新元素
    const linkEnter = links
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('stroke', '#afafaf')
      .attr('stroke-width', 2)

    // 合并并更新位置
    const linkUpdate = linkEnter.merge(links)
    this.updateLinks(linkUpdate)
  }

  /**
   * 更新连线位置
   */
  updateLinks(selection) {
    const links = selection || this.linkGroup.selectAll('.link')
    links
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y)
  }

  /**
   * 渲染节点
   */
  renderNodes() {
    const nodes = this.nodeGroup.selectAll('.node').data(this.nodes, (d) => d.id)

    // 移除旧节点
    nodes.exit().remove()

    // 添加新节点
    const nodeEnter = nodes
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(this.createDragBehavior())

    // 添加选中边框（默认隐藏）- 正方形
    nodeEnter
      .append('rect')
      .attr('class', 'node-selection-border')
      .attr('width', (this.options.nodeRadius + 6) * 2)
      .attr('height', (this.options.nodeRadius + 6) * 2)
      .attr('x', -(this.options.nodeRadius + 6))
      .attr('y', -(this.options.nodeRadius + 6))
      .attr('rx', 4)  // 圆角
      .attr('ry', 4)
      .attr('fill', 'none')
      .attr('stroke', '#91d5ff')  // 浅蓝色
      .attr('stroke-width', 2)
      .style('display', 'none')

    // 不再添加圆形背景，直接添加图标或SVG
    nodeEnter.each((d, i, nodes) => {
      this.renderNodeIcon(d3.select(nodes[i]), d)
    })

    // 添加锚点
    this.addAnchors(nodeEnter)

    // 添加文本标签
    const textElement = nodeEnter
      .append('text')
      .attr('y', this.options.nodeRadius - 5)  // 使用y属性而不是dy，确保绝对定位
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'hanging')  // 设置为从上往下排列
      .style('font-size', '12px')
      .style('fill', '#333')
      .style('pointer-events', 'none')  // 文字不响应鼠标事件，避免遮挡锚点

    // 为每个节点添加换行文本
    textElement.each(function (d) {
      const text = d3.select(this)
      const label = d.label || d.id
      NodeIconRenderer.wrapText(text, label, 60)
    })

    // 合并更新
    const nodeUpdate = nodeEnter.merge(nodes)

    // 更新选中状态
    nodeUpdate.classed('selected', (d) => d.selected)

    // 更新文本
    nodeUpdate.select('text').each(function (d) {
      const text = d3.select(this)
      const label = d.label || d.id
      text.selectAll('*').remove()  // 清空旧的tspan
      NodeIconRenderer.wrapText(text, label, 60)
    })
    nodeUpdate.select('text').style('pointer-events', 'none')  // 确保文字不响应鼠标事件

    // 绑定事件
    nodeUpdate
      .on('click', (event, d) => {
        event.stopPropagation()
        this.handleNodeClick(d)
      })
      .on('dblclick', (event, d) => {
        event.stopPropagation()
        this.handleNodeDblClick(d)
      })
      .on('contextmenu', (event, d) => {
        event.preventDefault()
        this.handleNodeContextMenu(event, d)
      })
  }

  /**
   * 添加节点锚点（上右下左四个方向）
   */
  addAnchors(nodeGroup) {
    const anchors = [
      { id: 0, x: 0, y: -this.options.nodeRadius, label: 'top' },      // 上
      { id: 1, x: this.options.nodeRadius, y: 0, label: 'right' },    // 右
      { id: 2, x: 0, y: this.options.nodeRadius, label: 'bottom' },   // 下
      { id: 3, x: -this.options.nodeRadius, y: 0, label: 'left' }     // 左
    ]

    const anchorGroups = nodeGroup
      .selectAll('.anchor')
      .data(anchors)
      .enter()
      .append('g')
      .attr('class', 'anchor')
      .attr('transform', (d) => `translate(${d.x}, ${d.y})`)
      .style('cursor', 'crosshair')

    // 锚点圆圈
    anchorGroups
      .append('circle')
      .attr('r', 4)
      .attr('fill', '#fff')
      .attr('stroke', '#1890ff')
      .attr('stroke-width', 2)
      .style('opacity', 0)
      .attr('class', 'anchor-circle')

    // 锚点交互区域（更大的点击区域）
    anchorGroups
      .append('circle')
      .attr('r', 8)
      .attr('fill', 'transparent')
      .attr('class', 'anchor-hit-area')

    // 锚点事件 - 移除单独的hover事件，统一由节点控制
    anchorGroups
      .on('mousedown', (event, anchorData) => {
        event.stopPropagation()
        this.handleAnchorMouseDown(event, anchorData)
      })

    // 节点hover时显示所有锚点 - 使用过渡效果避免闪烁
    nodeGroup
      .on('mouseenter', function () {
        d3.select(this)
          .selectAll('.anchor-circle')
          .transition()
          .duration(150)
          .style('opacity', 1)
      })
      .on('mouseleave', function () {
        d3.select(this)
          .selectAll('.anchor-circle')
          .transition()
          .duration(150)
          .style('opacity', 0)
      })
  }

  /**
   * 锚点鼠标按下事件 - 开始绘制连线
   */
  handleAnchorMouseDown(event, anchorData) {
    // 阻止默认行为，防止文本选择
    event.preventDefault()
    event.stopPropagation()

    // 获取节点数据
    const nodeElement = event.target.closest('.node')
    const nodeData = d3.select(nodeElement).datum()

    this.sourceNode = nodeData
    this.isDrawingLink = true

    // 显示拖拽线
    const transform = d3.zoomTransform(this.svg.node())
    const [mouseX, mouseY] = d3.pointer(event, this.g.node())

    this.dragLine
      .attr('x1', nodeData.x + anchorData.x)
      .attr('y1', nodeData.y + anchorData.y)
      .attr('x2', mouseX)
      .attr('y2', mouseY)
      .style('display', 'block')

    // 添加全局鼠标移动和释放事件
    const handleMouseMove = (e) => {
      e.preventDefault() // 防止文本选择
      const [x, y] = d3.pointer(e, this.g.node())
      this.dragLine.attr('x2', x).attr('y2', y)
    }

    const handleMouseUp = (e) => {
      this.handleAnchorMouseUp(e)
      this.svg.on('mousemove.drawlink', null)
      this.svg.on('mouseup.drawlink', null)
      // 恢复文本选择
      document.body.style.userSelect = ''
    }

    // 临时禁用文本选择
    document.body.style.userSelect = 'none'

    this.svg.on('mousemove.drawlink', handleMouseMove)
    this.svg.on('mouseup.drawlink', handleMouseUp)
  }

  /**
   * 锚点鼠标释放事件 - 完成连线
   */
  handleAnchorMouseUp(event) {
    // 隐藏拖拽线
    this.dragLine.style('display', 'none')

    if (!this.isDrawingLink || !this.sourceNode) {
      this.isDrawingLink = false
      this.sourceNode = null
      return
    }

    // 检查是否在锚点上释放
    const targetAnchor = event.target.closest('.anchor')
    if (targetAnchor) {
      const targetNode = d3.select(event.target.closest('.node')).datum()

      // 不能连接到自己
      if (targetNode && targetNode.id !== this.sourceNode.id) {
        this.addLink(this.sourceNode.id, targetNode.id)
      }
    }

    this.isDrawingLink = false
    this.sourceNode = null
  }

  /**
   * 渲染节点图标
   */
  renderNodeIcon(nodeGroup, d) {
    // 使用专门的图标渲染器
    NodeIconRenderer.renderIcon(nodeGroup, d, this.options.nodeRadius * 2)
  }

  /**
   * 获取节点颜色
   */
  getNodeColor(d) {
    if (d.selected) return '#1890ff'
    if (d.status === 'offline') return '#f0f0f0'
    return '#B5D6FB'
  }

  /**
   * 创建拖拽行为
   */
  createDragBehavior() {
    return d3
      .drag()
      .on('start', (event, d) => this.dragStarted(event, d))
      .on('drag', (event, d) => this.dragged(event, d))
      .on('end', (event, d) => this.dragEnded(event, d))
  }

  dragStarted(event, d) {
    // 阻止默认行为，防止文本选择
    if (event.sourceEvent) {
      event.sourceEvent.preventDefault()
      event.sourceEvent.stopPropagation()
    }

    // 临时禁用文本选择
    document.body.style.userSelect = 'none'
  }

  dragged(event, d) {
    // 直接更新节点位置
    d.x = event.x
    d.y = event.y

    // 实时更新节点和连线位置
    this.updatePositions()
  }

  dragEnded(event, d) {
    // 恢复文本选择
    document.body.style.userSelect = ''
  }

  /**
   * 节点点击事件
   */
  handleNodeClick(d) {
    // 清除之前的选中状态
    this.nodes.forEach((n) => (n.selected = false))
    d.selected = true
    this.selectedNode = d
    this.render()

    if (this.callbacks.onNodeClick) {
      this.callbacks.onNodeClick(d)
    }
  }

  /**
   * 节点双击事件
   */
  handleNodeDblClick(d) {
    if (this.callbacks.onNodeDblClick) {
      this.callbacks.onNodeDblClick(d)
    }
  }

  /**
   * 节点右键菜单
   */
  handleNodeContextMenu(event, d) {
    // 可以在这里实现右键菜单
    console.log('Right click on node:', d)
  }

  /**
   * 添加节点
   */
  addNode(node) {
    // 设置初始位置
    if (!node.x) node.x = this.options.width / 2 + (Math.random() - 0.5) * 100
    if (!node.y) node.y = this.options.height / 2 + (Math.random() - 0.5) * 100

    this.nodes.push(node)
    this.nodeMap.set(node.id, node)

    this.render()
    this.updatePositions()
  }

  /**
   * 删除节点
   */
  deleteNode(nodeId) {
    const index = this.nodes.findIndex((n) => n.id === nodeId)
    if (index === -1) return

    this.nodes.splice(index, 1)
    this.nodeMap.delete(nodeId)

    // 删除相关的连线
    this.links = this.links.filter((l) => l.source.id !== nodeId && l.target.id !== nodeId)

    this.render()

    if (this.callbacks.onNodeDeleted) {
      this.callbacks.onNodeDeleted(nodeId)
    }
  }

  /**
   * 添加连线
   */
  addLink(sourceId, targetId) {
    // 检查连线是否已存在
    const exists = this.links.some(
      (l) => (l.source.id === sourceId && l.target.id === targetId) || (l.source.id === targetId && l.target.id === sourceId)
    )

    if (exists) return

    const sourceNode = this.nodeMap.get(sourceId)
    const targetNode = this.nodeMap.get(targetId)

    if (!sourceNode || !targetNode) return

    const link = {
      source: sourceNode,
      target: targetNode
    }

    this.links.push(link)
    this.render()

    if (this.callbacks.onLinkCreated) {
      this.callbacks.onLinkCreated(link)
    }
  }

  /**
   * 删除连线
   */
  deleteLink(sourceId, targetId) {
    const index = this.links.findIndex((l) => l.source.id === sourceId && l.target.id === targetId)

    if (index === -1) return

    this.links.splice(index, 1)
    this.render()

    if (this.callbacks.onLinkDeleted) {
      this.callbacks.onLinkDeleted({ sourceId, targetId })
    }
  }

  /**
   * 获取当前数据
   */
  getData() {
    return {
      nodes: this.nodes.map((n) => ({
        id: n.id,
        type: n.type,
        label: n.label,
        x: n.x,
        y: n.y,
        status: n.status
        // properties 已移除，不包含在保存的数据中
      })),
      links: this.links.map((l) => ({
        source: l.source.id || l.source,
        target: l.target.id || l.target
      }))
    }
  }

  /**
   * 居中显示
   */
  fitView() {
    if (this.nodes.length === 0) return

    // 计算节点边界
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity

    this.nodes.forEach((node) => {
      minX = Math.min(minX, node.x)
      minY = Math.min(minY, node.y)
      maxX = Math.max(maxX, node.x)
      maxY = Math.max(maxY, node.y)
    })

    const padding = 50
    const width = maxX - minX + padding * 2
    const height = maxY - minY + padding * 2

    const scale = Math.min(this.options.width / width, this.options.height / height, 1)

    const centerX = (minX + maxX) / 2
    const centerY = (minY + maxY) / 2

    const translateX = this.options.width / 2 - centerX * scale
    const translateY = this.options.height / 2 - centerY * scale

    this.svg
      .transition()
      .duration(750)
      .call(
        this.zoom.transform,
        d3.zoomIdentity.translate(translateX, translateY).scale(scale)
      )
  }

  /**
   * 重置缩放
   */
  resetZoom() {
    this.svg.transition().duration(750).call(this.zoom.transform, d3.zoomIdentity)
  }

  /**
   * 缩放到指定级别
   */
  zoomTo(scale) {
    this.svg.transition().duration(750).call(this.zoom.scaleTo, scale)
  }

  /**
   * 设置事件回调
   */
  on(event, callback) {
    if (this.callbacks.hasOwnProperty(`on${event.charAt(0).toUpperCase()}${event.slice(1)}`)) {
      this.callbacks[`on${event.charAt(0).toUpperCase()}${event.slice(1)}`] = callback
    }
  }

  /**
   * 执行一键美化布局
   */
  beautify() {
    if (this.nodes.length === 0) return

    const useBarnesHut = this.nodes.length > 100

    // 使用混合布局算法，传递节点半径
    const result = LayoutAlgorithms.hybridLayout(this.nodes, this.links, {
      width: this.options.width,
      height: this.options.height,
      nodeRadius: this.options.nodeRadius,  // 传递节点半径
      useBarnesHut
    })

    // 手动更新位置
    this.render()
    this.updatePositions()

    return result
  }
}

export default D3TopologyGraph

