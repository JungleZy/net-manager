<template>
  <div class="p-[12px] size-full network" ref="networkWrapperRef">
    <div
      class="size-full bg-white rounded-lg shadow p-[6px] relative"
      ref="networkContainerRef"
    >
      <!-- 拓扑图容器 -->
      <div class="w-full h-full" ref="containerRef"></div>

      <!-- 状态统计面板 -->
      <div class="stats-panel">
        <div class="stat-item">
          <span class="stat-label">总节点:</span>
          <span class="stat-value">{{ stats.totalNodes }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">在线:</span>
          <span class="stat-value online">{{ stats.onlineNodes }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">离线:</span>
          <span class="stat-value offline">{{ stats.offlineNodes }}</span>
        </div>
      </div>

      <!-- 控制按钮 -->
      <div class="control-panel">
        <a-button
          @click="handleRefresh"
          :loading="loading"
          class="layout-center"
        >
          <template #icon>
            <ReloadOutlined />
          </template>
        </a-button>
        <a-button @click="handleCenter" class="layout-center">
          <template #icon>
            <AimOutlined />
          </template>
        </a-button>
        <a-dropdown v-if="!isFullscreen">
          <template #overlay>
            <a-menu @click="handleFullscreenMenuClick">
              <a-menu-item key="page">
                <template #icon>
                  <FullscreenOutlined />
                </template>
                页内全屏
              </a-menu-item>
              <a-menu-item key="screen">
                <template #icon>
                  <FullscreenOutlined />
                </template>
                屏幕全屏
              </a-menu-item>
            </a-menu>
          </template>
          <a-button class="layout-center">
            <template #icon>
              <FullscreenOutlined />
            </template>
          </a-button>
        </a-dropdown>

        <a-button class="layout-center" @click="exitFullscreen" v-else>
          <template #icon>
            <FullscreenExitOutlined />
          </template>
        </a-button>
      </div>

      <!-- 节点详情 Popover (自定义) -->
      <DeviceNodeDetailPopover
        :visible="popoverVisible"
        v-model="devices"
        v-model:index="deviceIndex"
        :position="popoverPosition"
        :placement="popoverPlacement"
        :max-height="popoverMaxHeight"
        :arrow-offset="popoverArrowOffset"
        @close="handlePopoverClose"
      />
      <SwitchNodeDetailPopover
        :visible="popoverVisible"
        v-model="switches"
        v-model:index="switchIndex"
        :position="popoverPosition"
        :placement="popoverPlacement"
        :max-height="popoverMaxHeight"
        :arrow-offset="popoverArrowOffset"
        @close="handlePopoverClose"
      />
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  onMounted,
  onUnmounted,
  nextTick,
  computed,
  shallowRef,
  useTemplateRef
} from 'vue'
import { LogicFlow } from '@logicflow/core'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'
import { default as customNodes } from '@/common/node/index'
import { default as customEdges } from '@/common/edge/index'
import TopologyApi from '@/common/api/topology'
import DeviceApi from '@/common/api/device'
import SwitchApi from '@/common/api/switch'
import { wsCode } from '@/common/ws/Ws'
import { PubSub } from '@/common/utils/PubSub'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined,
  AimOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined
} from '@ant-design/icons-vue'
import DeviceNodeDetailPopover from '../../components/network/DeviceNodeDetailPopover.vue'
import SwitchNodeDetailPopover from '../../components/network/SwitchNodeDetailPopover.vue'

const containerRef = useTemplateRef('containerRef')
const networkWrapperRef = useTemplateRef('networkWrapperRef')
const networkContainerRef = useTemplateRef('networkContainerRef')
const devices = ref([])
const switches = ref([])
// 使用 ref 确保响应式更新能够正确触发
let lf = null
const loading = ref(false)
const topologyData = shallowRef({ nodes: [], edges: [] })
const deviceStatusMap = shallowRef(new Map()) // 存储设备状态 {device_id: 'online'|'offline'}
const edgeDataMap = shallowRef(new Map()) // 存储边的数据传输状态 {edgeId: hasData}
const isComponentMounted = ref(false)

// 优化：使用 Map 加速设备查找
const deviceIdMap = shallowRef(new Map()) // {id/client_id: device}
const switchIdMap = shallowRef(new Map()) // {id/switch_id: switch}

// 全屏相关状态
const isFullscreen = ref(false)
const fullscreenMode = ref('') // 'page' | 'screen'

// Popover 相关状态
const popoverVisible = ref(false)
const selectedNode = ref(null)
const deviceIndex = ref(0)
const switchIndex = ref(0)
const popoverPosition = ref({ x: 0, y: 0 })
const popoverPlacement = ref('right') // 弹出方向: 'right' | 'left' | 'top' | 'bottom'
const popoverMaxHeight = ref(600) // 弹出框最大高度（像素）
const popoverArrowOffset = ref(0) // 箭头Y轴偏移量（像素）

// ResizeObserver 实例
let resizeObserver = null

// 防抖定时器
let resizeDebounceTimer = null
let updateEdgesDebounceTimer = null

// 插件配置移到外部常量,避免重复创建对象
const PLUGINS_OPTIONS = Object.freeze({})

// 处理全屏菜单点击
const handleFullscreenMenuClick = ({ key }) => {
  if (key === 'page') {
    enterPageFullscreen()
  } else if (key === 'screen') {
    enterScreenFullscreen()
  } else if (key === 'exit') {
    exitFullscreen()
  }
}

// 页内全屏
const enterPageFullscreen = () => {
  const wrapper = networkWrapperRef.value
  if (!wrapper) return

  // 添加页内全屏样式
  wrapper.classList.add('page-fullscreen')
  isFullscreen.value = true
  fullscreenMode.value = 'page'

  // 重新调整拓扑图尺寸
  nextTick(() => {
    resizeLogicFlow()
  })

  message.success('已进入页内全屏模式')
}

// 屏幕全屏
const enterScreenFullscreen = async () => {
  const container = networkContainerRef.value
  if (!container) return

  try {
    if (container.requestFullscreen) {
      await container.requestFullscreen()
    } else if (container.webkitRequestFullscreen) {
      await container.webkitRequestFullscreen()
    } else if (container.mozRequestFullScreen) {
      await container.mozRequestFullScreen()
    } else if (container.msRequestFullscreen) {
      await container.msRequestFullscreen()
    }

    isFullscreen.value = true
    fullscreenMode.value = 'screen'

    // 重新调整拓扑图尺寸
    nextTick(() => {
      resizeLogicFlow()
    })

    message.success('已进入屏幕全屏模式')
  } catch (error) {
    console.error('进入全屏失败:', error)
    message.error('进入全屏失败')
  }
}

// 退出全屏
const exitFullscreen = async () => {
  if (fullscreenMode.value === 'page') {
    // 退出页内全屏
    const wrapper = networkWrapperRef.value
    if (wrapper) {
      wrapper.classList.remove('page-fullscreen')
    }

    isFullscreen.value = false
    fullscreenMode.value = ''

    // 重新调整拓扑图尺寸
    nextTick(() => {
      resizeLogicFlow()
    })

    message.success('已退出页内全屏模式')
  } else if (fullscreenMode.value === 'screen') {
    // 退出屏幕全屏
    try {
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        await document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        await document.msExitFullscreen()
      }

      isFullscreen.value = false
      fullscreenMode.value = ''

      message.success('已退出屏幕全屏模式')
    } catch (error) {
      console.error('退出全屏失败:', error)
      message.error('退出全屏失败')
    }
  }
}

// 监听全屏状态变化（用户按ESC退出全屏）
const handleFullscreenChange = () => {
  const isInFullscreen = !!(
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  )

  if (!isInFullscreen && fullscreenMode.value === 'screen') {
    // 用户按ESC键退出了全屏
    isFullscreen.value = false
    fullscreenMode.value = ''

    // 重新调整拓扑图尺寸
    nextTick(() => {
      resizeLogicFlow()
    })
  }
}

// 统计信息（优化：避免 Array.from 和 filter）
const stats = computed(() => {
  const totalNodes = topologyData.value.nodes.length
  let onlineNodes = 0

  // 优化：直接遍历 Map，避免创建中间数组
  for (const status of deviceStatusMap.value.values()) {
    if (status === 'online') onlineNodes++
  }

  return {
    totalNodes,
    onlineNodes,
    offlineNodes: totalNodes - onlineNodes
  }
})

// 更新设备/交换机 Map（优化查找性能）
const updateDeviceIdMap = () => {
  const newDeviceMap = new Map()
  for (const device of devices.value) {
    if (device.id) newDeviceMap.set(device.id, device)
    if (device.client_id) newDeviceMap.set(device.client_id, device)
  }
  deviceIdMap.value = newDeviceMap
}

const updateSwitchIdMap = () => {
  const newSwitchMap = new Map()
  for (const switchDevice of switches.value) {
    if (switchDevice.id) newSwitchMap.set(switchDevice.id, switchDevice)
    if (switchDevice.switch_id)
      newSwitchMap.set(switchDevice.switch_id, switchDevice)
  }
  switchIdMap.value = newSwitchMap
}

// 初始化LogicFlow
const initLogicFlow = () => {
  // 清理旧实例
  if (lf) {
    try {
      lf.destroy()
    } catch (error) {
      console.warn('清理旧 LogicFlow 实例失败:', error)
    }
    lf = null
  }

  // 确保 container 已正确挂载并获取其尺寸
  const container = containerRef.value
  if (!container) {
    console.error('容器元素未找到')
    return
  }

  const width = container.offsetWidth || 800
  const height = container.offsetHeight || 600

  try {
    lf = new LogicFlow({
      grid: false,
      container: container,
      width: width,
      height: height,
      keyboard: {
        enabled: false // 禁用键盘操作
      },
      // 边的默认样式配置
      edgeType: 'line',
      style: {
        edge: {
          stroke: '#afafaf',
          strokeWidth: 2
        },
        edgeHover: {
          stroke: '#afafaf', // 悬停时保持原样式
          strokeWidth: 2
        },
        edgeSelected: {
          stroke: '#afafaf', // 选中时保持原样式
          strokeWidth: 2
        },
        arrow: {
          offset: 0,
          verticalLength: 0
        }
      },
      autoExpand: false,
      pluginsOptions: PLUGINS_OPTIONS,
      adjustEdgeStartAndEnd: true,
      // 性能优化配置
      stopScrollGraph: true,
      stopZoomGraph: false,
      snapToGrid: true,
      partial: true, // 启用局部渲染
      // 禁用所有编辑功能
      nodeTextEdit: false, // 禁用节点文本编辑
      edgeTextEdit: false, // 禁用边文本编辑
      nodeTextDraggable: false, // 禁用节点文本拖拽
      edgeTextDraggable: false, // 禁用边文本拖拽
      isSilentMode: true, // 静默模式，禁止编辑
      textEdit: false // 全局禁用文本编辑
    })

    // 注册自定义节点
    for (const node of customNodes) {
      lf.register(node)
    }

    // 注册自定义边
    for (const edge of customEdges) {
      lf.register(edge)
    }
  } catch (error) {
    console.error('LogicFlow 初始化失败:', error)
    message.error('拓扑图初始化失败')
    return
  }

  // 渲染拓扑图
  lf.render(topologyData.value)

  // 监听节点点击事件
  lf.on('node:click', ({ data, e }) => {
    handleNodeClick(data, e)
  })
  Promise.all([fetchDevices(), fetchSwitches()])
    .then(() => {
      console.log('设备列表和交换机列表初始化完成')
      // 初始化PubSub订阅
      initPubSubSubscriptions()
      // 加载最新的拓扑图数据并渲染
      Promise.all([loadLatestTopology()])
        .then(() => {
          // 数据加载完成后居中显示
          handleCenterView(lf)
        })
        .catch((error) => {
          console.error('初始化数据加载失败:', error)
        })
    })
    .catch((error) => {
      console.error('初始化数据加载失败:', error)
    })
}

// 加载最新拓扑图
const loadLatestTopology = async () => {
  if (!lf) {
    console.warn('LogicFlow 实例未初始化')
    return
  }

  loading.value = true
  try {
    const response = await TopologyApi.getLatestTopology()
    if (response?.data?.content) {
      const content = response.data.content

      // 优化：将所有边的类型修改为 animated-line，支持动画效果
      if (content.edges && content.edges.length > 0) {
        for (const edge of content.edges) {
          edge.type = 'animated-line'
        }
        console.log(
          `已将 ${content.edges.length} 条边设置为 animated-line 类型`
        )
      }

      topologyData.value = content

      // 根据 devices 和 switches 初始化节点状态（优化：使用 Map 加速查找）
      if (content.nodes && content.nodes.length > 0) {
        for (const node of content.nodes) {
          const deviceId = node.properties?.data?.id || node.id

          // 优化：使用 Map 查找而非 find
          const device = deviceIdMap.value.get(deviceId)
          const switchDevice = switchIdMap.value.get(deviceId)

          if (device) {
            const status = device.online ? 'online' : 'offline'
            deviceStatusMap.value.set(deviceId, status)
            if (node.properties) {
              node.properties.status = status
            } else {
              node.properties = { status }
            }
          } else if (switchDevice) {
            const status = switchDevice.online ? 'online' : 'offline'
            deviceStatusMap.value.set(deviceId, status)
            if (node.properties) {
              node.properties.status = status
            } else {
              node.properties = { status }
            }
          } else {
            const initialStatus = node.properties?.status || 'offline'
            deviceStatusMap.value.set(deviceId, initialStatus)
          }
        }
      }

      // 渲染拓扑图
      lf.render(content)

      // 根据设备网络流量数据初始化边的动画状态
      updateEdgesDataStatus()
    } else {
      // 没有保存的拓扑图,渲染空数据
      lf.render(topologyData.value)
    }
  } catch (error) {
    console.error('加载拓扑图失败:', error)
    message.error('加载拓扑图失败')
    // 失败时渲染空数据
    lf.render(topologyData.value)
  } finally {
    loading.value = false
  }
}

// 根据设备网络流量数据更新所有边的数据传输状态（优化：减少嵌套循环和重复查找）
const updateEdgesDataStatus = () => {
  if (!lf) return

  const graphData = lf.getGraphData()
  if (!graphData) return

  // 优化：预先构建节点 Map，避免重复 find
  const nodeByDeviceId = new Map()
  const nodeByIp = new Map()

  for (const node of graphData.nodes) {
    const deviceId =
      node.properties?.data?.id || node.properties?.data?.client_id
    const ip = node.properties?.data?.ip

    if (deviceId) nodeByDeviceId.set(deviceId, node)
    if (ip) nodeByIp.set(ip, node)
  }

  // 遍历所有设备，检查网络流量数据
  for (const device of devices.value) {
    const deviceId = device.client_id || device.id

    // 解析网络接口数据
    let interfaces = []
    if (device.networks) {
      if (typeof device.networks === 'string') {
        try {
          interfaces = JSON.parse(device.networks)
        } catch (e) {
          console.warn('解析 networks 字段失败:', e)
          continue
        }
      } else if (Array.isArray(device.networks)) {
        interfaces = device.networks
      }
    }

    // 检查每个接口的流量数据
    for (const iface of interfaces) {
      const hasData =
        (iface.upload_rate && iface.upload_rate > 0) ||
        (iface.download_rate && iface.download_rate > 0)

      if (hasData && iface.gateway) {
        const gatewayNode = nodeByIp.get(iface.gateway)
        const currentDeviceNode = nodeByDeviceId.get(deviceId)

        if (gatewayNode && currentDeviceNode) {
          updateEdgeDataStatus(currentDeviceNode.id, gatewayNode.id, hasData)
        }
      }
    }
  }

  // 遍历所有交换机，检查接口流量数据
  for (const switchDevice of switches.value) {
    const deviceId = switchDevice.switch_id || switchDevice.id

    // 检查接口流量数据
    if (switchDevice.interface_info) {
      const interfaces = switchDevice.interface_info.interfaces || []

      for (const iface of interfaces) {
        const hasData =
          (iface.in_octets_rate && iface.in_octets_rate > 0) ||
          (iface.out_octets_rate && iface.out_octets_rate > 0)

        // 如果有连接的设备ID，更新边状态
        if (hasData && iface.connected_device_id) {
          updateEdgeDataStatus(deviceId, iface.connected_device_id, hasData)
        }
      }
    }
  }
}

// 刷新拓扑图
const handleRefresh = async () => {
  await loadLatestTopology()
  message.success('刷新成功')
}

// 居中显示（供控制按钮调用）
const handleCenter = () => {
  handleCenterView(lf)
}

// 处理节点点击事件（优化：使用 Map 加速查找）
const handleNodeClick = (nodeData, event) => {
  if (!nodeData) return

  // 如果是分组节点,不弹出详情卡片
  if (nodeData.type === 'customGroup') {
    return
  }

  // 提取节点信息
  const deviceData = nodeData.properties?.data || {}
  const deviceId = deviceData.id || nodeData.id

  // 优化：使用 Map 查找，然后再在数组中 findIndex
  const device = deviceIdMap.value.get(deviceId)
  const switchDevice = switchIdMap.value.get(deviceId)

  deviceIndex.value = device ? devices.value.indexOf(device) : -1
  switchIndex.value = switchDevice ? switches.value.indexOf(switchDevice) : -1

  console.log('deviceIndex:', deviceIndex.value)
  console.log('switchIndex:', switchIndex.value)
  if (deviceIndex.value === -1 && switchIndex.value === -1) {
    message.error('该节点为虚拟设备，不支持查看详情!')
    return
  }

  // 计算 Popover 位置（节点中心点）
  const container = containerRef.value
  if (container) {
    const containerRect = container.getBoundingClientRect()
    const transform = lf.getTransform()

    // 计算节点在画布中的位置（考虑缩放和平移）
    const canvasX = nodeData.x * transform.SCALE_X + transform.TRANSLATE_X
    const canvasY = nodeData.y * transform.SCALE_Y + transform.TRANSLATE_Y

    // 智能计算 Popover 位置和方向
    calculatePopoverPosition(canvasX, canvasY, containerRect)
  }

  // 显示 Popover
  popoverVisible.value = true
}

// 智能计算 Popover 位置和方向
const calculatePopoverPosition = (nodeX, nodeY, containerRect) => {
  // 安全边距（像素）
  const SAFE_MARGIN = 20
  // Popover 预估尺寸
  const POPOVER_WIDTH = 450

  // 容器尺寸
  const containerWidth = containerRect.width
  const containerHeight = containerRect.height

  // 计算弹出框最大高度（画布高度的80%）
  popoverMaxHeight.value = Math.floor(containerHeight * 0.8)
  // 使用实际最大高度进行空间计算
  const POPOVER_HEIGHT = popoverMaxHeight.value

  // 节点偏移量（避免遮挡节点本身）
  const NODE_OFFSET = 70

  // 计算各个方向的可用空间
  const spaceRight = containerWidth - nodeX - SAFE_MARGIN
  const spaceLeft = nodeX - SAFE_MARGIN
  // 下方和上方需要考虑节点偏移量
  const spaceBottom = containerHeight - nodeY - NODE_OFFSET - SAFE_MARGIN
  const spaceTop = nodeY - NODE_OFFSET - SAFE_MARGIN

  let placement = 'right'
  let finalX = nodeX
  let finalY = nodeY

  // 优先级：右 > 左 > 下 > 上
  if (spaceRight >= POPOVER_WIDTH) {
    // 右侧有足够空间，检查上下边界是否足够（需要垂直居中）
    const halfHeight = POPOVER_HEIGHT / 2
    if (
      nodeY >= halfHeight + SAFE_MARGIN &&
      nodeY + halfHeight + SAFE_MARGIN <= containerHeight
    ) {
      placement = 'right'
      finalX = nodeX
      finalY = nodeY
    } else {
      // 上下边界不足，调整Y坐标
      placement = 'right'
      finalX = nodeX
      // 确保Popover不超出上下边界
      if (nodeY < halfHeight + SAFE_MARGIN) {
        finalY = halfHeight + SAFE_MARGIN
      } else if (nodeY + halfHeight + SAFE_MARGIN > containerHeight) {
        finalY = containerHeight - halfHeight - SAFE_MARGIN
      } else {
        finalY = nodeY
      }
    }
  } else if (spaceLeft >= POPOVER_WIDTH) {
    // 左侧有足够空间，检查上下边界是否足够（需要垂直居中）
    const halfHeight = POPOVER_HEIGHT / 2
    if (
      nodeY >= halfHeight + SAFE_MARGIN &&
      nodeY + halfHeight + SAFE_MARGIN <= containerHeight
    ) {
      placement = 'left'
      finalX = nodeX
      finalY = nodeY
    } else {
      // 上下边界不足，调整Y坐标
      placement = 'left'
      finalX = nodeX
      // 确保Popover不超出上下边界
      if (nodeY < halfHeight + SAFE_MARGIN) {
        finalY = halfHeight + SAFE_MARGIN
      } else if (nodeY + halfHeight + SAFE_MARGIN > containerHeight) {
        finalY = containerHeight - halfHeight - SAFE_MARGIN
      } else {
        finalY = nodeY
      }
    }
  } else if (spaceBottom >= POPOVER_HEIGHT) {
    // 下方有足够空间，检查左右边界是否足够（需要水平居中）
    const halfWidth = POPOVER_WIDTH / 2
    if (
      nodeX >= halfWidth + SAFE_MARGIN &&
      nodeX + halfWidth + SAFE_MARGIN <= containerWidth
    ) {
      placement = 'bottom'
      finalX = nodeX
      finalY = nodeY
    } else {
      // 左右边界不足，调整X坐标
      placement = 'bottom'
      finalY = nodeY
      // 确保Popover不超出左右边界
      if (nodeX < halfWidth + SAFE_MARGIN) {
        finalX = halfWidth + SAFE_MARGIN
      } else if (nodeX + halfWidth + SAFE_MARGIN > containerWidth) {
        finalX = containerWidth - halfWidth - SAFE_MARGIN
      } else {
        finalX = nodeX
      }
    }
  } else if (spaceTop >= POPOVER_HEIGHT) {
    // 上方有足够空间，检查左右边界是否足够（需要水平居中）
    const halfWidth = POPOVER_WIDTH / 2
    if (
      nodeX >= halfWidth + SAFE_MARGIN &&
      nodeX + halfWidth + SAFE_MARGIN <= containerWidth
    ) {
      placement = 'top'
      finalX = nodeX
      finalY = nodeY
    } else {
      // 左右边界不足，调整X坐标
      placement = 'top'
      finalY = nodeY
      // 确保Popover不超出左右边界
      if (nodeX < halfWidth + SAFE_MARGIN) {
        finalX = halfWidth + SAFE_MARGIN
      } else if (nodeX + halfWidth + SAFE_MARGIN > containerWidth) {
        finalX = containerWidth - halfWidth - SAFE_MARGIN
      } else {
        finalX = nodeX
      }
    }
  } else {
    // 所有方向空间都不足，选择空间最大的方向并调整位置
    const maxSpace = Math.max(spaceRight, spaceLeft, spaceBottom, spaceTop)
    if (maxSpace === spaceRight) {
      placement = 'right'
      // 调整Y坐标确保不超出上下边界
      const halfHeight = POPOVER_HEIGHT / 2
      if (nodeY < halfHeight + SAFE_MARGIN) {
        finalY = halfHeight + SAFE_MARGIN
      } else if (nodeY + halfHeight + SAFE_MARGIN > containerHeight) {
        finalY = containerHeight - halfHeight - SAFE_MARGIN
      } else {
        finalY = nodeY
      }
      finalX = nodeX
    } else if (maxSpace === spaceLeft) {
      placement = 'left'
      // 调整Y坐标确保不超出上下边界
      const halfHeight = POPOVER_HEIGHT / 2
      if (nodeY < halfHeight + SAFE_MARGIN) {
        finalY = halfHeight + SAFE_MARGIN
      } else if (nodeY + halfHeight + SAFE_MARGIN > containerHeight) {
        finalY = containerHeight - halfHeight - SAFE_MARGIN
      } else {
        finalY = nodeY
      }
      finalX = nodeX
    } else if (maxSpace === spaceBottom) {
      placement = 'bottom'
      // 调整X坐标确保不超出左右边界
      const halfWidth = POPOVER_WIDTH / 2
      if (nodeX < halfWidth + SAFE_MARGIN) {
        finalX = halfWidth + SAFE_MARGIN
      } else if (nodeX + halfWidth + SAFE_MARGIN > containerWidth) {
        finalX = containerWidth - halfWidth - SAFE_MARGIN
      } else {
        finalX = nodeX
      }
      finalY = nodeY
    } else {
      placement = 'top'
      // 调整X坐标确保不超出左右边界
      const halfWidth = POPOVER_WIDTH / 2
      if (nodeX < halfWidth + SAFE_MARGIN) {
        finalX = halfWidth + SAFE_MARGIN
      } else if (nodeX + halfWidth + SAFE_MARGIN > containerWidth) {
        finalX = containerWidth - halfWidth - SAFE_MARGIN
      } else {
        finalX = nodeX
      }
      finalY = nodeY
    }
  }

  // 设置位置和方向
  popoverPosition.value = { x: finalX, y: finalY }
  popoverPlacement.value = placement

  // 计算箭头偏移量（仅对上下方向）
  if (placement === 'top' || placement === 'bottom') {
    // 箭头需要偏移的距离 = 节点Y坐标 - 弹出框Y坐标
    popoverArrowOffset.value = nodeY - finalY
  } else {
    // 左右方向不需要偏移
    popoverArrowOffset.value = 0
  }

  console.log(
    `Popover弹出方向: ${placement}, 位置: (${finalX}, ${finalY})，节点位置: (${nodeX}, ${nodeY}), 箭头偏移: ${popoverArrowOffset.value}px`
  )
}

// 处理Popover关闭
const handlePopoverClose = () => {
  popoverVisible.value = false
  selectedNode.value = null
}

// 居中显示功能（供 LogicFlow 实例调用）
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

    // 优化：使用条件判断代替 Math.min/max，减少函数调用
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity

    const nodes = graphData.nodes
    for (let i = 0, len = nodes.length; i < len; i++) {
      const node = nodes[i]
      const nodeWidth = node.properties?.width || 60
      const nodeHeight = node.properties?.height || 60
      const halfWidth = nodeWidth / 2
      const halfHeight = nodeHeight / 2

      const left = node.x - halfWidth
      const right = node.x + halfWidth
      const top = node.y - halfHeight
      const bottom = node.y + halfHeight

      if (left < minX) minX = left
      if (right > maxX) maxX = right
      if (top < minY) minY = top
      if (bottom > maxY) maxY = bottom
    }

    // 计算内容中心点
    const contentCenterX = (minX + maxX) / 2
    const contentCenterY = (minY + maxY) / 2

    // 计算画布中心点
    const container = containerRef.value
    if (!container) return

    const canvasWidth = container.offsetWidth
    const canvasHeight = container.offsetHeight
    const canvasCenterX = canvasWidth / 2
    const canvasCenterY = canvasHeight / 2

    // 计算需要平移的距离
    const deltaX = canvasCenterX - contentCenterX
    const deltaY = canvasCenterY - contentCenterY

    // 平移画布
    lfInstance.translate(deltaX, deltaY)
  } catch (error) {
    console.error('居中操作失败:', error)
  }
}

// 更新节点状态
const updateNodeStatus = (deviceId, status) => {
  if (!lf) return

  try {
    // 更新状态映射
    deviceStatusMap.value.set(deviceId, status)

    // 查找对应的节点
    const graphData = lf.getGraphData()
    const node = graphData.nodes.find(
      (n) => n.properties?.data?.id === deviceId || n.id === deviceId
    )

    if (node) {
      // 更新节点属性
      const nodeModel = lf.getNodeModelById(node.id)
      if (nodeModel) {
        nodeModel.setProperties({
          ...node.properties,
          status: status
        })
      } else {
        console.warn(`无法获取节点模型: ${node.id}`)
      }

      // 如果设备离线,停止所有与该节点相连的边的动画
      if (status === 'offline') {
        stopNodeRelatedEdgesAnimation(node.id, graphData)
      }
    } else {
      console.warn(
        `未找到设备ID为 ${deviceId} 的节点，当前拓扑图中有 ${graphData.nodes.length} 个节点`
      )
      // 打印所有节点的ID用于调试
      if (graphData.nodes.length > 0 && graphData.nodes.length <= 10) {
        console.log(
          '当前节点列表:',
          graphData.nodes.map((n) => ({
            id: n.id,
            dataId: n.properties?.data?.id,
            status: n.properties?.status
          }))
        )
      }
    }
  } catch (error) {
    console.error('更新节点状态失败:', error)
  }
}

// 停止节点相关边的动画
const stopNodeRelatedEdgesAnimation = (nodeId, graphData) => {
  if (!lf) return

  try {
    // 查找所有与该节点相连的边
    const relatedEdges = graphData.edges.filter(
      (edge) => edge.sourceNodeId === nodeId || edge.targetNodeId === nodeId
    )

    if (relatedEdges.length > 0) {
      console.log(`设备离线，停止 ${relatedEdges.length} 条相关边的动画`)

      for (const edge of relatedEdges) {
        // 关闭边动画
        lf.closeEdgeAnimation(edge.id)

        // 更新边状态映射为 false
        edgeDataMap.value.set(edge.id, false)

        console.log(`已停止边 ${edge.id} 的动画 (节点 ${nodeId} 离线)`)
      }
    }
  } catch (error) {
    console.error('停止节点相关边动画失败:', error)
  }
}

// 更新边的数据传输状态
const updateEdgeDataStatus = (sourceId, targetId, hasData) => {
  if (!lf) return

  try {
    const graphData = lf.getGraphData()

    // 查找连接这两个节点的边
    const edge = graphData.edges.find(
      (e) =>
        (e.sourceNodeId === sourceId && e.targetNodeId === targetId) ||
        (e.sourceNodeId === targetId && e.targetNodeId === sourceId)
    )

    if (edge) {
      // 检查边的当前状态
      const currentState = edgeDataMap.value.get(edge.id)

      // 如果当前状态和需要更新的状态一致，则跳过更新
      if (currentState === hasData) {
        console.log(`边 ${edge.id} 状态未变化 (${hasData})，跳过更新`)
        return
      }

      console.log(`更新边 ${edge.id} 状态: ${currentState} -> ${hasData}`)

      // 更新状态映射
      edgeDataMap.value.set(edge.id, hasData)

      // 根据状态开启或关闭动画
      if (hasData) {
        lf?.openEdgeAnimation(edge.id)
      } else {
        lf?.closeEdgeAnimation(edge.id)
      }
    } else {
      console.warn(`未找到连接 ${sourceId} 和 ${targetId} 的边`)
      // 打印所有边的信息用于调试
      if (graphData.edges.length > 0 && graphData.edges.length <= 10) {
        console.log(
          '当前边列表:',
          graphData.edges.map((e) => ({
            id: e.id,
            sourceNodeId: e.sourceNodeId,
            targetNodeId: e.targetNodeId
          }))
        )
      }
    }
  } catch (error) {
    console.error('更新边数据状态失败:', error)
  }
}

// 处理设备状态更新（优化：使用 Map 加速查找）
const handleDeviceStatusUpdate = (data) => {
  console.log('设备状态更新:', data)

  if (!data) return

  const deviceId = data.client_id || data.device_id || data.id
  const status = data.status || (data.online ? 'online' : 'offline')

  if (deviceId) {
    updateNodeStatus(deviceId, status)

    // 优化：使用 Map 查找
    const device = deviceIdMap.value.get(deviceId)
    if (device) {
      device.status = status
      device.online = status === 'online'
      device.last_seen = new Date().toISOString()
    }

    const switchDevice = switchIdMap.value.get(deviceId)
    if (switchDevice) {
      switchDevice.status = status
      switchDevice.online = status === 'online'
      switchDevice.last_seen = new Date().toISOString()
    }
    console.log('设备列表已更新:', devices.value)
  }
}

// 处理SNMP设备更新（包含接口流量数据）
const handleSnmpDeviceUpdate = (data) => {
  console.log('SNMP设备更新:', data)

  if (!data) return

  const deviceId = data.switch_id || data.device_id

  // 更新设备在线状态
  if (deviceId) {
    updateNodeStatus(deviceId, 'online')
  }

  // 更新交换机列表中的对应数据（优化：使用 Map 查找）
  if (deviceId) {
    const switchDevice = switchIdMap.value.get(deviceId)
    if (switchDevice) {
      Object.assign(switchDevice, data, {
        last_updated: new Date().toISOString()
      })
    } else {
      // 新交换机，添加到列表
      const newSwitch = {
        ...data,
        id: deviceId,
        last_updated: new Date().toISOString()
      }
      switches.value.push(newSwitch)
      // 更新 Map
      updateSwitchIdMap()
    }
  }

  // 检查接口流量数据，更新边的动画状态
  if (data.interface_info) {
    const interfaces = data.interface_info.interfaces || []

    for (const iface of interfaces) {
      // 判断接口是否有数据传输（入站或出站速率 > 0）
      const hasData =
        (iface.in_octets_rate && iface.in_octets_rate > 0) ||
        (iface.out_octets_rate && iface.out_octets_rate > 0)

      // 根据接口描述或MAC地址映射到目标设备
      // 这里需要根据实际业务逻辑调整
      if (hasData && iface.connected_device_id) {
        updateEdgeDataStatus(deviceId, iface.connected_device_id, hasData)
      }
    }
  }
}

// 处理客户端设备信息更新（包含网络流量数据）
const handleDeviceInfoUpdate = (data) => {
  console.log('客户端设备信息更新:', data)

  if (!data) return

  const deviceId = data.client_id || data.device_id || data.id

  // 更新设备列表中的对应数据（优化：使用 Map 查找）
  if (deviceId) {
    updateNodeStatus(deviceId, 'online')

    const device = deviceIdMap.value.get(deviceId)
    if (device) {
      Object.assign(device, data, {
        status: 'online',
        last_updated: new Date().toISOString()
      })
    } else {
      // 新设备，添加到列表
      const newDevice = {
        ...data,
        id: deviceId,
        status: 'online',
        last_updated: new Date().toISOString()
      }
      devices.value.push(newDevice)
      // 更新 Map
      updateDeviceIdMap()
    }
  }

  // 检查网络接口流量数据，更新边的动画状态
  // 注意：客户端发送的字段名是 networks，不是 network_info
  if (data.networks) {
    let interfaces = []

    // 处理两种可能的数据格式
    if (typeof data.networks === 'string') {
      // 如果是JSON字符串，先解析
      try {
        interfaces = JSON.parse(data.networks)
      } catch (e) {
        console.warn('解析 networks 字段失败:', e)
        return
      }
    } else if (Array.isArray(data.networks)) {
      // 如果已经是数组，直接使用
      interfaces = data.networks
    } else {
      return
    }

    // 优化：预先获取 graphData 和构建节点 Map
    const graphData = lf?.getGraphData()
    if (!graphData) return

    const nodeByIp = new Map()
    const nodeByDeviceId = new Map()

    for (const node of graphData.nodes) {
      const ip = node.properties?.data?.ip
      const id = node.properties?.data?.id

      if (ip) nodeByIp.set(ip, node)
      if (id) nodeByDeviceId.set(id, node)
    }

    for (const iface of interfaces) {
      // 判断接口是否有数据传输（上传或下载速率 > 0）
      const hasData =
        (iface.upload_rate && iface.upload_rate > 0) ||
        (iface.download_rate && iface.download_rate > 0)

      if (hasData && iface.gateway) {
        const gatewayNode = nodeByIp.get(iface.gateway)
        const currentDeviceNode = nodeByDeviceId.get(deviceId)

        if (gatewayNode && currentDeviceNode) {
          console.log(
            `找到节点: 当前设备节点 ${currentDeviceNode.id}, 网关节点 ${gatewayNode.id}`
          )
          updateEdgeDataStatus(currentDeviceNode.id, gatewayNode.id, hasData)
        } else {
          if (!currentDeviceNode) {
            console.warn(`未找到设备 ${deviceId} 对应的节点`)
          }
          if (!gatewayNode) {
            console.warn(`未找到网关 ${iface.gateway} 对应的节点`)
          }
        }
      }
    }
  }
}

// 初始化PubSub订阅
const initPubSubSubscriptions = () => {
  try {
    // 订阅设备状态更新
    PubSub.subscribe(wsCode.DEVICE_STATUS, handleDeviceStatusUpdate)

    // 订阅SNMP设备更新
    PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, handleSnmpDeviceUpdate)

    // 订阅客户端设备信息更新（用于网络流量动画）
    PubSub.subscribe(wsCode.DEVICE_INFO, handleDeviceInfoUpdate)

    console.log('Network.vue: PubSub订阅已初始化')
  } catch (error) {
    console.error('PubSub订阅初始化失败:', error)
  }
}

// 响应式调整拓扑图大小（优化：添加防抖）
const resizeLogicFlow = () => {
  if (!lf || !containerRef.value) return

  try {
    const container = containerRef.value
    const newWidth = container.offsetWidth
    const newHeight = container.offsetHeight

    // 获取当前尺寸
    const currentWidth = lf.graphModel.width
    const currentHeight = lf.graphModel.height

    // 如果尺寸有变化，则调整
    if (newWidth !== currentWidth || newHeight !== currentHeight) {
      console.log(
        `调整拓扑图大小: ${currentWidth}x${currentHeight} -> ${newWidth}x${newHeight}`
      )
      lf.resize(newWidth, newHeight)
    }
  } catch (error) {
    console.error('调整拓扑图大小失败:', error)
  }
}

// 防抖的 resize 函数
const debouncedResizeLogicFlow = () => {
  if (resizeDebounceTimer) {
    clearTimeout(resizeDebounceTimer)
  }
  resizeDebounceTimer = setTimeout(() => {
    resizeLogicFlow()
  }, 150)
}

// 初始化 ResizeObserver（优化：使用防抖）
const initResizeObserver = () => {
  const container = containerRef.value
  if (!container) return

  try {
    // 创建 ResizeObserver 实例
    resizeObserver = new ResizeObserver((entries) => {
      // 使用防抖优化性能
      debouncedResizeLogicFlow()
    })

    // 开始监听容器大小变化
    resizeObserver.observe(container)
    console.log('ResizeObserver 已启用')
  } catch (error) {
    console.error('ResizeObserver 初始化失败:', error)
  }
}

// 资源清理函数（优化：清理定时器）
const cleanup = () => {
  isComponentMounted.value = false

  // 清理防抖定时器
  if (resizeDebounceTimer) {
    clearTimeout(resizeDebounceTimer)
    resizeDebounceTimer = null
  }
  if (updateEdgesDebounceTimer) {
    clearTimeout(updateEdgesDebounceTimer)
    updateEdgesDebounceTimer = null
  }

  // 移除全局点击事件监听
  document.removeEventListener('click', handleClickOutside)
  PubSub.unsubscribe(wsCode.DEVICE_STATUS)
  PubSub.unsubscribe(wsCode.DEVICE_INFO)
  PubSub.unsubscribe(wsCode.SNMP_DEVICE_UPDATE)
  // 移除 ResizeObserver
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }

  // 销毀LogicFlow实例,释放内存
  if (lf) {
    try {
      lf.destroy()
    } catch (error) {
      console.warn('LogicFlow 实例销毁失败:', error)
    }
    lf = null
  }
}
// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await DeviceApi.getDevicesList()
    devices.value = response?.data || []
    // 更新 Map
    updateDeviceIdMap()
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
    // 更新 Map
    updateSwitchIdMap()
  } catch (error) {
    console.error('获取交换机列表失败:', error)
    message.error('获取交换机列表失败')
  }
}
// 生命周期
onMounted(() => {
  nextTick(() => {
    isComponentMounted.value = true

    // 初始化LogicFlow（内部会加载数据）
    initLogicFlow()

    // 初始化 ResizeObserver
    initResizeObserver()

    // 添加全屏状态监听
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('msfullscreenchange', handleFullscreenChange)

    // 注意：不在这里添加全局点击监听
    // 全局点击监听会在点击节点时动态添加
  })
})

onUnmounted(() => {
  // 移除全屏状态监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)

  // 组件销毁时清理资源
  cleanup()
})
</script>

<style lang="less">
// 页内全屏样式
.page-fullscreen {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  padding: 0 !important;
  margin: 0 !important;
  background: #f0f2f5;
}

.network {
  // 统计面板
  .stats-panel {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    gap: 24px;
    z-index: 10;

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .stat-label {
        font-size: 12px;
        color: #666;
        font-weight: 500;
      }

      .stat-value {
        font-size: 20px;
        font-weight: 600;
        color: #333;

        &.online {
          color: #52c41a;
        }

        &.offline {
          color: #ff4d4f;
        }
      }
    }
  }

  // 控制面板
  .control-panel {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    gap: 8px;
    z-index: 10;
  }

  // 边的样式
  :deep(.lf-edge) {
    path {
      transition: all 0.3s ease;
    }

    // 禁用边的选中效果
    &.lf-edge-selected {
      path {
        stroke: #afafaf !important;
        stroke-width: 2 !important;
      }
    }

    // 禁用边的悬停效果
    &:hover {
      path {
        stroke: #afafaf !important;
        stroke-width: 2 !important;
        cursor: default !important;
      }
    }
  }

  // 取消边的箭头
  :deep(.lf-edge) {
    .lf-arrow {
      display: none !important;
    }
  }

  :deep(.lf-edge-line),
  :deep(.lf-edge-polyline),
  :deep(.lf-edge-bezier) {
    marker-end: none !important;
    marker-start: none !important;
  }

  // 小球动画透明度过渡
  :deep(.edge-animation-ball) {
    transition: opacity 0.3s ease;
  }

  .lf-outline {
    .lf-outline-edge {
      display: none;
    }
  }
}
</style>
