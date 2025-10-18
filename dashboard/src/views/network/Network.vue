<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[6px] relative">
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
        <a-button @click="handleRefresh" :loading="loading">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button @click="handleCenter">
          <template #icon>
            <AimOutlined />
          </template>
          居中
        </a-button>
      </div>
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
import { LogicFlow, LineEdge, LineEdgeModel } from '@logicflow/core'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'
import { default as customNodes } from '@/common/node/index'
import TopologyApi from '@/common/api/topology'
import { wsCode } from '@/common/ws/Ws'
import { PubSub } from '@/common/utils/PubSub'
import { message } from 'ant-design-vue'
import { ReloadOutlined, AimOutlined } from '@ant-design/icons-vue'

const containerRef = useTemplateRef('containerRef')
// 使用 shallowRef 避免深度响应式带来的性能开销
let lf = null
const loading = ref(false)
const topologyData = shallowRef({ nodes: [], edges: [] })
const deviceStatusMap = ref(new Map()) // 存储设备状态 {device_id: 'online'|'offline'}
const edgeDataMap = ref(new Map()) // 存储边的数据传输状态 {edgeId: hasData}
const isComponentMounted = ref(false)

// PubSub订阅token
let deviceStatusSubscriber = null
let snmpDeviceUpdateSubscriber = null

// 插件配置移到外部常量,避免重复创建对象
const PLUGINS_OPTIONS = Object.freeze({})

// 统计信息
const stats = computed(() => {
  const totalNodes = topologyData.value.nodes.length
  const onlineNodes = Array.from(deviceStatusMap.value.values()).filter(
    (status) => status === 'online'
  ).length
  const offlineNodes = totalNodes - onlineNodes

  return {
    totalNodes,
    onlineNodes,
    offlineNodes
  }
})

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
      grid: true,
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
    customNodes.forEach((node) => {
      lf.register(node)
    })

    // 添加自定义边类型：带动画的流动边
    registerAnimatedEdge()
  } catch (error) {
    console.error('LogicFlow 初始化失败:', error)
    message.error('拓扑图初始化失败')
    return
  }

  // 渲染拓扑图
  lf.render(topologyData.value)

  // 监听边的点击事件（可用于查看详情）
  lf.on('edge:click', ({ data }) => {
    console.log('边被点击:', data)
  })

  // 加载最新的拓扑图数据并渲染
  Promise.all([loadLatestTopology()])
    .then(() => {
      // 数据加载完成后居中显示
      handleCenterView(lf)
    })
    .catch((error) => {
      console.error('初始化数据加载失败:', error)
    })
}

// 注册带动画的边
const registerAnimatedEdge = () => {
  // 自定义边的视图
  class AnimatedEdgeView extends LineEdge {
    getEdgeStyle() {
      const style = super.getEdgeStyle()
      const { properties } = this.props.model

      // 根据是否有数据传输添加动画
      if (properties?.hasData) {
        return {
          ...style,
          stroke: '#1890ff',
          strokeWidth: 3,
          strokeDasharray: '10 5',
          animation: 'lf-dash-flow 1s linear infinite'
        }
      }

      return style
    }

    getAttributes() {
      const attr = super.getAttributes()
      const { properties } = this.props.model

      if (properties?.hasData) {
        return {
          ...attr,
          className: 'animated-edge-active'
        }
      }

      return attr
    }
  }

  lf.register({
    type: 'animated-line',
    view: AnimatedEdgeView,
    model: LineEdgeModel
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
      topologyData.value = content

      // 初始化设备状态映射
      if (content.nodes && content.nodes.length > 0) {
        content.nodes.forEach((node) => {
          const deviceId = node.properties?.data?.id || node.id
          const initialStatus = node.properties?.status || 'offline'
          deviceStatusMap.value.set(deviceId, initialStatus)
        })
      }

      // 渲染拓扑图
      lf.render(content)
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

// 刷新拓扑图
const handleRefresh = async () => {
  await loadLatestTopology()
  message.success('刷新成功')
}

// 居中显示（供控制按钮调用）
const handleCenter = () => {
  handleCenterView(lf)
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
      console.log(
        `找到节点 ${deviceId}，更新状态为 ${status}，节点ID: ${node.id}`
      )
      // 更新节点属性
      const nodeModel = lf.getNodeModelById(node.id)
      if (nodeModel) {
        nodeModel.setProperties({
          ...node.properties,
          status: status
        })
        console.log(`节点 ${node.id} 状态已更新`)
      } else {
        console.warn(`无法获取节点模型: ${node.id}`)
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
      const edgeModel = lf.getEdgeModelById(edge.id)
      if (edgeModel) {
        // 更新边的属性
        const newProperties = {
          ...edge.properties,
          hasData: hasData
        }

        edgeModel.setProperties(newProperties)

        // 如果有数据，更新边的样式以显示动画
        if (hasData) {
          edgeModel.setAttributes({
            style: {
              stroke: '#1890ff',
              strokeWidth: 3
            }
          })
        } else {
          edgeModel.setAttributes({
            style: {
              stroke: '#afafaf',
              strokeWidth: 2
            }
          })
        }
      }
    }
  } catch (error) {
    console.error('更新边数据状态失败:', error)
  }
}

// 处理设备状态更新
const handleDeviceStatusUpdate = (data) => {
  console.log('设备状态更新:', data)

  if (!data) return

  // 根据实际的WebSocket数据结构调整
  // 后端推送的deviceStatus包含client_id字段
  const deviceId = data.client_id || data.device_id || data.id
  const status = data.status || (data.online ? 'online' : 'offline')

  if (deviceId) {
    updateNodeStatus(deviceId, status)
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

  // 检查接口流量数据，更新边的动画状态
  if (data.interface_info) {
    const interfaces = data.interface_info.interfaces || []

    interfaces.forEach((iface) => {
      // 判断接口是否有数据传输（入站或出站速率 > 0）
      const hasData =
        (iface.in_octets_rate && iface.in_octets_rate > 0) ||
        (iface.out_octets_rate && iface.out_octets_rate > 0)

      // 根据接口描述或MAC地址映射到目标设备
      // 这里需要根据实际业务逻辑调整
      if (hasData && iface.connected_device_id) {
        updateEdgeDataStatus(deviceId, iface.connected_device_id, hasData)
      }
    })
  }
}

// 初始化PubSub订阅
const initPubSubSubscriptions = () => {
  try {
    // 订阅设备状态更新
    deviceStatusSubscriber = PubSub.subscribe(
      wsCode.DEVICE_STATUS,
      handleDeviceStatusUpdate
    )

    // 订阅SNMP设备更新
    snmpDeviceUpdateSubscriber = PubSub.subscribe(
      wsCode.SNMP_DEVICE_UPDATE,
      handleSnmpDeviceUpdate
    )

    console.log('Network.vue: PubSub订阅已初始化')
  } catch (error) {
    console.error('PubSub订阅初始化失败:', error)
  }
}

// 资源清理函数
const cleanup = () => {
  isComponentMounted.value = false

  // 取消订阅
  if (deviceStatusSubscriber) {
    PubSub.unsubscribe(deviceStatusSubscriber)
    deviceStatusSubscriber = null
  }
  if (snmpDeviceUpdateSubscriber) {
    PubSub.unsubscribe(snmpDeviceUpdateSubscriber)
    snmpDeviceUpdateSubscriber = null
  }

  // 销毁LogicFlow实例,释放内存
  if (lf) {
    try {
      lf.destroy()
    } catch (error) {
      console.warn('LogicFlow 实例销毁失败:', error)
    }
    lf = null
  }
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    isComponentMounted.value = true

    // 初始化PubSub订阅
    initPubSubSubscriptions()

    // 初始化LogicFlow（内部会加载数据）
    initLogicFlow()
  })
})

onUnmounted(() => {
  // 组件销毁时清理资源
  cleanup()
})
</script>

<style scoped lang="less">
// 统计面板
.stats-panel {
  position: absolute;
  top: 20px;
  left: 20px;
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
  top: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  z-index: 10;
}

// 边的流动动画 - 使用 /deep/ 选择器
/deep/ .lf-edge {
  // 为有数据传输的边添加动画 class
  &.animated-edge-active {
    path {
      stroke: #1890ff !important;
      stroke-width: 3 !important;
      stroke-dasharray: 10 5 !important;
      animation: lf-dash-flow 1s linear infinite !important;
    }
  }
}

// 定义边的流动动画
@keyframes lf-dash-flow {
  from {
    stroke-dashoffset: 0;
  }
  to {
    stroke-dashoffset: -15;
  }
}

// 取消边的箭头
/deep/ .lf-edge {
  .lf-arrow {
    display: none !important;
  }
}

/deep/ .lf-edge-line,
/deep/ .lf-edge-polyline,
/deep/ .lf-edge-bezier {
  marker-end: none !important;
  marker-start: none !important;
}
</style>
