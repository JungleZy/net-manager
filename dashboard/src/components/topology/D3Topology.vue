<template>
  <div class="d3-topology-container">
    <!-- 拓扑图画布 -->
    <div ref="graphContainer" class="graph-container"></div>

    <!-- 左侧设备面板 -->
    <div v-if="showDevicePanel" class="device-panel">
      <div class="panel-header">设备列表</div>
      <div class="panel-content">
        <div
          v-for="device in availableDevices"
          :key="device.id"
          class="device-item"
          draggable="true"
          @dragstart="handleDeviceDragStart($event, device)"
          @dragend="handleDeviceDragEnd"
        >
          <div class="device-icon">{{ getDeviceIcon(device.type) }}</div>
          <div class="device-label">{{ device.label }}</div>
        </div>
        <div v-if="availableDevices.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <div class="empty-text">暂无可用设备</div>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <a-tooltip title="缩小">
        <a-button class="control-btn" @click="handleZoomOut">
          <template #icon>➖</template>
        </a-button>
      </a-tooltip>

      <a-tooltip title="放大">
        <a-button class="control-btn" @click="handleZoomIn">
          <template #icon>➕</template>
        </a-button>
      </a-tooltip>

      <a-tooltip title="适应画布">
        <a-button class="control-btn" @click="handleFitView">
          <template #icon>⊙</template>
        </a-button>
      </a-tooltip>

      <a-tooltip title="重置视图">
        <a-button class="control-btn" @click="handleResetView">
          <template #icon>↺</template>
        </a-button>
      </a-tooltip>

      <a-tooltip title="一键美化">
        <a-button class="control-btn beautify-btn" @click="handleBeautify">
          <template #icon>✨</template>
        </a-button>
      </a-tooltip>

      <a-tooltip title="删除选中">
        <a-button
          class="control-btn delete-btn"
          @click="handleDeleteSelected"
          danger
        >
          <template #icon>🗑</template>
        </a-button>
      </a-tooltip>
    </div>

    <!-- 保存按钮 -->
    <div class="save-panel">
      <a-button type="primary" @click="handleSave" :loading="isSaving">
        {{ isSaving ? '保存中...' : '保存' }}
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import D3TopologyGraph from './D3TopologyGraph'

// Props
const props = defineProps({
  devices: {
    type: Array,
    default: () => []
  },
  switches: {
    type: Array,
    default: () => []
  },
  initialData: {
    type: Object,
    default: () => ({ nodes: [], links: [] })
  },
  showDevicePanel: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['save', 'nodeClick', 'nodeDelete', 'dataChange'])

// Refs
const graphContainer = ref(null)
const isSaving = ref(false)

// 拓扑图实例
let graphInstance = null

// 可用设备列表（未添加到拓扑图的设备）
const availableDevices = ref([])

// 设备图标映射
const deviceIconMap = {
  pc: '🖥️',
  laptop: '💻',
  server: '🖧',
  router: '📡',
  switch: '🔀',
  firewall: '🛡️',
  printer: '🖨️'
}

/**
 * 初始化拓扑图
 */
const initGraph = () => {
  if (!graphContainer.value) return

  const container = graphContainer.value
  const width = container.offsetWidth || 800
  const height = container.offsetHeight || 600

  graphInstance = new D3TopologyGraph(container, {
    width,
    height,
    nodeRadius: 30,
    linkDistance: 150,
    chargeStrength: -800
  })

  // 设置事件回调
  graphInstance.on('nodeClick', (node) => {
    emit('nodeClick', node)
  })

  graphInstance.on('nodeDeleted', (nodeId) => {
    emit('nodeDelete', nodeId)
    updateAvailableDevices()
  })

  graphInstance.on('linkCreated', () => {
    emit('dataChange', graphInstance.getData())
  })

  // 加载初始数据
  if (props.initialData && props.initialData.nodes) {
    graphInstance.loadData(props.initialData)
  }

  // 监听画布拖放事件
  setupDropZone()

  // 更新可用设备列表
  updateAvailableDevices()
}

/**
 * 设置拖放区域
 */
const setupDropZone = () => {
  const container = graphContainer.value
  if (!container) return

  container.addEventListener('dragover', (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  })

  container.addEventListener('drop', (e) => {
    e.preventDefault()
    handleDeviceDrop(e)
  })
}

/**
 * 更新可用设备列表
 */
const updateAvailableDevices = () => {
  if (!graphInstance) return

  const existingNodeIds = new Set()
  const data = graphInstance.getData()

  data.nodes.forEach((node) => {
    if (node.properties && node.properties.deviceId) {
      existingNodeIds.add(node.properties.deviceId)
    }
  })

  const devices = []

  // 添加未使用的设备
  props.devices.forEach((device) => {
    if (!existingNodeIds.has(device.client_id)) {
      devices.push({
        id: device.client_id,
        label: device.hostname || device.ip_address || '未知设备',
        type: getDeviceType(device.type),
        properties: {
          deviceId: device.client_id,
          data: device
        }
      })
    }
  })

  // 添加未使用的交换机
  props.switches.forEach((switchItem) => {
    if (!existingNodeIds.has(switchItem.id)) {
      devices.push({
        id: switchItem.id,
        label: switchItem.device_name || switchItem.description || '未知交换机',
        type: 'switch',
        properties: {
          deviceId: switchItem.id,
          data: switchItem
        }
      })
    }
  })

  availableDevices.value = devices
}

/**
 * 获取设备类型
 */
const getDeviceType = (type) => {
  const typeMap = {
    台式机: 'pc',
    笔记本: 'laptop',
    服务器: 'server',
    路由器: 'router',
    交换机: 'switch',
    防火墙: 'firewall',
    打印机: 'printer'
  }
  return typeMap[type] || 'pc'
}

/**
 * 获取设备图标
 */
const getDeviceIcon = (type) => {
  return deviceIconMap[type] || '⚙️'
}

/**
 * 处理设备拖拽开始
 */
const handleDeviceDragStart = (event, device) => {
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('device', JSON.stringify(device))
}

/**
 * 处理设备拖拽结束
 */
const handleDeviceDragEnd = (event) => {
  // 可以在这里添加拖拽结束的视觉反馈
}

/**
 * 处理设备放置
 */
const handleDeviceDrop = (event) => {
  try {
    const deviceData = event.dataTransfer.getData('device')
    if (!deviceData) return

    const device = JSON.parse(deviceData)

    // 获取放置位置（需要考虑缩放和平移变换）
    if (!graphInstance) return

    // 获取鼠标在SVG容器中的位置
    const svg = graphInstance.svg.node()
    const pt = svg.createSVGPoint()
    pt.x = event.clientX
    pt.y = event.clientY

    // 获取当前的缩放和平移变换矩阵
    const g = graphInstance.g.node()
    const ctm = g.getScreenCTM()

    // 将屏幕坐标转换为SVG坐标系中的坐标
    const transformedPt = pt.matrixTransform(ctm.inverse())
    const x = transformedPt.x
    const y = transformedPt.y

    // 添加节点到图中
    const node = {
      id: device.id,
      type: device.type,
      label: device.label,
      x,
      y,
      status: 'online',
      properties: device.properties
    }

    graphInstance.addNode(node)
    updateAvailableDevices()
    emit('dataChange', graphInstance.getData())

    message.success(`已添加设备: ${device.label}`)
  } catch (error) {
    console.error('添加设备失败:', error)
    message.error('添加设备失败')
  }
}

/**
 * 缩小
 */
const handleZoomOut = () => {
  if (!graphInstance) return
  graphInstance.zoomTo(0.8)
}

/**
 * 放大
 */
const handleZoomIn = () => {
  if (!graphInstance) return
  graphInstance.zoomTo(1.2)
}

/**
 * 适应画布
 */
const handleFitView = () => {
  if (!graphInstance) return
  graphInstance.fitView()
}

/**
 * 重置视图
 */
const handleResetView = () => {
  if (!graphInstance) return
  graphInstance.resetZoom()
}

/**
 * 一键美化
 */
const handleBeautify = () => {
  if (!graphInstance) return

  const hideLoading = message.loading('正在优化布局...', 0)

  try {
    const result = graphInstance.beautify()

    setTimeout(() => {
      hideLoading()
      graphInstance.fitView()

      const nodeCount = graphInstance.nodes.length
      const linkCount = graphInstance.links.length
      message.success(`布局完成！节点: ${nodeCount} | 连线: ${linkCount}`, 3)
    }, 500)

    emit('dataChange', graphInstance.getData())
  } catch (error) {
    hideLoading()
    console.error('美化失败:', error)
    message.error('布局优化失败')
  }
}

/**
 * 删除选中节点
 */
const handleDeleteSelected = () => {
  if (!graphInstance || !graphInstance.selectedNode) {
    message.warning('请先选择要删除的节点')
    return
  }

  const node = graphInstance.selectedNode
  graphInstance.deleteNode(node.id)
  message.success('已删除节点')
  emit('dataChange', graphInstance.getData())
}

/**
 * 保存拓扑图
 */
const handleSave = () => {
  if (!graphInstance) return

  const data = graphInstance.getData()
  emit('save', data)
}

/**
 * 监听设备列表变化
 */
watch(
  () => [props.devices, props.switches],
  () => {
    updateAvailableDevices()
  },
  { deep: true }
)

/**
 * 监听初始数据变化
 */
watch(
  () => props.initialData,
  (newData) => {
    if (graphInstance && newData) {
      graphInstance.loadData(newData)
      updateAvailableDevices()
    }
  },
  { deep: true }
)

onMounted(() => {
  nextTick(() => {
    initGraph()
  })
})

onUnmounted(() => {
  if (graphInstance) {
    graphInstance.destroy()
    graphInstance = null
  }
})

// 导出方法供父组件使用
defineExpose({
  getData: () => graphInstance?.getData(),
  fitView: () => graphInstance?.fitView(),
  beautify: () => handleBeautify(),
  resetZoom: () => graphInstance?.resetZoom()
})
</script>

<style lang="less" scoped>
.d3-topology-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: transparent;
  border-radius: 8px;
  overflow: hidden;
  // 禁止文本选择，防止拖拽时选中文本
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;

  .graph-container {
    width: 100%;
    height: 100%;

    // 节点样式
    :deep(.node) {
      cursor: move;
      // 禁止文本选择
      user-select: none;

      // 选中边框默认隐藏
      .node-selection-border {
        display: none;
        transition: all 0.2s ease;
      }

      // 选中状态显示边框
      &.selected {
        .node-selection-border {
          display: block !important;
          stroke: #91d5ff; // 浅蓝色
          stroke-width: 2;
        }
      }
    }

    // 锚点样式
    :deep(.anchor) {
      // 禁止文本选择
      user-select: none;
      .anchor-circle {
        transition: opacity 0.2s, r 0.2s;
      }

      &:hover .anchor-circle {
        r: 5;
        opacity: 1 !important;
      }
    }

    // 连线样式
    :deep(.link) {
      stroke: #afafaf;
      stroke-width: 2;
      fill: none;
      transition: stroke 0.2s;

      &:hover {
        stroke: #1890ff;
        stroke-width: 3;
      }
    }

    // 拖拽线样式
    :deep(.drag-line) {
      pointer-events: none;
      stroke: #1890ff;
      stroke-width: 2;
      stroke-dasharray: 5, 5;
      animation: dash 0.5s linear infinite;
      // 禁止文本选择
      user-select: none;
    }

    @keyframes dash {
      to {
        stroke-dashoffset: -10;
      }
    }
  }

  .device-panel {
    position: absolute;
    left: 8px;
    top: 8px;
    bottom: 8px;
    width: 120px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;

    .panel-header {
      padding: 12px;
      font-weight: 600;
      font-size: 14px;
      border-bottom: 1px solid #f0f0f0;
      color: #333;
    }

    .panel-content {
      flex: 1;
      overflow-y: auto;
      padding: 8px;

      .device-item {
        padding: 10px 8px;
        margin-bottom: 6px;
        background: #fafafa;
        border: 1px solid #e8e8e8;
        border-radius: 4px;
        cursor: move;
        transition: all 0.3s;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;

        &:hover {
          background: #e6f7ff;
          border-color: #1890ff;
          transform: translateY(-2px);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .device-icon {
          font-size: 24px;
        }

        .device-label {
          font-size: 11px;
          text-align: center;
          color: #666;
          word-break: break-all;
          line-height: 1.2;
        }
      }

      .empty-state {
        text-align: center;
        padding: 30px 10px;
        color: #999;

        .empty-icon {
          font-size: 32px;
          margin-bottom: 8px;
        }

        .empty-text {
          font-size: 12px;
        }
      }
    }
  }

  .control-panel {
    position: absolute;
    right: 12px;
    top: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;

    .help-badge {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 50%;
      font-size: 18px;
      cursor: help;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
      animation: pulse 2s infinite;

      &:hover {
        transform: scale(1.1);
      }
    }

    @keyframes pulse {
      0%,
      100% {
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
      }
      50% {
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.6);
      }
    }

    .control-btn {
      width: 36px;
      height: 36px;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      background: white;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
      }

      &.beautify-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;

        &:hover {
          opacity: 0.9;
        }
      }

      &.delete-btn:hover {
        transform: scale(1.05);
      }
    }
  }

  .save-panel {
    position: absolute;
    right: 20px;
    bottom: 20px;
  }
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>
