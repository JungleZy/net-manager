<template>
  <div class="p-[12px] size-full topology-area">
    <div class="size-full bg-white rounded-lg shadow p-[6px] relative">
      <div class="w-full h-full project-grid" ref="container"></div>

      <!-- 左侧菜单空状态提示 -->
      <div v-if="leftMenus.length === 0" class="left-menu-empty layout-center">
        <div class="empty-content">
          <div class="empty-icon">📦</div>
          <div class="empty-text">暂无数据</div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="absolute bottom-[24px] right-[24px]">
        <a-button type="primary" @click="handleAddNode" :loading="isSaving">
          {{ isSaving ? '保存中...' : '保存' }}
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  onMounted,
  onUnmounted,
  nextTick,
  ref,
  useTemplateRef,
  shallowRef
} from 'vue'
import { LogicFlow } from '@logicflow/core'
import dagre from 'dagre'
import {
  Control,
  DndPanel,
  SelectionSelect,
  MiniMap,
  Highlight
} from '@logicflow/extension'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'
import CustomHtml from '@/common/node/HtmlNode'
import { default as customNodes } from '@/common/node/index'
import DeviceApi from '@/common/api/device'
import SwitchApi from '@/common/api/switch'
import TopologyApi from '@/common/api/topology'
import { message } from 'ant-design-vue'
import Firewall from '@/assets/firewall.png'
import Laptop from '@/assets/laptop.png'
import Pc from '@/assets/pc.png'
import Router from '@/assets/router.png'
import Server from '@/assets/server.png'
import Switches from '@/assets/switches.png'
import { deriveDeviceName } from '@/common/utils/Utils.js'

const containerRef = useTemplateRef('container')
// 使用 shallowRef 避免深度响应式带来的性能开销
let lf = null
const devices = shallowRef([])
const switches = shallowRef([])
const currentTopologyId = ref(null)
const isSaving = ref(false)
const leftMenus = shallowRef([])
const isComponentMounted = ref(false)

// 设备类型映射 - 移到外部作为常量,避免重复创建
const DEVICE_TYPE_MAP = Object.freeze({
  台式机: { icon: Pc, type: 'pc' },
  笔记本: { icon: Laptop, type: 'laptop' },
  服务器: { icon: Server, type: 'server' },
  路由器: { icon: Router, type: 'router' },
  交换机: { icon: Switches, type: 'switch' },
  防火墙: { icon: Firewall, type: 'firewall' }
})

// 锚点索引常量
const ANCHOR = Object.freeze({
  TOP: 0,
  RIGHT: 1,
  BOTTOM: 2,
  LEFT: 3
})

// 使用 shallowRef 减少响应式开销,拓扑数据不需要深度响应
const data = shallowRef({
  // nodes: [
  //   {
  //     id: '3',
  //     type: 'firewall',
  //     x: 200,
  //     y: 300,
  //     properties: { width: 60, height: 60, status: 'online' },
  //     text: { x: 200, y: 300, value: '防火墙防火墙防火墙' }
  //   },
  //   {
  //     id: '31',
  //     type: 'firewall',
  //     x: 652,
  //     y: 658,
  //     properties: { width: 60, height: 60, status: 'offline' },
  //     text: { x: 652, y: 658, value: '防火墙防火墙防火墙' }
  //   },
  //   {
  //     id: '4',
  //     type: 'laptop',
  //     x: 350,
  //     y: 300,
  //     properties: { width: 60, height: 60, status: 'offline' },
  //     text: { x: 350, y: 300, value: '笔记本防火墙台式机路由器' }
  //   },
  //   {
  //     id: '41',
  //     type: 'laptop',
  //     x: 451,
  //     y: 173,
  //     properties: { width: 60, height: 60, status: 'online' },
  //     text: { x: 451, y: 173, value: '笔记本防火墙台式机路由器' }
  //   },
  //   {
  //     id: '5',
  //     type: 'pc',
  //     x: 500,
  //     y: 300,
  //     properties: { width: 60, height: 60, status: 'offline' },
  //     text: { x: 500, y: 300, value: '台式机' }
  //   },
  //   {
  //     id: '51',
  //     type: 'pc',
  //     x: 767,
  //     y: 201,
  //     properties: { width: 60, height: 60, status: 'online' },
  //     text: { x: 767, y: 201, value: '台式机' }
  //   },
  //   {
  //     id: '6',
  //     type: 'router',
  //     x: 656,
  //     y: 536,
  //     properties: { width: 60, height: 60, status: 'offline' },
  //     text: { x: 656, y: 536, value: '路由器' }
  //   },
  //   {
  //     id: '61',
  //     type: 'router',
  //     x: 282,
  //     y: 604,
  //     properties: { width: 60, height: 60, status: 'online' },
  //     text: { x: 282, y: 604, value: '路由器' }
  //   },
  //   {
  //     id: '7',
  //     type: 'server',
  //     x: 654,
  //     y: 824,
  //     properties: { width: 60, height: 60, status: 'offline' },
  //     text: { x: 654, y: 824, value: '服务器' }
  //   },
  //   {
  //     id: '71',
  //     type: 'server',
  //     x: 432,
  //     y: 643,
  //     properties: { width: 60, height: 60, status: 'online' },
  //     text: { x: 432, y: 643, value: '服务器' }
  //   },
  //   {
  //     id: '8',
  //     type: 'switch',
  //     x: 673,
  //     y: 380,
  //     properties: { width: 60, height: 60, status: 'offline' },
  //     text: { x: 673, y: 380, value: '交换机' }
  //   },
  //   {
  //     id: '81',
  //     type: 'switch',
  //     x: 473,
  //     y: 417,
  //     properties: { width: 60, height: 60, status: 'online' },
  //     text: { x: 473, y: 417, value: '交换机' }
  //   }
  // ],
  // edges: [
  //   {
  //     id: '5a93be03-4a83-4e0d-9f51-66dc35b91c69',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '41',
  //     targetNodeId: '8',
  //     sourceAnchorId: '41_1',
  //     targetAnchorId: '8_0',
  //     startPoint: { x: 481, y: 173 },
  //     endPoint: { x: 673, y: 350 },
  //     pointsList: [
  //       { x: 481, y: 173 },
  //       { x: 673, y: 173 },
  //       { x: 673, y: 350 }
  //     ]
  //   },
  //   {
  //     id: '3927ff57-8721-4b14-93dc-614dc359f864',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '51',
  //     targetNodeId: '8',
  //     sourceAnchorId: '51_2',
  //     targetAnchorId: '8_0',
  //     startPoint: { x: 767, y: 231 },
  //     endPoint: { x: 673, y: 350 },
  //     pointsList: [
  //       { x: 767, y: 231 },
  //       { x: 767, y: 320 },
  //       { x: 673, y: 320 },
  //       { x: 673, y: 350 }
  //     ]
  //   },
  //   {
  //     id: '214ca0b3-1a1f-43f7-a00b-f1e01183b82a',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '5',
  //     targetNodeId: '8',
  //     sourceAnchorId: '5_1',
  //     targetAnchorId: '8_0',
  //     startPoint: { x: 530, y: 300 },
  //     endPoint: { x: 673, y: 350 },
  //     pointsList: [
  //       { x: 530, y: 300 },
  //       { x: 673, y: 300 },
  //       { x: 673, y: 350 }
  //     ]
  //   },
  //   {
  //     id: '007d8b7b-f77b-4891-8e55-f2515bdb133a',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '4',
  //     targetNodeId: '81',
  //     sourceAnchorId: '4_2',
  //     targetAnchorId: '81_0',
  //     startPoint: { x: 350, y: 330 },
  //     endPoint: { x: 473, y: 387 },
  //     pointsList: [
  //       { x: 350, y: 330 },
  //       { x: 350, y: 357 },
  //       { x: 473, y: 357 },
  //       { x: 473, y: 387 }
  //     ]
  //   },
  //   {
  //     id: 'e440b0ea-f69a-4c3a-bdbf-778049faf7bc',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '81',
  //     targetNodeId: '6',
  //     sourceAnchorId: '81_2',
  //     targetAnchorId: '6_0',
  //     startPoint: { x: 473, y: 447 },
  //     endPoint: { x: 656, y: 506 },
  //     pointsList: [
  //       { x: 473, y: 447 },
  //       { x: 473, y: 476 },
  //       { x: 656, y: 476 },
  //       { x: 656, y: 506 }
  //     ]
  //   },
  //   {
  //     id: '7cfd444b-04ba-4383-b282-7da9726800cf',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '8',
  //     targetNodeId: '6',
  //     sourceAnchorId: '8_2',
  //     targetAnchorId: '6_0',
  //     startPoint: { x: 673, y: 410 },
  //     endPoint: { x: 656, y: 506 },
  //     pointsList: [
  //       { x: 673, y: 410 },
  //       { x: 673, y: 458 },
  //       { x: 656, y: 458 },
  //       { x: 656, y: 506 }
  //     ]
  //   },
  //   {
  //     id: '3d5c2846-9e14-4110-9952-d623541cc55f',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '6',
  //     targetNodeId: '31',
  //     sourceAnchorId: '6_2',
  //     targetAnchorId: '31_0',
  //     startPoint: { x: 656, y: 566 },
  //     endPoint: { x: 652, y: 628 },
  //     pointsList: [
  //       { x: 656, y: 566 },
  //       { x: 656, y: 597 },
  //       { x: 652, y: 597 },
  //       { x: 652, y: 628 }
  //     ]
  //   },
  //   {
  //     id: '15c820d6-2265-47ec-85e8-69ffd631f068',
  //     type: 'polyline',
  //     properties: {},
  //     sourceNodeId: '31',
  //     targetNodeId: '7',
  //     sourceAnchorId: '31_2',
  //     targetAnchorId: '7_0',
  //     startPoint: { x: 652, y: 688 },
  //     endPoint: { x: 654, y: 794 },
  //     pointsList: [
  //       { x: 652, y: 688 },
  //       { x: 652, y: 741 },
  //       { x: 654, y: 741 },
  //       { x: 654, y: 794 }
  //     ]
  //   }
  // ]
})

onMounted(() => {
  nextTick(() => {
    isComponentMounted.value = true
    initTopology()
  })
})

onUnmounted(() => {
  // 组件销毁时清理资源
  cleanup()
})

// 资源清理函数
const cleanup = () => {
  document.removeEventListener('keydown', handleKeyDown)
  isComponentMounted.value = false

  // 销毁 LogicFlow 实例,释放内存
  if (lf) {
    try {
      lf.destroy()
    } catch (error) {
      console.warn('LogicFlow 实例销毁失败:', error)
    }
    lf = null
  }
}

// 插件配置移到外部常量,避免重复创建对象
const PLUGINS_OPTIONS = Object.freeze({
  miniMap: {
    width: 137,
    height: 121,
    rightPosition: 8,
    bottomPosition: 8
  },
  label: {
    isMultiple: true,
    textOverflowMode: 'ellipsis'
  }
})

const initTopology = () => {
  // 清理旧实例
  if (lf) {
    try {
      lf.destroy()
    } catch (error) {
      console.warn('清理旧 LogicFlow 实例失败:', error)
    }
    lf = null
  }

  // 确保container已正确挂载并获取其尺寸
  const container = containerRef.value
  if (!container) {
    console.error('容器元素未找到')
    return
  }

  const width = container.offsetWidth || 800
  const height = container.offsetHeight || 600

  try {
    lf = new LogicFlow({
      grid: true,
      container: container,
      width: width,
      height: height,
      keyboard: {
        enabled: true
      },
      // 边的默认样式配置
      edgeType: 'polyline',
      style: {
        edge: {
          stroke: '#afafaf',
          strokeWidth: 2
        },
        arrow: {
          offset: 0,
          verticalLength: 0
        }
      },
      plugins: [Control, DndPanel, SelectionSelect, MiniMap, Highlight],
      pluginsOptions: PLUGINS_OPTIONS,
      adjustEdgeStartAndEnd: true,
      // 性能优化配置
      stopScrollGraph: true,
      stopZoomGraph: false,
      partial: true // 启用局部渲染
    })

    lf.register(CustomHtml)
    // 注册所有自定义节点
    customNodes.forEach((node) => {
      lf.register(node)
    })
  } catch (error) {
    console.error('LogicFlow 初始化失败:', error)
    message.error('拓扑图初始化失败')
    return
  }

  lf.extension.dndPanel.setPatternItems([])

  // 添加一键美化按钮
  lf.extension.control.addItem({
    key: 'beautify',
    iconClass: 'lf-control-beautify',
    title: '一键美化',
    text: '美化',
    onClick: (lf) => {
      handleBeautifyAction(lf)
    }
  })

  // 添加居中按钮
  lf.extension.control.addItem({
    key: 'center',
    iconClass: 'lf-control-center',
    title: '居中显示',
    text: '居中',
    onClick: (lf) => {
      handleCenterView(lf)
    }
  })

  lf.render(data.value)

  // 添加键盘Delete键监听
  document.addEventListener('keydown', handleKeyDown)

  // 监听节点拖拽添加事件，添加后从leftMenus中移除
  lf.on('node:dnd-add', (nodeData) => {
    try {
      const dataId = nodeData?.data?.properties?.data?.id
      if (!dataId) return

      // 查找匹配的菜单项并移除
      const index = leftMenus.value.findIndex(
        (item) => item?.properties?.data?.id === dataId
      )

      if (index !== -1) {
        // 创建新数组，移除匹配项
        const newMenus = [...leftMenus.value]
        newMenus.splice(index, 1)
        leftMenus.value = newMenus

        // 更新拖拽面板项
        if (lf?.extension?.dndPanel) {
          lf.extension.dndPanel.setPatternItems(leftMenus.value)
        }
      }
    } catch (error) {
      console.warn('处理节点添加事件失败:', error)
    }
  })

  // 监听节点删除事件，删除后重新添加到左侧菜单
  lf.on('node:delete', ({ data }) => {
    try {
      // 延迟更新菜单，确保节点已完全删除
      nextTick(() => {
        updateLeftMenus()
        // 更新拖拽面板项
        if (lf?.extension?.dndPanel) {
          lf.extension.dndPanel.setPatternItems(leftMenus.value)
        }
      })
    } catch (error) {
      console.warn('处理节点删除事件失败:', error)
    }
  })

  // 获取设备和交换机数据并设置拖拽面板项
  Promise.all([loadLatestTopology()])
    .then(() => {
      fetchDevices()
      fetchSwitches()
    })
    .catch((error) => {
      console.error('初始化数据加载失败:', error)
    })
}

// 加载最新的拓扑图
const loadLatestTopology = async () => {
  if (!lf) {
    console.warn('LogicFlow 实例未初始化')
    return
  }

  try {
    const response = await TopologyApi.getLatestTopology()
    if (response?.data?.content) {
      const topologyData = response.data.content
      currentTopologyId.value = response.data.id
      data.value = topologyData
      lf.render(data.value)
    } else {
      // 没有保存的拓扑图,使用默认数据
      lf.render(data.value)
    }
    handleCenterView(lf)
  } catch (error) {
    // 如果是404错误(没有拓扑图),使用默认数据
    if (error?.response?.status === 404) {
      lf.render(data.value)
    } else {
      console.error('加载拓扑图失败:', error)
      message.error('加载拓扑图失败')
      lf.render(data.value)
    }
  }
}

const handleAddNode = async () => {
  if (isSaving.value) {
    return
  }

  if (!lf) {
    message.error('拓扑图未初始化')
    return
  }

  try {
    isSaving.value = true

    // 获取当前拓扑图数据
    let graphData = lf.getGraphData()

    if (!graphData) {
      throw new Error('无法获取拓扑图数据')
    }

    // 格式化坐标,保留2位小数
    graphData = formatGraphData(graphData)

    // 如果当前已有拓扑图ID,则更新;否则创建新的
    const response = await TopologyApi.createTopology(graphData)
    if (response?.data?.id) {
      currentTopologyId.value = response.data.id
    }
    message.success('拓扑图保存成功')
  } catch (error) {
    console.error('保存拓扑图失败:', error)
    message.error(error?.response?.data?.message || '保存拓扑图失败')
  } finally {
    isSaving.value = false
  }
}

// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await DeviceApi.getDevicesList()
    devices.value = response?.data || []
    updateLeftMenus()
  } catch (error) {
    console.error('获取设备列表失败:', error)
    message.error('获取设备列表失败')
  }
}

// 获取交换机列表
const fetchSwitches = async () => {
  try {
    const response = await SwitchApi.getSwitchesList()
    switches.value = response?.data || []
    updateLeftMenus()
  } catch (error) {
    console.error('获取交换机列表失败:', error)
    message.error('获取交换机列表失败')
  }
}

/**
 * 格式化图数据，将所有坐标保留2位小数
 * 优化: 添加空值检查,减少不必要的计算
 */
const formatGraphData = (graphData) => {
  if (!graphData) return graphData

  // 格式化节点坐标 - 使用for-of循环提升可读性
  if (graphData.nodes?.length > 0) {
    for (const node of graphData.nodes) {
      if (typeof node.x === 'number') {
        node.x = Number(node.x.toFixed(2))
      }
      if (typeof node.y === 'number') {
        node.y = Number(node.y.toFixed(2))
      }
      // 格式化文本坐标
      if (node.text && typeof node.text === 'object') {
        if (typeof node.text.x === 'number') {
          node.text.x = Number(node.text.x.toFixed(2))
        }
        if (typeof node.text.y === 'number') {
          node.text.y = Number(node.text.y.toFixed(2))
        }
      }
    }
  }

  // 格式化边的坐标点 - 使用for-of循环提升可读性
  if (graphData.edges?.length > 0) {
    for (const edge of graphData.edges) {
      // 格式化起点
      if (edge.startPoint) {
        if (typeof edge.startPoint.x === 'number') {
          edge.startPoint.x = Number(edge.startPoint.x.toFixed(2))
        }
        if (typeof edge.startPoint.y === 'number') {
          edge.startPoint.y = Number(edge.startPoint.y.toFixed(2))
        }
      }
      // 格式化终点
      if (edge.endPoint) {
        if (typeof edge.endPoint.x === 'number') {
          edge.endPoint.x = Number(edge.endPoint.x.toFixed(2))
        }
        if (typeof edge.endPoint.y === 'number') {
          edge.endPoint.y = Number(edge.endPoint.y.toFixed(2))
        }
      }
      // 格式化路径点列表
      if (edge.pointsList?.length > 0) {
        for (const point of edge.pointsList) {
          if (typeof point.x === 'number') {
            point.x = Number(point.x.toFixed(2))
          }
          if (typeof point.y === 'number') {
            point.y = Number(point.y.toFixed(2))
          }
        }
      }
    }
  }

  return graphData
}

/**
 * 创建并配置dagre图布局
 */
const createDagreGraph = () => {
  const g = new dagre.graphlib.Graph()
  g.setGraph({
    rankdir: 'TB', // 从上到下布局
    nodesep: 100, // 节点间距
    ranksep: 100, // 层级间距
    marginx: 50,
    marginy: 50
  })
  g.setDefaultEdgeLabel(() => ({}))
  return g
}

/**
 * 将节点和边添加到dagre图中
 */
const populateDagreGraph = (g, graphData) => {
  // 添加节点
  for (const node of graphData.nodes) {
    g.setNode(node.id, {
      width: node.properties?.width || 60,
      height: node.properties?.height || 60
    })
  }

  // 添加边
  if (graphData.edges?.length > 0) {
    for (const edge of graphData.edges) {
      g.setEdge(edge.sourceNodeId, edge.targetNodeId)
    }
  }
}

/**
 * 根据dagre布局结果更新节点位置
 */
const updateNodePositions = (graphData, g) => {
  for (const node of graphData.nodes) {
    const dagreNode = g.node(node.id)
    if (!dagreNode) continue

    // 保留2位小数
    node.x = Number(dagreNode.x.toFixed(2))
    node.y = Number(dagreNode.y.toFixed(2))

    // 更新文本位置
    if (node.text && typeof node.text === 'object') {
      node.text.x = Number(dagreNode.x.toFixed(2))
      node.text.y = Number(dagreNode.y.toFixed(2))
    }
  }
}

/**
 * 优化边的锚点连接
 */
const optimizeEdgeAnchors = (graphData) => {
  if (!graphData.edges?.length) return

  for (const edge of graphData.edges) {
    const sourceNode = graphData.nodes.find((n) => n.id === edge.sourceNodeId)
    const targetNode = graphData.nodes.find((n) => n.id === edge.targetNodeId)

    if (sourceNode && targetNode) {
      const bestAnchors = calculateBestAnchors(sourceNode, targetNode)
      edge.sourceAnchorId = bestAnchors.sourceAnchor
      edge.targetAnchorId = bestAnchors.targetAnchor
    }

    // 删除旧的路径点信息，让LogicFlow重新计算
    delete edge.pointsList
    delete edge.startPoint
    delete edge.endPoint
  }
}

/**
 * 触发画布适应视图
 */
const triggerFitView = (lfInstance) => {
  const control = lfInstance.extension?.control
  if (!control) {
    lfInstance.fitView(20)
    return
  }

  const controlItems = control.controlItems
  if (!controlItems) {
    lfInstance.fitView(20)
    return
  }

  // 查找适应画布按钮
  const fitItem = controlItems.find(
    (item) =>
      item.key === 'reset' ||
      item.key === 'fit' ||
      item.key === 'lf-control-fit'
  )

  const hasFitFunction = fitItem?.onClick
  if (hasFitFunction) {
    fitItem.onClick(lfInstance)
  } else {
    lfInstance.fitView(20)
  }
}

// 一键美化功能（供 Control 插件调用）
const handleBeautifyAction = (lfInstance) => {
  if (!lfInstance) {
    console.warn('美化操作: LogicFlow 实例不存在')
    return
  }

  try {
    const graphData = lfInstance.getGraphData()

    if (!graphData?.nodes?.length) {
      message.warning('画布中没有节点')
      return
    }

    // 创建dagre图并执行布局
    const g = createDagreGraph()
    populateDagreGraph(g, graphData)
    dagre.layout(g)

    // 更新节点位置和边的锚点
    updateNodePositions(graphData, g)
    optimizeEdgeAnchors(graphData)

    // 重新渲染图
    lfInstance.render(graphData)

    // 适应视图并居中
    nextTick(() => {
      triggerFitView(lfInstance)
      handleCenterView(lf)
    })

    message.success('布局美化完成')
  } catch (error) {
    console.error('美化失败:', error)
    message.error('美化失败，请确保已安装dagre库')
  }
}

// 居中显示功能（供 Control 插件调用）
const handleCenterView = (lfInstance) => {
  if (!lfInstance) {
    console.warn('居中操作: LogicFlow 实例不存在')
    return
  }

  try {
    const graphData = lfInstance.getGraphData()

    if (!graphData?.nodes?.length) {
      message.warning('画布中没有节点')
      return
    }

    // 计算所有节点的边界框
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity

    for (const node of graphData.nodes) {
      const nodeWidth = node.properties?.width || 60
      const nodeHeight = node.properties?.height || 60

      minX = Math.min(minX, node.x - nodeWidth / 2)
      minY = Math.min(minY, node.y - nodeHeight / 2)
      maxX = Math.max(maxX, node.x + nodeWidth / 2)
      maxY = Math.max(maxY, node.y + nodeHeight / 2)
    }

    // 计算内容中心点
    const contentCenterX = (minX + maxX) / 2
    const contentCenterY = (minY + maxY) / 2

    // 获取画布尺寸和变换
    const transform = lfInstance.getTransform()
    const canvasWidth = lfInstance.graphModel.width
    const canvasHeight = lfInstance.graphModel.height

    // 计算画布中心点（在逻辑坐标系中，考虑当前缩放和平移）
    const canvasCenterX =
      (canvasWidth / 2 - transform.TRANSLATE_X) / transform.SCALE_X
    const canvasCenterY =
      (canvasHeight / 2 - transform.TRANSLATE_Y) / transform.SCALE_Y

    // 计算需要移动的距离
    const offsetX = canvasCenterX - contentCenterX
    const offsetY = canvasCenterY - contentCenterY

    // 移动所有节点 - 使用for-of循环提升可读性
    for (const node of graphData.nodes) {
      node.x = Number((node.x + offsetX).toFixed(2))
      node.y = Number((node.y + offsetY).toFixed(2))
      // 更新文本位置
      if (node.text && typeof node.text === 'object') {
        node.text.x = Number((node.text.x + offsetX).toFixed(2))
        node.text.y = Number((node.text.y + offsetY).toFixed(2))
      }
    }

    // 清空边的路径点，让LogicFlow自动重新计算
    if (graphData.edges?.length > 0) {
      for (const edge of graphData.edges) {
        delete edge.pointsList
        delete edge.startPoint
        delete edge.endPoint
      }
    }

    // 重新渲染图
    lfInstance.render(graphData)
  } catch (error) {
    console.error('居中失败:', error)
    message.error('居中失败')
  }
}

/**
 * 根据角度确定锚点方向
 * @param {number} angle - 角度值（度数）
 * @returns {Array} [源锚点索引, 目标锚点索引]
 */
const getAnchorsByAngle = (angle) => {
  // 角度区间到锚点的映射表
  const angleRanges = [
    { min: -22.5, max: 22.5, anchors: [ANCHOR.RIGHT, ANCHOR.LEFT] }, // 正右
    { min: 22.5, max: 157.5, anchors: [ANCHOR.BOTTOM, ANCHOR.TOP] }, // 下半圆
    { min: 157.5, max: 180, anchors: [ANCHOR.LEFT, ANCHOR.RIGHT] }, // 正左（正值）
    { min: -180, max: -157.5, anchors: [ANCHOR.LEFT, ANCHOR.RIGHT] }, // 正左（负值）
    { min: -157.5, max: -22.5, anchors: [ANCHOR.TOP, ANCHOR.BOTTOM] } // 上半圆
  ]

  for (const range of angleRanges) {
    if (angle >= range.min && angle < range.max) {
      return range.anchors
    }
  }

  // 默认返回右侧连接
  return [ANCHOR.RIGHT, ANCHOR.LEFT]
}

/**
 * 根据距离差值确定主方向的锚点
 * @param {number} dx - x轴差值
 * @param {number} dy - y轴差值
 * @param {number} absDx - x轴距离绝对值
 * @param {number} absDy - y轴距离绝对值
 * @returns {Array|null} [源锚点索引, 目标锚点索引] 或 null（表示需要用角度计算）
 */
const getAnchorsByDistance = (dx, dy, absDx, absDy) => {
  const horizontalDominant = absDx > absDy * 1.5
  const verticalDominant = absDy > absDx * 1.5

  if (horizontalDominant) {
    return dx > 0 ? [ANCHOR.RIGHT, ANCHOR.LEFT] : [ANCHOR.LEFT, ANCHOR.RIGHT]
  }

  if (verticalDominant) {
    return dy > 0 ? [ANCHOR.BOTTOM, ANCHOR.TOP] : [ANCHOR.TOP, ANCHOR.BOTTOM]
  }

  return null
}

/**
 * 格式化锚点ID
 * @param {string} nodeId - 节点ID
 * @param {number} anchorIndex - 锚点索引
 * @returns {string} 格式化的锚点ID
 */
const formatAnchorId = (nodeId, anchorIndex) => `${nodeId}_${anchorIndex}`

/**
 * 计算两个节点之间的最佳锚点连接
 * 锚点索引: 0-上, 1-右, 2-下, 3-左
 * 原则：目标在源的某个方向，源节点就用该方向的锚点，目标节点用相反方向的锚点
 */
const calculateBestAnchors = (sourceNode, targetNode) => {
  if (!sourceNode || !targetNode) {
    console.warn('计算锚点: 节点不存在')
    return {
      sourceAnchor: `${sourceNode?.id}_0`,
      targetAnchor: `${targetNode?.id}_0`
    }
  }

  // 计算节点中心点之间的差值
  const dx = targetNode.x - sourceNode.x
  const dy = targetNode.y - sourceNode.y
  const absDx = Math.abs(dx)
  const absDy = Math.abs(dy)

  // 优先根据距离判断主方向
  let anchors = getAnchorsByDistance(dx, dy, absDx, absDy)

  // 如果距离无法确定主方向，则根据角度判断
  if (!anchors) {
    const angle = Math.atan2(dy, dx) * (180 / Math.PI)
    anchors = getAnchorsByAngle(angle)
  }

  const [sourceAnchorIndex, targetAnchorIndex] = anchors

  return {
    sourceAnchor: formatAnchorId(sourceNode.id, sourceAnchorIndex),
    targetAnchor: formatAnchorId(targetNode.id, targetAnchorIndex)
  }
}

// 更新左侧菜单项 - 优化性能
const updateLeftMenus = () => {
  // 获取当前拓扑图中已存在的节点ID集合
  const existingNodeIds = new Set()
  if (lf) {
    try {
      const graphData = lf.getGraphData()
      if (graphData?.nodes?.length > 0) {
        // 使用for-of循环提升可读性
        for (const node of graphData.nodes) {
          const dataId = node?.properties?.data?.id
          if (dataId) {
            existingNodeIds.add(dataId)
          }
        }
      }
    } catch (error) {
      console.warn('获取拓扑图节点失败:', error)
    }
  }

  // 构建新的菜单项列表
  const newMenus = []

  // 添加设备项（过滤已在拓扑图中的设备） - 使用for-of循环
  const devicesArray = devices.value
  for (const device of devicesArray) {
    // 检查设备是否已在拓扑图中
    if (existingNodeIds.has(device.client_id)) {
      continue // 跳过已存在的设备
    }

    const deviceType = device.type || '未知设备'
    const typeConfig = DEVICE_TYPE_MAP[deviceType] || { icon: Pc, type: 'pc' }

    newMenus.push({
      type: typeConfig.type,
      label: device.hostname || device.ip_address || '未知设备',
      text: device.hostname || device.ip_address || '未知设备',
      properties: {
        width: 60,
        height: 60,
        data: {
          id: device.client_id
        }
      },
      icon: typeConfig.icon
    })
  }

  // 添加交换机项（过滤已在拓扑图中的交换机） - 使用for-of循环
  const switchesArray = switches.value
  for (const switchItem of switchesArray) {
    // 检查交换机是否已在拓扑图中
    if (existingNodeIds.has(switchItem.id)) {
      continue // 跳过已存在的交换机
    }

    // 使用 deriveDeviceName 函数从描述推导设备名称
    const deviceName =
      switchItem.device_name ||
      deriveDeviceName(switchItem.description) ||
      '未知交换机'

    newMenus.push({
      type: 'switch',
      label: deviceName,
      text: deviceName,
      properties: {
        width: 60,
        height: 60,
        data: {
          id: switchItem.id
        }
      },
      icon: Switches
    })
  }

  // 更新 leftMenus
  leftMenus.value = newMenus
  if (lf?.extension?.dndPanel) {
    lf.extension.dndPanel.setPatternItems(leftMenus.value)
  }
}

/**
 * 检查事件目标是否为可编辑元素
 * @param {EventTarget} target - 事件目标
 * @returns {boolean} 是否为可编辑元素
 */
const isEditableElement = (target) => {
  return (
    target?.tagName === 'INPUT' ||
    target?.tagName === 'TEXTAREA' ||
    target?.isContentEditable
  )
}

/**
 * 删除选中的节点和边
 * @param {Object} selectElements - 选中的元素
 * @returns {boolean} 是否成功删除
 */
const deleteSelectedElements = (selectElements) => {
  const nodesCount = selectElements.nodes?.length || 0
  const edgesCount = selectElements.edges?.length || 0

  if (nodesCount === 0 && edgesCount === 0) {
    return false
  }

  // 删除选中的节点
  if (nodesCount > 0) {
    for (const node of selectElements.nodes) {
      lf.deleteNode(node.id)
    }
    message.success(`已删除 ${nodesCount} 个节点`)
  }

  // 删除选中的边
  if (edgesCount > 0) {
    for (const edge of selectElements.edges) {
      lf.deleteEdge(edge.id)
    }
    message.success(`已删除 ${edgesCount} 条边`)
  }

  return true
}

// 处理键盘Delete键删除功能 - 优化健壮性
const handleKeyDown = (event) => {
  // 检查组件是否已挂载和LogicFlow实例是否存在
  if (!isComponentMounted.value || !lf) {
    return false
  }

  // 检查是否按下Delete或Backspace键
  const isDeleteKey = event.key === 'Delete' || event.key === 'Backspace'
  if (!isDeleteKey) {
    return false
  }

  // 防止在输入框等元素中触发删除操作
  if (isEditableElement(event.target)) {
    return false
  }

  // 阻止默认行为（如浏览器后退）
  event.preventDefault()

  try {
    // 获取选中的元素
    const selectElements = lf.getSelectElements(true)

    if (!selectElements) {
      return false
    }

    // 删除选中的元素
    const deleted = deleteSelectedElements(selectElements)
    return deleted
  } catch (error) {
    console.error('删除元素失败:', error)
    message.error('删除失败')
    return false
  }
}
</script>

<style lang="less">
.topology-area {
  // 左侧菜单空状态样式
  .left-menu-empty {
    background: hsla(0, 0%, 100%, 0.8);
    border-radius: 5px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
    margin: 5px;
    padding: 15px 5px;
    position: absolute;
    z-index: 999;
    top: 6px;
    bottom: 6px;
    width: 120px;
    overflow: auto;

    .empty-content {
      text-align: center;
      padding: 20px;

      .empty-icon {
        font-size: 38px;
        margin-bottom: 8px;
      }

      .empty-text {
        font-size: 12px;
        color: #999;
      }
    }
  }

  .lf-dndpanel {
    top: 0;
    bottom: 0;
    width: 120px;
    overflow: auto;

    .lf-dnd-text {
      font-size: 12px;
    }
  }

  // Control插件样式自定义
  .lf-control {
    top: 12px;
    right: 2px;
    padding: 0 12px;
    margin: 0;
    // 一键美化按钮样式
    .lf-control-item {
      .lf-control-text {
        font-size: 12px;
      }
      i {
        width: 16px;
        height: 16px;
      }
      &[data-key='beautify'],
      &[data-key='center'] {
        width: 32px;
        height: 32px;
        background-color: #fff;
        border: 1px solid #e8e8e8;
        border-radius: 4px;
        cursor: pointer;
        display: flex !important;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
        transition: all 0.3s;
        position: relative;

        &:hover {
          background-color: #f5f5f5;
          border-color: #1890ff;
        }

        // 隐藏可能的文本
        .lf-control-text {
          display: none;
        }
      }
    }

    // 美化按钮图标
    .lf-control-beautify {
      &::before {
        content: '✨';
        font-size: 16px;
        line-height: 1;
        display: block;
      }
    }

    // 居中按钮图标
    .lf-control-center {
      &::before {
        content: '◉';
        font-size: 16px;
        line-height: 1;
        display: block;
      }
    }
  }

  // 取消边的箭头
  :deep(.lf-edge) {
    .lf-arrow {
      display: none !important;
    }
  }

  // 确保所有类型的边都没有箭头
  :deep(.lf-edge-polyline),
  :deep(.lf-edge-line),
  :deep(.lf-edge-bezier) {
    marker-end: none !important;
    marker-start: none !important;
  }
}
</style>
