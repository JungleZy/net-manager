<template>
  <div class="p-[12px] size-full topology-area">
    <div class="size-full bg-white rounded-lg shadow p-[6px] relative">
      <div class="w-full h-full project-grid" ref="container"></div>
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
import SvgNode from '@/common/node/SvgNode'
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

const data = ref({})

onMounted(() => {
  nextTick(() => {
    initTopology()
  })
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
    plugins: [DndPanel, SelectionSelect, MiniMap, Highlight],
    pluginsOptions: pluginsOptions(),
    adjustEdgeStartAndEnd: true
  })
  lf.register(CustomHtml)
  // 注册所有自定义节点
  customNodes.forEach((node) => {
    lf.register(node)
  })

  lf.render(data.value)
  lf.extension.dndPanel.setPatternItems([])

  // 监听节点拖拽添加事件，添加后从leftMenus中移除
  lf.on('node:dnd-add', (nodeData) => {
    // 根据添加的节点类型和标签从leftMenus中移除对应项
    const nodeType = nodeData.type
    const nodeText = nodeData.text
    console.log(nodeData)

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
}
</style>
