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
import { onMounted, onUnmounted, nextTick, ref, useTemplateRef } from 'vue'
import { LogicFlow } from '@logicflow/core'
import dagre from 'dagre'
import {
  Control,
  DndPanel,
  SelectionSelect,
  Menu,
  MiniMap,
  Highlight,
  CurvedEdge,
  CurvedEdgeModel,
  Label
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
let lf = null
const devices = ref([])
const switches = ref([])
const currentTopologyId = ref(null) // 当前拓扑图ID
const isSaving = ref(false) // 保存状态
const leftMenus = ref([])

const data = ref({
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
const isComponentMounted = ref(false)

onMounted(() => {
  nextTick(() => {
    isComponentMounted.value = true
    initTopology()
  })
})

onUnmounted(() => {
  // 组件销毁时移除键盘事件监听
  document.removeEventListener('keydown', handleKeyDown)
  isComponentMounted.value = false
})

const pluginsOptions = () => {
  return {
    miniMap: {
      width: 137,
      height: 121,
      rightPosition: 8,
      bottomPosition: 8
    },
    lable: {
      isMultiple: true,
      textOverflowMode: 'ellipsis'
    }
  }
}

const initTopology = () => {
  // 确保container已正确挂载并获取其尺寸
  const container = containerRef.value
  const width = container.offsetWidth || 800
  const height = container.offsetHeight || 600

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
      // 取消边的箭头
      edge: {
        stroke: '#afafaf',
        strokeWidth: 2
      },
      // 取消箭头
      arrow: {
        offset: 0,
        verticalLength: 0
      }
    },
    plugins: [Control, DndPanel, SelectionSelect, MiniMap, Highlight],
    pluginsOptions: pluginsOptions(),
    adjustEdgeStartAndEnd: true
  })
  lf.register(CustomHtml)
  // 注册所有自定义节点
  customNodes.forEach((node) => {
    lf.register(node)
  })

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
    // 查找匹配的菜单项并移除
    const index = leftMenus.value.findIndex(
      (item) => item.properties.data.id === nodeData.data.properties.data.id
    )

    if (index !== -1) {
      // 创建新数组，移除匹配项
      const newMenus = [...leftMenus.value]
      newMenus.splice(index, 1)
      leftMenus.value = newMenus

      // 更新拖拽面板项
      lf.extension.dndPanel.setPatternItems(leftMenus.value)
    }
  })

  // 监听节点删除事件，删除后重新添加到左侧菜单
  lf.on('node:delete', ({ data }) => {
    // 延迟更新菜单，确保节点已完全删除
    nextTick(() => {
      updateLeftMenus()
      // 更新拖拽面板项
      if (lf && lf.extension && lf.extension.dndPanel) {
        lf.extension.dndPanel.setPatternItems(leftMenus.value)
      }
    })
  })

  // 获取设备和交换机数据并设置拖拽面板项
  Promise.all([loadLatestTopology()]).then(() => {
    fetchDevices()
    fetchSwitches()
  })
}

// 加载最新的拓扑图
const loadLatestTopology = async () => {
  try {
    const response = await TopologyApi.getLatestTopology()
    if (response.data && response.data.content) {
      const topologyData = response.data.content
      currentTopologyId.value = response.data.id
      data.value = topologyData
      lf.render(data.value)
    } else {
      // 没有保存的拓扑图，使用默认数据
      lf.render(data.value)
    }
    handleCenterView(lf)
  } catch (error) {
    // 如果是404错误（没有拓扑图），使用默认数据
    if (error.response?.status === 404) {
      lf.render(data.value)
    } else {
      console.error('加载拓扑图失败:', error)
      lf.render(data.value)
    }
  }
}

const handleAddNode = async () => {
  if (isSaving.value) {
    return
  }

  try {
    isSaving.value = true

    // 获取当前拓扑图数据
    let graphData = lf.getGraphData()

    // 格式化坐标，保留2位小数
    graphData = formatGraphData(graphData)

    // 如果当前已有拓扑图ID，则更新；否则创建新的
    const response = await TopologyApi.createTopology(graphData)
    if (response.data && response.data.id) {
      currentTopologyId.value = response.data.id
    }
    message.success('拓扑图保存成功')
  } catch (error) {
    console.error('保存拓扑图失败:', error)
    message.error(error.response?.data?.message || '保存拓扑图失败')
  } finally {
    isSaving.value = false
  }
}

// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await DeviceApi.getDevicesList()
    devices.value = response.data || []
    updateLeftMenus()
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

// 获取交换机列表
const fetchSwitches = async () => {
  try {
    const response = await SwitchApi.getSwitchesList()
    switches.value = response.data || []
    updateLeftMenus()
  } catch (error) {
    console.error('获取交换机列表失败:', error)
  }
}

/**
 * 格式化图数据，将所有坐标保留2位小数
 */
const formatGraphData = (graphData) => {
  if (!graphData) return graphData

  // 格式化节点坐标
  if (graphData.nodes) {
    graphData.nodes.forEach((node) => {
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
    })
  }

  // 格式化边的坐标点
  if (graphData.edges) {
    graphData.edges.forEach((edge) => {
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
      if (edge.pointsList && Array.isArray(edge.pointsList)) {
        edge.pointsList = edge.pointsList.map((point) => ({
          x: typeof point.x === 'number' ? Number(point.x.toFixed(2)) : point.x,
          y: typeof point.y === 'number' ? Number(point.y.toFixed(2)) : point.y
        }))
      }
    })
  }

  return graphData
}

// 一键美化功能（供 Control 插件调用）
const handleBeautifyAction = (lfInstance) => {
  if (!lfInstance) return
  try {
    const graphData = lfInstance.getGraphData()

    if (!graphData.nodes || graphData.nodes.length === 0) {
      message.warning('画布中没有节点')
      return
    }

    // 创建dagre图
    const g = new dagre.graphlib.Graph()
    g.setGraph({
      rankdir: 'TB', // 从上到下布局
      nodesep: 100, // 节点间距
      ranksep: 100, // 层级间距
      marginx: 50,
      marginy: 50
    })
    g.setDefaultEdgeLabel(() => ({}))

    // 添加节点到dagre图
    graphData.nodes.forEach((node) => {
      g.setNode(node.id, {
        width: node.properties?.width || 60,
        height: node.properties?.height || 60
      })
    })

    // 添加边到dagre图
    if (graphData.edges) {
      graphData.edges.forEach((edge) => {
        g.setEdge(edge.sourceNodeId, edge.targetNodeId)
      })
    }

    // 执行布局计算
    dagre.layout(g)

    // 更新节点位置 - 直接修改graphData并重新渲染
    graphData.nodes.forEach((node) => {
      const dagreNode = g.node(node.id)
      if (dagreNode) {
        // 保留2位小数
        node.x = Number(dagreNode.x.toFixed(2))
        node.y = Number(dagreNode.y.toFixed(2))
        // 更新文本位置
        if (node.text && typeof node.text === 'object') {
          node.text.x = Number(dagreNode.x.toFixed(2))
          node.text.y = Number(dagreNode.y.toFixed(2))
        }
      }
    })

    // 优化边的锚点连接 - 遵循就近原则
    if (graphData.edges) {
      graphData.edges.forEach((edge) => {
        const sourceNode = graphData.nodes.find(
          (n) => n.id === edge.sourceNodeId
        )
        const targetNode = graphData.nodes.find(
          (n) => n.id === edge.targetNodeId
        )

        if (sourceNode && targetNode) {
          // 计算最佳锚点
          const bestAnchors = calculateBestAnchors(sourceNode, targetNode)

          // 更新锚点ID
          edge.sourceAnchorId = bestAnchors.sourceAnchor
          edge.targetAnchorId = bestAnchors.targetAnchor
        }

        // 删除旧的路径点信息，让LogicFlow重新计算
        delete edge.pointsList
        delete edge.startPoint
        delete edge.endPoint
      })
    }

    // 重新渲染图，这会根据新的节点位置自动计算连线
    lfInstance.render(graphData)

    // 使用Control插件的适应画布功能
    nextTick(() => {
      if (lfInstance.extension && lfInstance.extension.control) {
        // 查找并触发Control插件的适应按钮
        const controlItems = lfInstance.extension.control.controlItems
        if (controlItems) {
          // 查找适应画布按钮（通常key为'reset'或'fit'）
          const fitItem = controlItems.find(
            (item) =>
              item.key === 'reset' ||
              item.key === 'fit' ||
              item.key === 'lf-control-fit'
          )
          if (fitItem && fitItem.onClick) {
            // 调用Control插件的适应功能
            fitItem.onClick(lfInstance)
          } else {
            // 如果找不到，降级使用原生API
            lfInstance.fitView(20)
          }
        } else {
          // 如果Control插件未正确初始化，使用原生API
          lfInstance.fitView(20)
        }
      } else {
        // 如果Control插件不存在，使用原生API
        lfInstance.fitView(20)
      }
    })
    handleCenterView(lf)
    message.success('布局美化完成')
  } catch (error) {
    console.error('美化失败:', error)
    message.error('美化失败，请确保已安装dagre库')
  }
}

// 居中显示功能（供 Control 插件调用）
const handleCenterView = (lfInstance) => {
  if (!lfInstance) return
  try {
    const graphData = lfInstance.getGraphData()

    if (!graphData.nodes || graphData.nodes.length === 0) {
      message.warning('画布中没有节点')
      return
    }

    // 计算所有节点的边界框
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity

    graphData.nodes.forEach((node) => {
      const nodeWidth = node.properties?.width || 60
      const nodeHeight = node.properties?.height || 60

      minX = Math.min(minX, node.x - nodeWidth / 2)
      minY = Math.min(minY, node.y - nodeHeight / 2)
      maxX = Math.max(maxX, node.x + nodeWidth / 2)
      maxY = Math.max(maxY, node.y + nodeHeight / 2)
    })

    // 计算内容中心点
    const contentCenterX = (minX + maxX) / 2
    const contentCenterY = (minY + maxY) / 2

    // 获取画布尺寸和变换
    const transform = lfInstance.getTransform()
    const canvasWidth = lfInstance.graphModel.width
    const canvasHeight = lfInstance.graphModel.height

    // 计算画布中心点（在逻辑坐标系中，考虑当前缩放和平移）
    // 公式: 逻辑坐标 = (屏幕坐标 - 平移) / 缩放
    const canvasCenterX =
      (canvasWidth / 2 - transform.TRANSLATE_X) / transform.SCALE_X
    const canvasCenterY =
      (canvasHeight / 2 - transform.TRANSLATE_Y) / transform.SCALE_Y

    // 计算需要移动的距离
    const offsetX = canvasCenterX - contentCenterX
    const offsetY = canvasCenterY - contentCenterY

    // 移动所有节点
    graphData.nodes.forEach((node) => {
      // 保留2位小数
      node.x = Number((node.x + offsetX).toFixed(2))
      node.y = Number((node.y + offsetY).toFixed(2))
      // 更新文本位置
      if (node.text && typeof node.text === 'object') {
        node.text.x = Number((node.text.x + offsetX).toFixed(2))
        node.text.y = Number((node.text.y + offsetY).toFixed(2))
      }
    })

    // 清空边的路径点，让LogicFlow自动重新计算
    if (graphData.edges) {
      graphData.edges.forEach((edge) => {
        delete edge.pointsList
        delete edge.startPoint
        delete edge.endPoint
      })
    }

    // 重新渲染图
    lfInstance.render(graphData)
  } catch (error) {
    console.error('居中失败:', error)
    message.error('居中失败')
  }
}

/**
 * 计算两个节点之间的最佳锚点连接
 * 锚点索引: 0-上, 1-右, 2-下, 3-左
 * 原则：目标在源的某个方向，源节点就用该方向的锚点，目标节点用相反方向的锚点
 */
const calculateBestAnchors = (sourceNode, targetNode) => {
  const sx = sourceNode.x
  const sy = sourceNode.y
  const tx = targetNode.x
  const ty = targetNode.y

  // 计算节点中心点之间的差值和角度
  const dx = tx - sx
  const dy = ty - sy
  const angle = Math.atan2(dy, dx) * (180 / Math.PI)

  // 计算水平和垂直距离的绝对值，用于判断主要方向
  const absDx = Math.abs(dx)
  const absDy = Math.abs(dy)

  // 锚点索引映射：0-上, 1-右, 2-下, 3-左
  const ANCHOR = { TOP: 0, RIGHT: 1, BOTTOM: 2, LEFT: 3 }
  let sourceAnchor
  let targetAnchor

  // 优化策略：比较水平和垂直距离，选择更大的主方向
  if (absDx > absDy * 1.5) {
    // 水平距离明显大于垂直距离，优先水平连接
    const [source, target] =
      dx > 0
        ? [ANCHOR.RIGHT, ANCHOR.LEFT] // 目标在右侧 →
        : [ANCHOR.LEFT, ANCHOR.RIGHT] // 目标在左侧 ←
    sourceAnchor = `${sourceNode.id}_${source}`
    targetAnchor = `${targetNode.id}_${target}`
  } else if (absDy > absDx * 1.5) {
    // 垂直距离明显大于水平距离，优先垂直连接
    const [source, target] =
      dy > 0
        ? [ANCHOR.BOTTOM, ANCHOR.TOP] // 目标在下方 ↓
        : [ANCHOR.TOP, ANCHOR.BOTTOM] // 目标在上方 ↑
    sourceAnchor = `${sourceNode.id}_${source}`
    targetAnchor = `${targetNode.id}_${target}`
  } else {
    // 对角方向：水平和垂直距离相近，根据角度区间选择
    let source, target

    if (angle >= -22.5 && angle < 22.5) {
      // 正右 → (0°)
      ;[source, target] = [ANCHOR.RIGHT, ANCHOR.LEFT]
    } else if (angle >= 22.5 && angle < 157.5) {
      // 下半圆 ↓ (22.5° ~ 157.5°) 包含：右下、正下、左下
      ;[source, target] = [ANCHOR.BOTTOM, ANCHOR.TOP]
    } else if (angle >= 157.5 || angle < -157.5) {
      // 正左 ← (180°)
      ;[source, target] = [ANCHOR.LEFT, ANCHOR.RIGHT]
    } else {
      // 上半圆 ↑ (-157.5° ~ -22.5°) 包含：左上、正上、右上
      ;[source, target] = [ANCHOR.TOP, ANCHOR.BOTTOM]
    }

    sourceAnchor = `${sourceNode.id}_${source}`
    targetAnchor = `${targetNode.id}_${target}`
  }

  return {
    sourceAnchor,
    targetAnchor
  }
}

// 更新左侧菜单项
const updateLeftMenus = () => {
  // 获取当前拓扑图中已存在的节点ID集合
  const existingNodeIds = new Set()
  if (lf) {
    try {
      const graphData = lf.getGraphData()
      if (graphData && graphData.nodes) {
        graphData.nodes.forEach((node) => {
          // 提取节点的 data.id
          if (
            node.properties &&
            node.properties.data &&
            node.properties.data.id
          ) {
            existingNodeIds.add(node.properties.data.id)
          }
        })
      }
    } catch (error) {
      console.warn('获取拓扑图节点失败:', error)
    }
  }

  // 设备类型映射
  const deviceTypeMap = {
    台式机: { icon: Pc, type: 'pc' },
    笔记本: { icon: Laptop, type: 'laptop' },
    服务器: { icon: Server, type: 'server' },
    路由器: { icon: Router, type: 'router' },
    交换机: { icon: Switches, type: 'switch' },
    防火墙: { icon: Firewall, type: 'firewall' }
  }

  // 构建新的菜单项列表
  const newMenus = []

  // 添加设备项（过滤已在拓扑图中的设备）
  devices.value.forEach((device) => {
    // 检查设备是否已在拓扑图中

    if (existingNodeIds.has(device.client_id)) {
      return // 跳过已存在的设备
    }

    const deviceType = device.type || '未知设备'
    const typeConfig = deviceTypeMap[deviceType] || { icon: Pc, type: 'pc' }

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
  })

  // 添加交换机项（过滤已在拓扑图中的交换机）
  switches.value.forEach((switchItem) => {
    // 检查交换机是否已在拓扑图中
    if (existingNodeIds.has(switchItem.id)) {
      return // 跳过已存在的交换机
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
  })
  // 更新 leftMenus
  leftMenus.value = newMenus
  lf.extension.dndPanel.setPatternItems(leftMenus.value)
}

// 处理键盘Delete键删除功能
const handleKeyDown = (event) => {
  // 检查组件是否已挂载和LogicFlow实例是否存在
  if (!isComponentMounted.value || !lf) {
    return
  }

  // 检查是否按下Delete或Backspace键
  if (event.key === 'Delete' || event.key === 'Backspace') {
    // 防止在输入框等元素中触发删除操作
    const target = event.target
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.isContentEditable
    ) {
      return
    }

    // 阻止默认行为（如浏览器后退）
    event.preventDefault()

    try {
      // 获取选中的元素
      const selectElements = lf.getSelectElements(true)

      if (
        !selectElements ||
        (selectElements.nodes.length === 0 && selectElements.edges.length === 0)
      ) {
        return
      }

      // 删除选中的节点
      if (selectElements.nodes && selectElements.nodes.length > 0) {
        selectElements.nodes.forEach((node) => {
          lf.deleteNode(node.id)
        })
        message.success(`已删除 ${selectElements.nodes.length} 个节点`)
      }

      // 删除选中的边
      if (selectElements.edges && selectElements.edges.length > 0) {
        selectElements.edges.forEach((edge) => {
          lf.deleteEdge(edge.id)
        })
        message.success(`已删除 ${selectElements.edges.length} 条边`)
      }
    } catch (error) {
      console.error('删除元素失败:', error)
      message.error('删除失败')
    }
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
