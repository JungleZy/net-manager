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

      <!-- 调试面板 -->
      <div v-if="showDebugPanel" class="debug-panel">
        <div class="debug-panel-header">
          <span class="debug-panel-title">🔧 拓扑调试面板</span>
          <span class="debug-panel-close" @click="toggleDebugPanel">×</span>
        </div>
        <div class="debug-panel-content">
          <div class="debug-section">
            <h4 class="debug-section-title">生成测试拓扑</h4>
            <div class="debug-buttons">
              <button
                class="debug-btn debug-btn-micro"
                @click="generateTestTopology('micro')"
                :disabled="isGenerating"
              >
                <span class="debug-btn-icon">🏠</span>
                <span class="debug-btn-text">微型</span>
                <span class="debug-btn-desc">20设备/2交换机</span>
              </button>
              <button
                class="debug-btn debug-btn-standard"
                @click="generateTestTopology('standard')"
                :disabled="isGenerating"
              >
                <span class="debug-btn-icon">🏢</span>
                <span class="debug-btn-text">标准</span>
                <span class="debug-btn-desc">100设备/5交换机</span>
              </button>
              <button
                class="debug-btn debug-btn-large"
                @click="generateTestTopology('large')"
                :disabled="isGenerating"
              >
                <span class="debug-btn-icon">🏭</span>
                <span class="debug-btn-text">大型</span>
                <span class="debug-btn-desc">500设备/10交换机</span>
              </button>
              <button
                class="debug-btn debug-btn-huge"
                @click="generateTestTopology('huge')"
                :disabled="isGenerating"
              >
                <span class="debug-btn-icon">🌐</span>
                <span class="debug-btn-text">巨型</span>
                <span class="debug-btn-desc">1000设备/50交换机</span>
              </button>
            </div>
          </div>
          <div v-if="topologyStats" class="debug-section">
            <h4 class="debug-section-title">当前拓扑统计</h4>
            <div class="debug-stats">
              <div class="debug-stat-item">
                <span class="debug-stat-label">总节点:</span>
                <span class="debug-stat-value">{{
                  topologyStats.totalNodes
                }}</span>
              </div>
              <div class="debug-stat-item">
                <span class="debug-stat-label">总连线:</span>
                <span class="debug-stat-value">{{
                  topologyStats.totalEdges
                }}</span>
              </div>
              <div class="debug-stat-item">
                <span class="debug-stat-label">交换机:</span>
                <span class="debug-stat-value">{{
                  topologyStats.switches
                }}</span>
              </div>
              <div class="debug-stat-item">
                <span class="debug-stat-label">设备:</span>
                <span class="debug-stat-value">{{
                  topologyStats.devices
                }}</span>
              </div>
              <div class="debug-stat-item">
                <span class="debug-stat-label">在线:</span>
                <span class="debug-stat-value success">{{
                  topologyStats.online
                }}</span>
              </div>
              <div class="debug-stat-item">
                <span class="debug-stat-label">离线:</span>
                <span class="debug-stat-value error">{{
                  topologyStats.offline
                }}</span>
              </div>
            </div>
          </div>
          <div class="debug-section">
            <button
              class="debug-btn-clear"
              @click="clearTopology"
              :disabled="isGenerating"
            >
              🗑️ 清空拓扑
            </button>
          </div>
        </div>
        <div class="debug-panel-footer">
          <span class="debug-hint">提示: 按 Ctrl+Shift+K 关闭面板</span>
        </div>
      </div>

      <!-- 分组编辑模态框 -->
      <a-modal
        v-model:open="showGroupEditModal"
        title="编辑分组"
        :width="500"
        centered
        @ok="handleGroupEditConfirm"
        @cancel="handleGroupEditCancel"
      >
        <div class="group-edit-form">
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">分组名称：</label>
            <a-input
              style="width: calc(100% - 70px)"
              v-model:value="groupEditForm.name"
              placeholder="请输入分组名称"
            />
          </div>
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">背景颜色：</label>
            <div class="color-picker-wrapper">
              <input
                type="color"
                v-model="groupEditForm.fillColor"
                class="color-input"
              />
            </div>
          </div>
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">背景透明：</label>
            <a-slider
              v-model:value="groupEditForm.fillOpacity"
              :min="0"
              :max="1"
              :step="0.1"
              :marks="{ 0: '0', 0.5: '0.5', 1: '1' }"
              style="margin: 0 0 12px 0; width: calc(100% - 100px)"
            />
          </div>
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">边框颜色：</label>
            <div class="color-picker-wrapper">
              <input
                type="color"
                v-model="groupEditForm.strokeColor"
                class="color-input"
              />
            </div>
          </div>
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">边框宽度：</label>
            <a-input-number
              size="small"
              v-model:value="groupEditForm.strokeWidth"
              :min="1"
              :max="10"
            />
          </div>
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">边框样式：</label>
            <a-radio-group v-model:value="groupEditForm.strokeDasharray">
              <a-radio value="">实线</a-radio>
              <a-radio value="5,5">虚线</a-radio>
              <a-radio value="2,2">点线</a-radio>
            </a-radio-group>
          </div>
          <div class="form-item layout-left-center">
            <label class="form-label">限制移动：</label>
            <a-switch v-model:checked="groupEditForm.isRestrict" />
            <span class="form-hint">开启后，子节点不能移出分组范围</span>
          </div>
        </div>
      </a-modal>

      <!-- 节点属性模态框 -->
      <a-modal
        v-model:open="showNodePropsModal"
        title="节点属性"
        :width="420"
        centered
        @ok="handleNodePropsConfirm"
        @cancel="handleNodePropsCancel"
      >
        <div class="group-edit-form">
          <div class="form-item layout-left-center mb-[12px]">
            <label class="form-label">是否虚拟节点：</label>
            <a-switch v-model:checked="nodePropsForm.isVirtual" />
            <span class="form-hint"
              >虚拟节点用于占位或说明，当设为虚拟节点后，该节点会一直保持在线状态</span
            >
          </div>
        </div>
      </a-modal>

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
  shallowRef,
  computed
} from 'vue'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'
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
import Printer from '@/assets/printer.png'
import Text from '@/assets/text.png'
import { deriveDeviceName, handleCenterView } from '@/common/utils/Utils.js'
import {
  generateTopologyByScale,
  getTopologyStats
} from '@/utils/topologyTestDataGenerator.js'

const containerRef = useTemplateRef('container')
// 使用 shallowRef 避免深度响应式带来的性能开销
let lf = null
const devices = shallowRef([])
const switches = shallowRef([])
const currentTopologyId = ref(null)
const isSaving = ref(false)
const leftMenus = shallowRef([])
const isComponentMounted = ref(false)

// 调试面板相关状态
const showDebugPanel = ref(false)
const isGenerating = ref(false)

// 分组编辑模态框相关状态
const showGroupEditModal = ref(false)
const currentEditingGroupId = ref(null)
const groupEditForm = ref({
  name: '',
  fillColor: '#F4F5F6',
  fillOpacity: 0.3,
  strokeColor: '#CECECE',
  strokeWidth: 2,
  strokeDasharray: '', // 空字符串表示实线，'5,5'表示虚线
  isRestrict: false // 是否限制子节点移动到分组外
})

// 计算拓扑统计信息
const topologyStats = computed(() => {
  if (!lf) return null
  try {
    const graphData = lf.getGraphData()
    return getTopologyStats(graphData)
  } catch (error) {
    return null
  }
})
// 节点属性模态框相关状态
const showNodePropsModal = ref(false)
const currentEditingNodeId = ref(null)
const nodePropsForm = ref({
  isVirtual: false
})
// 设备类型映射 - 移到外部作为常量,避免重复创建
const DEVICE_TYPE_MAP = Object.freeze({
  台式机: { icon: Pc, type: 'pc' },
  笔记本: { icon: Laptop, type: 'laptop' },
  服务器: { icon: Server, type: 'server' },
  路由器: { icon: Router, type: 'router' },
  交换机: { icon: Switches, type: 'switch' },
  防火墙: { icon: Firewall, type: 'firewall' },
  打印机: { icon: Printer, type: 'printer' },
  文本标签: { icon: Text, type: 'textLabel' }
})

// 锚点索引常量
const ANCHOR = Object.freeze({
  TOP: 0,
  RIGHT: 1,
  BOTTOM: 2,
  LEFT: 3
})

let data = {}

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
  document.removeEventListener('keydown', handleCtrlKeyDown)
  document.removeEventListener('keyup', handleCtrlKeyUp)
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
  label: {
    isMultiple: true,
    textOverflowMode: 'ellipsis'
  }
})

const initTopology = async () => {
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
    // 动态导入 LogicFlow 核心库
    const LogicFlowModule = await import(
      /* webpackChunkName: "logicflow-core" */
      '@logicflow/core'
    )
    const LogicFlow = LogicFlowModule.default || LogicFlowModule.LogicFlow

    // 动态导入 LogicFlow 扩展
    const ExtensionModule = await import(
      /* webpackChunkName: "logicflow-extensions" */
      '@logicflow/extension'
    )
    const { Control, DndPanel, SelectionSelect, Group } = ExtensionModule

    // 动态导入布局库
    const LayoutModule = await import(
      /* webpackChunkName: "logicflow-layout" */
      '@logicflow/layout'
    )
    const { Dagre } = LayoutModule

    // 动态导入自定义节点
    const CustomHtmlModule = await import(
      /* webpackChunkName: "logicflow-node" */
      '@/common/node/HtmlNode'
    )
    const CustomHtml = CustomHtmlModule.default || CustomHtmlModule

    // 动态导入自定义节点注册模块
    const CustomNodesModule = await import(
      /* webpackChunkName: "logicflow-nodes" */
      '@/common/node/index'
    )
    const customNodes = CustomNodesModule.default || CustomNodesModule

    lf = new LogicFlow({
      grid: true,
      container: container,
      width: width,
      height: height,
      keyboard: {
        enabled: true
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
      plugins: [Group, Control, DndPanel, SelectionSelect, Dagre],
      multipleSelectKey: 'shift',
      disabledTools: ['multipleSelect'],
      pluginsOptions: PLUGINS_OPTIONS,
      adjustEdgeStartAndEnd: true,
      // 性能优化配置
      stopScrollGraph: true,
      stopZoomGraph: false,
      snapToGrid: true,
      partial: true, // 启用局部渲染
      // 禁用双击节点编辑文本
      nodeTextEdit: true,
      edgeTextEdit: true
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

  // 添加创建分组按钮
  lf.extension.control.addItem({
    key: 'createGroup',
    iconClass: 'lf-control-create-group',
    title: '创建分组',
    text: '分组',
    onClick: (lf) => {
      handleCreateGroup(lf)
    }
  })

  lf.render(data)

  // 添加键盘Delete键监听和Ctrl键框选监听
  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('keydown', handleCtrlKeyDown)
  document.addEventListener('keyup', handleCtrlKeyUp)

  // 监听节点拖拽添加事件，添加后从leftMenus中移除
  lf.on('node:dnd-add', (nodeData) => {
    console.log(nodeData)

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

  // 监听分组创建事件，为新分组添加名称
  lf.on('node-selection:group-create', ({ groupData }) => {
    try {
      console.log('分组创建事件:', groupData)
      if (groupData && groupData.id) {
        // 为分组添加默认名称
        const groupModel = lf.getNodeModelById(groupData.id)
        if (groupModel) {
          groupModel.updateText({
            value: '新建分组',
            editable: true,
            draggable: false
          })
        }
      }
    } catch (error) {
      console.warn('处理分组创建事件失败:', error)
    }
  })

  // 监听节点右键点击事件，处理分组编辑
  lf.on('node:contextmenu', ({ data, e }) => {
    try {
      // 只处理customGroup类型的节点
      if (data && data.type === 'customGroup') {
        e.preventDefault() // 阻止默认右键菜单
        handleGroupRightClick(data)
        return
      }

      // 其余普通节点右键，打开节点属性编辑
      if (data && data.id) {
        e.preventDefault()
        handleNodeRightClick(data)
        return
      }
    } catch (error) {
      console.warn('处理节点右键事件失败:', error)
    }
  })

  // 获取设备和交换机数据并设置拖拽面板项
  Promise.all([fetchDevices(), fetchSwitches()])
    .then(() => {
      // 设备和交换机数据加载完成后，再加载拓扑图数据
      loadLatestTopology()
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
    // 动态导入拓扑图API
    const TopologyApiModule = await import(
      /* webpackChunkName: "topology-api" */
      '@/common/api/topology'
    )
    const TopologyApi = TopologyApiModule.default || TopologyApiModule

    const response = await TopologyApi.getLatestTopology()
    if (response?.data?.content) {
      const topologyData = response.data.content
      currentTopologyId.value = response.data.id

      // 更新节点文本以反映最新的别名
      if (topologyData.nodes && devices.value && switches.value) {
        // 创建设备映射，便于快速查找
        const deviceMap = {}
        for (let i = 0, len = devices.value.length; i < len; i++) {
          const device = devices.value[i]
          deviceMap[device.client_id] = device
        }

        // 创建交换机映射，便于快速查找
        const switchMap = {}
        for (let i = 0, len = switches.value.length; i < len; i++) {
          const switchItem = switches.value[i]
          switchMap[switchItem.id] = switchItem
        }

        // 更新节点文本
        for (let i = 0, len = topologyData.nodes.length; i < len; i++) {
          const node = topologyData.nodes[i]
          const dataId = node?.properties?.data?.id

          if (dataId) {
            // 检查是否是设备节点
            const device = deviceMap[dataId]
            if (device) {
              // 优先使用alias，如果没有则使用hostname或ip_address
              const displayName =
                device.alias ||
                device.hostname ||
                device.ip_address ||
                '未知设备'
              if (node.text) {
                node.text.value = displayName
              } else {
                node.text = { value: displayName }
              }
              continue
            }

            // 检查是否是交换机节点
            const switchItem = switchMap[dataId]
            if (switchItem) {
              // 优先使用alias，如果没有则使用device_name或从描述推导设备名称
              const deviceName =
                switchItem.alias ||
                switchItem.device_name ||
                deriveDeviceName(switchItem.description) ||
                '未知交换机'
              if (node.text) {
                node.text.value = deviceName
              } else {
                node.text = { value: deviceName }
              }
            }
          }
        }
      }

      data = topologyData
      lf.render(data)
    } else {
      // 没有保存的拓扑图,使用默认数据
      lf.render(data)
    }
    handleCenterView(lf)

    // 更新左侧菜单，确保已添加到拓扑图的设备不会重复显示
    updateLeftMenus()
  } catch (error) {
    // 如果是404错误(没有拓扑图),使用默认数据
    if (error?.response?.status === 404) {
      lf.render(data)
    } else {
      console.error('加载拓扑图失败:', error)
      message.error('加载拓扑图失败')
      lf.render(data)
    }
    handleCenterView(lf)

    // 更新左侧菜单，确保已添加到拓扑图的设备不会重复显示
    updateLeftMenus()
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
    return Promise.resolve()
  } catch (error) {
    console.error('获取设备列表失败:', error)
    message.error('获取设备列表失败')
    return Promise.reject(error)
  }
}

// 获取交换机列表
const fetchSwitches = async () => {
  try {
    const response = await SwitchApi.getSwitchesList()
    switches.value = response?.data || []
    updateLeftMenus()
    return Promise.resolve()
  } catch (error) {
    console.error('获取交换机列表失败:', error)
    message.error('获取交换机列表失败')
    return Promise.reject(error)
  }
}

/**
 * 格式化图数据，将所有坐标保留2位小数
 * 优化: 使用传统循环和减少函数调用
 */
const formatGraphData = (graphData) => {
  if (!graphData) return graphData

  // 优化：提取 toFixed 逻辑为内联函数，减少重复代码
  const format2 = (num) => Number(num.toFixed(2))

  // 格式化节点坐标
  const nodes = graphData.nodes
  if (nodes?.length > 0) {
    for (let i = 0, len = nodes.length; i < len; i++) {
      const node = nodes[i]

      // 移除 customGroup 的 nodeSize 属性
      if (node.type === 'customGroup') {
        delete node.properties?.nodeSize
      }

      // 格式化节点坐标
      if (typeof node.x === 'number') {
        node.x = format2(node.x)
      }
      if (typeof node.y === 'number') {
        node.y = format2(node.y)
      }

      // 格式化文本坐标
      const text = node.text
      if (text && typeof text === 'object') {
        if (typeof text.x === 'number') {
          text.x = format2(text.x)
        }
        if (typeof text.y === 'number') {
          text.y = format2(text.y)
        }
      }
    }
  }

  // 格式化边的坐标点
  const edges = graphData.edges
  if (edges?.length > 0) {
    for (let i = 0, len = edges.length; i < len; i++) {
      const edge = edges[i]

      // 格式化起点
      const startPoint = edge.startPoint
      if (startPoint) {
        if (typeof startPoint.x === 'number') {
          startPoint.x = format2(startPoint.x)
        }
        if (typeof startPoint.y === 'number') {
          startPoint.y = format2(startPoint.y)
        }
      }

      // 格式化终点
      const endPoint = edge.endPoint
      if (endPoint) {
        if (typeof endPoint.x === 'number') {
          endPoint.x = format2(endPoint.x)
        }
        if (typeof endPoint.y === 'number') {
          endPoint.y = format2(endPoint.y)
        }
      }

      // 格式化路径点列表
      const pointsList = edge.pointsList
      if (pointsList?.length > 0) {
        for (let j = 0, pLen = pointsList.length; j < pLen; j++) {
          const point = pointsList[j]
          if (typeof point.x === 'number') {
            point.x = format2(point.x)
          }
          if (typeof point.y === 'number') {
            point.y = format2(point.y)
          }
        }
      }
    }
  }

  return graphData
}

// 一键美化功能
const handleBeautifyAction = (lfInstance) => {
  lf.extension.dagre.layout({
    rankdir: 'TB', // 从上到下的布局方向
    align: '', // 上左对齐
    ranker: 'network-simplex'
  })
  lf.fitView()
}

// 创建分组功能
// 分组默认配置常量（冻结以防止运行时修改）
const GROUP_DEFAULT_CONFIG = Object.freeze({
  PADDING: 30, // 分组边距
  DEFAULT_NODE_SIZE: 60, // 默认节点尺寸
  FILL_COLOR: '#cccccc', // 默认填充色
  FILL_OPACITY: 0.3, // 默认透明度
  STROKE_COLOR: '#2196F3', // 默认边框色
  STROKE_WIDTH: 2, // 默认边框宽度
  DEFAULT_NAME: '新建分组', // 默认名称
  MIN_NODES: 2 // 最小节点数
})

const handleCreateGroup = (lfInstance) => {
  if (!lfInstance) {
    console.warn('创建分组: LogicFlow 实例不存在')
    return
  }

  try {
    // 获取选中的节点
    const selectElements = lfInstance.getSelectElements(true)
    const selectedNodes = selectElements?.nodes

    // 提前返回：检查节点数量
    if (
      !selectedNodes ||
      selectedNodes.length < GROUP_DEFAULT_CONFIG.MIN_NODES
    ) {
      message.warning('请至少选择2个节点来创建分组')
      return
    }

    // 优化：一次遍历完成过滤和边界计算，减少数组操作
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity
    const normalNodes = []
    const childrenIds = []

    for (let i = 0, len = selectedNodes.length; i < len; i++) {
      const node = selectedNodes[i]

      // 过滤掉group类型的节点，避免嵌套分组
      if (node.type === 'group') {
        continue
      }

      normalNodes.push(node)
      childrenIds.push(node.id)

      // 同时计算边界（避免二次遍历）
      const nodeWidth =
        node.properties?.width || GROUP_DEFAULT_CONFIG.DEFAULT_NODE_SIZE
      const nodeHeight =
        node.properties?.height || GROUP_DEFAULT_CONFIG.DEFAULT_NODE_SIZE
      const halfWidth = nodeWidth / 2
      const halfHeight = nodeHeight / 2

      const nodeLeft = node.x - halfWidth
      const nodeRight = node.x + halfWidth
      const nodeTop = node.y - halfHeight
      const nodeBottom = node.y + halfHeight

      // 使用条件判断代替 Math.min/max，减少函数调用开销
      if (nodeLeft < minX) minX = nodeLeft
      if (nodeRight > maxX) maxX = nodeRight
      if (nodeTop < minY) minY = nodeTop
      if (nodeBottom > maxY) maxY = nodeBottom
    }

    // 提前返回：检查有效节点数量
    if (normalNodes.length < GROUP_DEFAULT_CONFIG.MIN_NODES) {
      message.warning('请选择至少两个非分组节点')
      return
    }

    // 计算分组中心点和尺寸
    const padding2 = GROUP_DEFAULT_CONFIG.PADDING * 2
    const groupX = (minX + maxX) / 2
    const groupY = (minY + maxY) / 2
    const groupWidth = maxX - minX + padding2
    const groupHeight = maxY - minY + padding2

    // 创建分组节点（直接使用已收集的 childrenIds，避免 map 操作）
    lfInstance.addNode({
      type: 'customGroup',
      x: groupX,
      y: groupY,
      width: groupWidth,
      height: groupHeight,
      properties: {
        fillColor: GROUP_DEFAULT_CONFIG.FILL_COLOR,
        fillOpacity: GROUP_DEFAULT_CONFIG.FILL_OPACITY,
        strokeColor: GROUP_DEFAULT_CONFIG.STROKE_COLOR,
        strokeWidth: GROUP_DEFAULT_CONFIG.STROKE_WIDTH,
        isRestrict: true // 默认不限制子节点移动
      },
      text: {
        value: GROUP_DEFAULT_CONFIG.DEFAULT_NAME
      },
      children: childrenIds
    })

    // 清除选中状态
    lfInstance.clearSelectElements()

    message.success('分组创建成功')
  } catch (error) {
    console.error('创建分组失败:', error)
    message.error('创建分组失败')
  }
}

// 更新左侧菜单项 - 优化性能
const updateLeftMenus = () => {
  // 优化：使用 Set 快速查找已存在的节点
  const existingNodeIds = new Set()
  if (lf) {
    try {
      const graphData = lf.getGraphData()
      const nodes = graphData?.nodes
      if (nodes?.length > 0) {
        for (let i = 0, len = nodes.length; i < len; i++) {
          const dataId = nodes[i]?.properties?.data?.id
          if (dataId) {
            existingNodeIds.add(dataId)
          }
        }
      }
    } catch (error) {
      console.warn('获取拓扑图节点失败:', error)
    }
  }

  const newMenus = []
  newMenus.length = 0 // 确保从空开始

  // 顶部添加可多次拖入的纯文本节点
  newMenus.push({
    type: 'text',
    label: '文本标签',
    text: '默认文本标签',
    properties: {
      textStyle: { fontSize: 14 }
    },
    icon: Text
  })

  // 添加设备项（过滤已在拓扑图中的设备）
  const devicesArray = devices.value
  for (let i = 0, len = devicesArray.length; i < len; i++) {
    const device = devicesArray[i]

    // 跳过已存在的设备
    if (existingNodeIds.has(device.client_id)) {
      continue
    }

    const deviceType = device.type || '未知设备'
    const typeConfig = DEVICE_TYPE_MAP[deviceType] || { icon: Pc, type: 'pc' }
    // 优先使用alias，如果没有则使用hostname或ip_address
    const displayName =
      device.alias || device.hostname || device.ip_address || '未知设备'

    newMenus.push({
      type: typeConfig.type,
      label: displayName,
      text: displayName,
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

  // 添加交换机项（过滤已在拓扑图中的交换机）
  const switchesArray = switches.value
  for (let i = 0, len = switchesArray.length; i < len; i++) {
    const switchItem = switchesArray[i]

    // 跳过已存在的交换机
    if (existingNodeIds.has(switchItem.id)) {
      continue
    }

    // 优先使用alias，如果没有则使用device_name或从描述推导设备名称
    const deviceName =
      switchItem.alias ||
      switchItem.device_name ||
      deriveDeviceName(switchItem.description) ||
      '未知交换机'
    const deviceType = switchItem.device_type || '未知设备'
    const typeConfig = DEVICE_TYPE_MAP[deviceType] || {
      icon: Switches,
      type: 'switch'
    }

    newMenus.push({
      type: typeConfig.type,
      label: deviceName,
      text: deviceName,
      properties: {
        width: 60,
        height: 60,
        data: {
          id: switchItem.id
        }
      },
      icon: typeConfig.icon
    })
  }

  // 更新 leftMenus
  leftMenus.value = newMenus
  if (lf?.extension?.dndPanel) {
    lf.extension.dndPanel.setPatternItems(newMenus)
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
 * 优化：减少重复遍历
 * @param {Object} selectElements - 选中的元素
 * @returns {boolean} 是否成功删除
 */
const deleteSelectedElements = (selectElements) => {
  const nodes = selectElements.nodes
  const edges = selectElements.edges
  const nodesCount = nodes?.length || 0
  const edgesCount = edges?.length || 0

  if (nodesCount === 0 && edgesCount === 0) {
    return false
  }

  // 优化：批量删除节点
  if (nodesCount > 0) {
    for (let i = 0; i < nodesCount; i++) {
      lf.deleteNode(nodes[i].id)
    }
    message.success(`已删除 ${nodesCount} 个节点`)
  }

  // 优化：批量删除边
  if (edgesCount > 0) {
    for (let i = 0; i < edgesCount; i++) {
      lf.deleteEdge(edges[i].id)
    }
    message.success(`已删除 ${edgesCount} 条边`)
  }

  return true
}

/**
 * 切换调试面板显示状态
 */
const toggleDebugPanel = () => {
  showDebugPanel.value = !showDebugPanel.value
  if (showDebugPanel.value) {
    message.info('调试面板已打开', 1)
  }
}

/**
 * 生成测试拓扑数据
 * @param {string} scale - 规模类型: 'micro' | 'standard' | 'large' | 'huge'
 */
const generateTestTopology = async (scale) => {
  if (!lf) {
    message.error('拓扑图未初始化')
    return
  }

  if (isGenerating.value) {
    return
  }

  const scaleNames = {
    micro: '微型',
    standard: '标准',
    large: '大型',
    huge: '巨型'
  }

  const scaleName = scaleNames[scale] || scale

  try {
    isGenerating.value = true
    const hideLoading = message.loading(`正在生成${scaleName}拓扑数据...`, 0)

    // 异步生成数据以避免阻塞UI
    await nextTick()

    const startTime = performance.now()
    const testData = generateTopologyByScale(scale)
    const endTime = performance.now()
    const duration = ((endTime - startTime) / 1000).toFixed(2)

    // 渲染数据
    lf.render(testData)

    // 等待渲染完成后居中显示
    await nextTick()
    handleCenterView(lf)

    hideLoading()

    const stats = getTopologyStats(testData)
    message.success(
      `${scaleName}拓扑生成成功！节点: ${stats.totalNodes} | 连线: ${stats.totalEdges} | 耗时: ${duration}秒`,
      4
    )
  } catch (error) {
    console.error('生成测试拓扑失败:', error)
    message.error('生成拓扑数据失败: ' + error.message)
  } finally {
    isGenerating.value = false
  }
}

/**
 * 清空拓扑图
 */
const clearTopology = () => {
  if (!lf) {
    message.error('拓扑图未初始化')
    return
  }

  try {
    const graphData = lf.getGraphData()
    const nodeCount = graphData?.nodes?.length || 0

    if (nodeCount === 0) {
      message.info('拓扑图已经是空的')
      return
    }

    lf.render({ nodes: [], edges: [] })
    message.success(`已清空拓扑图 (${nodeCount} 个节点)`)
  } catch (error) {
    console.error('清空拓扑失败:', error)
    message.error('清空拓扑失败')
  }
}

// 处理Ctrl键按下触发框选
const handleCtrlKeyDown = (event) => {
  // 检查组件是否已挂载和LogicFlow实例是否存在
  if (!isComponentMounted.value || !lf) {
    return false
  }

  // 防止在输入框等元素中触发操作
  if (isEditableElement(event.target)) {
    return false
  }

  // 检查是否按下Ctrl键（排除其他修饰键的组合）
  if ((event.ctrlKey || event.metaKey) && !event.shiftKey && !event.altKey) {
    // 防止重复触发
    if (event.repeat) {
      return false
    }

    try {
      const selectionSelect = lf.extension.selectionSelect
      if (selectionSelect) {
        selectionSelect.openSelectionSelect()
        // 添加样式指示器，让用户知道框选模式已激活
        document.body.style.cursor = 'crosshair'
      }
    } catch (error) {
      console.error('开启框选模式失败:', error)
    }
  }
}

// 处理Ctrl键松开关闭框选
const handleCtrlKeyUp = (event) => {
  // 检查组件是否已挂载和LogicFlow实例是否存在
  if (!isComponentMounted.value || !lf) {
    return false
  }

  // 检查是否松开Ctrl键
  if (event.key === 'Control' || event.key === 'Meta') {
    try {
      const selectionSelect = lf.extension.selectionSelect
      if (selectionSelect) {
        selectionSelect.closeSelectionSelect()
        // 恢复默认鼠标样式
        document.body.style.cursor = ''
      }
    } catch (error) {
      console.error('关闭框选模式失败:', error)
    }
  }
}

// 处理键盘Delete键删除、Ctrl+Z撤销和Ctrl+Shift+K调试面板功能
const handleKeyDown = (event) => {
  // 检查组件是否已挂载和LogicFlow实例是否存在
  if (!isComponentMounted.value || !lf) {
    return false
  }

  // 防止在输入框等元素中触发操作
  if (isEditableElement(event.target)) {
    return false
  }

  // 处理Ctrl+Shift+K切换调试面板
  if (
    (event.ctrlKey || event.metaKey) &&
    event.shiftKey &&
    event.key.toLowerCase() === 'k'
  ) {
    event.preventDefault()
    toggleDebugPanel()
    return true
  }

  // 检查是否按下Delete或Backspace键
  const isDeleteKey = event.key === 'Delete' || event.key === 'Backspace'
  if (!isDeleteKey) {
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

/**
 * 处理分组节点右键点击
 */
const handleGroupRightClick = (nodeData) => {
  if (!lf || !nodeData) return

  try {
    const groupModel = lf.getNodeModelById(nodeData.id)
    if (!groupModel) return

    // 获取当前分组的属性
    const properties = groupModel.properties || {}
    const text = groupModel.text?.value || ''

    // 填充表单数据
    // 注意：isRestrict 是 GroupNode 模型的直接属性，优先从模型读取，其次从 properties 读取
    groupEditForm.value = {
      name: text,
      fillColor: properties.fillColor || '#F4F5F6',
      fillOpacity:
        properties.fillOpacity !== undefined ? properties.fillOpacity : 0.3,
      strokeColor: properties.strokeColor || '#CECECE',
      strokeWidth: properties.strokeWidth || 2,
      strokeDasharray: properties.strokeDasharray || '',
      isRestrict:
        groupModel.isRestrict !== undefined
          ? groupModel.isRestrict
          : properties.isRestrict !== undefined
          ? properties.isRestrict
          : false
    }

    console.log('打开分组编辑:', {
      modelIsRestrict: groupModel.isRestrict,
      propertiesIsRestrict: properties.isRestrict,
      formIsRestrict: groupEditForm.value.isRestrict
    })

    // 保存当前编辑的分组ID
    currentEditingGroupId.value = nodeData.id

    // 显示模态框
    showGroupEditModal.value = true
  } catch (error) {
    console.error('打开分组编辑失败:', error)
    message.error('打开编辑失败')
  }
}

/**
 * 处理普通节点右键点击，打开属性编辑
 */
const handleNodeRightClick = (nodeData) => {
  if (!lf || !nodeData) return
  try {
    const nodeModel = lf.getNodeModelById(nodeData.id)
    if (!nodeModel) return

    currentEditingNodeId.value = nodeData.id
    const isVirtual = !!(nodeModel.properties && nodeModel.properties.isVirtual)
    nodePropsForm.value = {
      isVirtual
    }
    showNodePropsModal.value = true
  } catch (error) {
    console.error('打开节点属性失败:', error)
    message.error('打开节点属性失败')
  }
}

/**
 * 确认节点属性编辑
 */
const handleNodePropsConfirm = () => {
  if (!lf || !currentEditingNodeId.value) return
  try {
    const nodeModel = lf.getNodeModelById(currentEditingNodeId.value)
    if (!nodeModel) {
      message.error('未找到节点')
      return
    }

    nodeModel.setProperties({
      ...nodeModel.properties,
      isVirtual: !!nodePropsForm.value.isVirtual
    })

    message.success('节点属性更新成功')
    showNodePropsModal.value = false
    currentEditingNodeId.value = null
  } catch (error) {
    console.error('更新节点属性失败:', error)
    message.error('更新节点属性失败')
  }
}

/**
 * 取消节点属性编辑
 */
const handleNodePropsCancel = () => {
  showNodePropsModal.value = false
  currentEditingNodeId.value = null
}

/**
 * 确认分组编辑
 */
const handleGroupEditConfirm = () => {
  if (!lf || !currentEditingGroupId.value) return

  try {
    const groupModel = lf.getNodeModelById(currentEditingGroupId.value)
    if (!groupModel) {
      message.error('未找到分组节点')
      return
    }

    // 更新 isRestrict 属性（这是 GroupNode 的直接属性）
    groupModel.isRestrict = groupEditForm.value.isRestrict

    // 使用 setProperties 方法直接更新分组样式属性，避免删除重建导致子节点丢失
    groupModel.setProperties({
      ...groupModel.properties,
      fillColor: groupEditForm.value.fillColor,
      fillOpacity: groupEditForm.value.fillOpacity,
      strokeColor: groupEditForm.value.strokeColor,
      strokeWidth: groupEditForm.value.strokeWidth,
      strokeDasharray: groupEditForm.value.strokeDasharray,
      isRestrict: groupEditForm.value.isRestrict // 同时保存到 properties 中以便持久化
    })

    // 更新分组名称
    if (groupEditForm.value.name) {
      groupModel.updateText(groupEditForm.value.name)
    }

    console.log('编辑分组 - 更新后的属性:', {
      isRestrict: groupModel.isRestrict,
      properties: groupModel.properties
    })
    message.success('分组样式更新成功')

    // 关闭模态框
    showGroupEditModal.value = false
    currentEditingGroupId.value = null
  } catch (error) {
    console.error('更新分组失败:', error)
    message.error('更新分组失败')
  }
}

/**
 * 取消分组编辑
 */
const handleGroupEditCancel = () => {
  showGroupEditModal.value = false
  currentEditingGroupId.value = null
}
</script>

<style lang="less">
.form-hint {
  font-size: 12px;
  color: #999;
}
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
    top: 2px;
    right: 2px;
    padding: 0 8px;
    margin: 0;
    // 一键美化按钮样式
    .lf-control-item {
      padding: 4px 8px;
      .lf-control-text {
        font-size: 11px;
      }
      i {
        width: 12px;
        height: 12px;
      }
      &[data-key='beautify'],
      &[data-key='center'],
      &[data-key='createGroup'] {
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
        font-size: 12px;
        line-height: 1;
        display: block;
      }
    }

    // 居中按钮图标
    .lf-control-center {
      &::before {
        content: '◉';
        font-size: 12px;
        line-height: 1;
        display: block;
      }
    }

    // 创建分组按钮图标
    .lf-control-create-group {
      &::before {
        content: '📦';
        font-size: 12px;
        line-height: 1;
        display: block;
      }
    }
  }

  // 取消边的箭头
  :deep(.lf-edge .lf-arrow) {
    display: none !important;
  }

  // 确保所有类型的边都没有箭头
  :deep(.lf-edge-polyline),
  :deep(.lf-edge-line),
  :deep(.lf-edge-bezier) {
    marker-end: none !important;
    marker-start: none !important;
  }

  // 分组节点文本样式
  :deep(.lf-node-group .lf-node-text) {
    font-size: 14px;
    font-weight: 600;
    fill: #1890ff;
    cursor: default;
    user-select: none;
    pointer-events: none;
  }

  // 增强分组节点的resize锚点点击区域与兼容性
  :deep(.lf-node-group .lf-resize-control) {
    pointer-events: auto !important;
  }
  :deep(.lf-node-group .lf-resize-control circle) {
    r: 8 !important;
    fill: #1677ff !important;
    stroke: #ffffff !important;
    stroke-width: 1.5 !important;
    cursor: nwse-resize !important;
  }

  :deep(.lf-node-group .lf-node-text-edit) {
    font-size: 14px;
    font-weight: 600;
    color: #1890ff;
    padding: 4px 8px;
    border: 1px solid #1890ff;
    border-radius: 4px;
    background: white;
    outline: none;

    &:focus {
      border-color: #40a9ff;
      box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
    }
  }

  // 分组编辑表单样式
  .group-edit-form {
    .form-item {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }

      .form-label {
        display: block;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #333;
      }

      .color-picker-wrapper {
        display: flex;
        gap: 8px;
        align-items: center;

        .color-input {
          width: 60px;
          height: 32px;
          border: 1px solid #d9d9d9;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            border-color: #40a9ff;
          }
        }

        .color-text {
          flex: 1;
        }
      }
    }
  }

  // 调试面板样式
  .debug-panel {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 600px;
    max-height: 80vh;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .debug-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      .debug-panel-title {
        font-size: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .debug-panel-close {
        font-size: 28px;
        line-height: 1;
        cursor: pointer;
        opacity: 0.8;
        transition: opacity 0.2s;
        padding: 0 4px;

        &:hover {
          opacity: 1;
        }
      }
    }

    .debug-panel-content {
      flex: 1;
      padding: 20px;
      overflow-y: auto;

      .debug-section {
        margin-bottom: 24px;

        &:last-child {
          margin-bottom: 0;
        }

        .debug-section-title {
          font-size: 14px;
          font-weight: 600;
          color: #333;
          margin: 0 0 12px 0;
          padding-bottom: 8px;
          border-bottom: 2px solid #f0f0f0;
        }

        .debug-buttons {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }

        .debug-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          padding: 16px 12px;
          border: 2px solid #e8e8e8;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.3s;
          font-family: inherit;

          &:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          }

          &:active:not(:disabled) {
            transform: translateY(0);
          }

          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }

          .debug-btn-icon {
            font-size: 32px;
            line-height: 1;
          }

          .debug-btn-text {
            font-size: 14px;
            font-weight: 600;
            color: #333;
          }

          .debug-btn-desc {
            font-size: 12px;
            color: #999;
          }

          &.debug-btn-micro {
            border-color: #52c41a;

            &:hover:not(:disabled) {
              border-color: #52c41a;
              background: #f6ffed;
            }
          }

          &.debug-btn-standard {
            border-color: #1890ff;

            &:hover:not(:disabled) {
              border-color: #1890ff;
              background: #e6f7ff;
            }
          }

          &.debug-btn-large {
            border-color: #fa8c16;

            &:hover:not(:disabled) {
              border-color: #fa8c16;
              background: #fff7e6;
            }
          }

          &.debug-btn-huge {
            border-color: #f5222d;

            &:hover:not(:disabled) {
              border-color: #f5222d;
              background: #fff1f0;
            }
          }
        }

        .debug-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;

          .debug-stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: #f5f5f5;
            border-radius: 6px;
            font-size: 13px;

            .debug-stat-label {
              color: #666;
              font-weight: 500;
            }

            .debug-stat-value {
              color: #333;
              font-weight: 600;

              &.success {
                color: #52c41a;
              }

              &.error {
                color: #f5222d;
              }
            }
          }
        }

        .debug-btn-clear {
          width: 100%;
          padding: 12px;
          background: #ff4d4f;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          font-family: inherit;

          &:hover:not(:disabled) {
            background: #ff7875;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
          }

          &:active:not(:disabled) {
            transform: translateY(0);
          }

          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
        }
      }
    }

    .debug-panel-footer {
      padding: 12px 20px;
      background: #f5f5f5;
      border-top: 1px solid #e8e8e8;
      text-align: center;

      .debug-hint {
        font-size: 12px;
        color: #999;
      }
    }
  }
}
</style>
