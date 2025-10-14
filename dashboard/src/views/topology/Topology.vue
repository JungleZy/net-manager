<template>
  <div class="p-[12px] size-full topology-area">
    <div class="size-full bg-white rounded-lg shadow p-[6px] relative">
      <div class="w-full h-full project-grid" ref="container"></div>

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
  nodes: [
    {
      id: '3',
      type: 'firewall',
      x: 200,
      y: 300,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 200, y: 300, value: '防火墙防火墙防火墙' }
    },
    {
      id: '31',
      type: 'firewall',
      x: 652,
      y: 658,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 652, y: 658, value: '防火墙防火墙防火墙' }
    },
    {
      id: '4',
      type: 'laptop',
      x: 350,
      y: 300,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 350, y: 300, value: '笔记本防火墙台式机路由器' }
    },
    {
      id: '41',
      type: 'laptop',
      x: 451,
      y: 173,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 451, y: 173, value: '笔记本防火墙台式机路由器' }
    },
    {
      id: '5',
      type: 'pc',
      x: 500,
      y: 300,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 500, y: 300, value: '台式机' }
    },
    {
      id: '51',
      type: 'pc',
      x: 767,
      y: 201,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 767, y: 201, value: '台式机' }
    },
    {
      id: '6',
      type: 'router',
      x: 656,
      y: 536,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 656, y: 536, value: '路由器' }
    },
    {
      id: '61',
      type: 'router',
      x: 282,
      y: 604,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 282, y: 604, value: '路由器' }
    },
    {
      id: '7',
      type: 'server',
      x: 654,
      y: 824,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 654, y: 824, value: '服务器' }
    },
    {
      id: '71',
      type: 'server',
      x: 432,
      y: 643,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 432, y: 643, value: '服务器' }
    },
    {
      id: '8',
      type: 'switch',
      x: 673,
      y: 380,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 673, y: 380, value: '交换机' }
    },
    {
      id: '81',
      type: 'switch',
      x: 473,
      y: 417,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 473, y: 417, value: '交换机' }
    }
  ],
  edges: [
    {
      id: '5a93be03-4a83-4e0d-9f51-66dc35b91c69',
      type: 'polyline',
      properties: {},
      sourceNodeId: '41',
      targetNodeId: '8',
      sourceAnchorId: '41_1',
      targetAnchorId: '8_0',
      startPoint: { x: 481, y: 173 },
      endPoint: { x: 673, y: 350 },
      pointsList: [
        { x: 481, y: 173 },
        { x: 673, y: 173 },
        { x: 673, y: 350 }
      ]
    },
    {
      id: '3927ff57-8721-4b14-93dc-614dc359f864',
      type: 'polyline',
      properties: {},
      sourceNodeId: '51',
      targetNodeId: '8',
      sourceAnchorId: '51_2',
      targetAnchorId: '8_0',
      startPoint: { x: 767, y: 231 },
      endPoint: { x: 673, y: 350 },
      pointsList: [
        { x: 767, y: 231 },
        { x: 767, y: 320 },
        { x: 673, y: 320 },
        { x: 673, y: 350 }
      ]
    },
    {
      id: '214ca0b3-1a1f-43f7-a00b-f1e01183b82a',
      type: 'polyline',
      properties: {},
      sourceNodeId: '5',
      targetNodeId: '8',
      sourceAnchorId: '5_1',
      targetAnchorId: '8_0',
      startPoint: { x: 530, y: 300 },
      endPoint: { x: 673, y: 350 },
      pointsList: [
        { x: 530, y: 300 },
        { x: 673, y: 300 },
        { x: 673, y: 350 }
      ]
    },
    {
      id: '007d8b7b-f77b-4891-8e55-f2515bdb133a',
      type: 'polyline',
      properties: {},
      sourceNodeId: '4',
      targetNodeId: '81',
      sourceAnchorId: '4_2',
      targetAnchorId: '81_0',
      startPoint: { x: 350, y: 330 },
      endPoint: { x: 473, y: 387 },
      pointsList: [
        { x: 350, y: 330 },
        { x: 350, y: 357 },
        { x: 473, y: 357 },
        { x: 473, y: 387 }
      ]
    },
    {
      id: 'e440b0ea-f69a-4c3a-bdbf-778049faf7bc',
      type: 'polyline',
      properties: {},
      sourceNodeId: '81',
      targetNodeId: '6',
      sourceAnchorId: '81_2',
      targetAnchorId: '6_0',
      startPoint: { x: 473, y: 447 },
      endPoint: { x: 656, y: 506 },
      pointsList: [
        { x: 473, y: 447 },
        { x: 473, y: 476 },
        { x: 656, y: 476 },
        { x: 656, y: 506 }
      ]
    },
    {
      id: '7cfd444b-04ba-4383-b282-7da9726800cf',
      type: 'polyline',
      properties: {},
      sourceNodeId: '8',
      targetNodeId: '6',
      sourceAnchorId: '8_2',
      targetAnchorId: '6_0',
      startPoint: { x: 673, y: 410 },
      endPoint: { x: 656, y: 506 },
      pointsList: [
        { x: 673, y: 410 },
        { x: 673, y: 458 },
        { x: 656, y: 458 },
        { x: 656, y: 506 }
      ]
    },
    {
      id: '3d5c2846-9e14-4110-9952-d623541cc55f',
      type: 'polyline',
      properties: {},
      sourceNodeId: '6',
      targetNodeId: '31',
      sourceAnchorId: '6_2',
      targetAnchorId: '31_0',
      startPoint: { x: 656, y: 566 },
      endPoint: { x: 652, y: 628 },
      pointsList: [
        { x: 656, y: 566 },
        { x: 656, y: 597 },
        { x: 652, y: 597 },
        { x: 652, y: 628 }
      ]
    },
    {
      id: '15c820d6-2265-47ec-85e8-69ffd631f068',
      type: 'polyline',
      properties: {},
      sourceNodeId: '31',
      targetNodeId: '7',
      sourceAnchorId: '31_2',
      targetAnchorId: '7_0',
      startPoint: { x: 652, y: 688 },
      endPoint: { x: 654, y: 794 },
      pointsList: [
        { x: 652, y: 688 },
        { x: 652, y: 741 },
        { x: 654, y: 741 },
        { x: 654, y: 794 }
      ]
    }
  ]
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
  console.log('Control 插件美化按钮添加成功', lf.extension.control)

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

  // 获取设备和交换机数据并设置拖拽面板项
  Promise.all([fetchDevices(), fetchSwitches(), loadLatestTopology()]).then(
    () => {
      lf.extension.dndPanel.setPatternItems(leftMenus.value)
    }
  )
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
    const graphData = lf.getGraphData()

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
        node.x = dagreNode.x
        node.y = dagreNode.y
        // 更新文本位置
        if (node.text && typeof node.text === 'object') {
          node.text.x = dagreNode.x
          node.text.y = dagreNode.y
        }
      }
    })

    // 清空边的路径点，让LogicFlow自动重新计算
    if (graphData.edges) {
      graphData.edges.forEach((edge) => {
        // 删除旧的路径点信息，让LogicFlow重新计算
        delete edge.pointsList
        delete edge.startPoint
        delete edge.endPoint
      })
    }

    // 重新渲染图，这会根据新的节点位置自动计算连线
    lfInstance.render(graphData)

    // 适应画布
    setTimeout(() => {
      lfInstance.fitView(20)
    }, 100)

    message.success('布局美化完成')
  } catch (error) {
    console.error('美化失败:', error)
    message.error('美化失败，请确保已安装dagre库')
  }
}

// 更新左侧菜单项
const updateLeftMenus = () => {
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

  // 添加设备项
  devices.value.forEach((device) => {
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

  // 添加交换机项
  switches.value.forEach((switchItem) => {
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
    // 一键美化按钮样式
    .lf-control-item {
      &[data-key='beautify'] {
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
  }
}
</style>
