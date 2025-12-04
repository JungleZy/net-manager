<template>
  <div
    class="p-[12px] size-full network"
    ref="networkWrapperRef"
    :class="{ 'dark-mode': isDarkMode }"
  >
    <div
      class="size-full rounded-lg shadow p-[6px] relative network-container"
      ref="networkContainerRef"
    >
      <!-- 拓扑图容器 -->
      <div class="w-full h-full" ref="containerRef"></div>

      <!-- 状态统计面板 -->
      <div class="stats-panel">
        <div class="stat-item">
          <span class="stat-label">总节点</span>
          <span class="stat-value">{{ stats.totalNodes }}</span>
        </div>

        <!-- 在线设备 Popover -->
        <a-popover
          v-model:open="onlinePopoverVisible"
          title="在线设备列表"
          trigger="click"
          placement="bottomLeft"
          overlayClassName="device-list-popover"
        >
          <template #content>
            <div class="device-list-content">
              <div v-if="onlineDevicesList.length === 0" class="empty-state">
                暂无在线设备
              </div>
              <div
                v-else
                class="device-item"
                v-for="device in onlineDevicesList"
                :key="device.id"
                @click="handleDeviceListItemClick(device)"
              >
                <div class="device-name">
                  {{ device.hostname || device.name || '未命名设备' }}
                </div>
                <div class="device-info">
                  <span class="device-ip">{{ device.ip || '-' }}</span>
                  <span class="device-status online-badge">在线</span>
                </div>
              </div>
            </div>
          </template>
          <div class="stat-item clickable">
            <span class="stat-label">在线</span>
            <span class="stat-value online">{{ stats.onlineNodes }}</span>
          </div>
        </a-popover>

        <!-- 离线设备 Popover -->
        <a-popover
          v-model:open="offlinePopoverVisible"
          title="离线设备列表"
          trigger="click"
          placement="bottomLeft"
          overlayClassName="device-list-popover"
        >
          <template #content>
            <div class="device-list-content">
              <div v-if="offlineDevicesList.length === 0" class="empty-state">
                暂无离线设备
              </div>
              <div
                v-else
                class="device-item"
                v-for="device in offlineDevicesList"
                :key="device.id"
                @click="handleDeviceListItemClick(device)"
              >
                <div class="device-name">
                  {{ device.hostname || device.name || '未命名设备' }}
                </div>
                <div class="device-info">
                  <span class="device-ip">{{ device.ip || '-' }}</span>
                  <span class="device-status offline-badge">离线</span>
                </div>
              </div>
            </div>
          </template>
          <div class="stat-item clickable">
            <span class="stat-label">离线</span>
            <span class="stat-value offline">{{ stats.offlineNodes }}</span>
          </div>
        </a-popover>
      </div>

      <!-- 控制按钮 -->
      <div class="control-panel">
        <a-input-search
          ref="searchInputRef"
          v-model:value="searchValue"
          style="width: 180px"
          placeholder="输入设备名称或IP"
          @search="handleSearchImmediate"
          @input="handleSearch"
          @focus="
            () => {
              if (searchValue) handleSearchImmediate()
            }
          "
        >
          <template #enterButton>
            <a-button class="layout-center search-button" style="width: 32px">
              <SearchOutlined style="font-size: 16px" />
            </a-button>
          </template>
        </a-input-search>
        <!-- 刷新按钮 -->
        <a-tooltip title="刷新拓扑图" placement="bottom">
          <a-button
            @click="handleRefresh"
            :loading="loading"
            class="layout-center"
          >
            <template #icon>
              <ReloadOutlined />
            </template>
          </a-button>
        </a-tooltip>

        <!-- 居中按钮 -->
        <a-tooltip title="居中显示" placement="bottom">
          <a-button @click="handleCenter" class="layout-center">
            <template #icon>
              <AimOutlined />
            </template>
          </a-button>
        </a-tooltip>

        <!-- 全屏按钮 -->
        <a-tooltip v-if="!isFullscreen" title="全屏" placement="top">
          <a-dropdown>
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
        </a-tooltip>

        <!-- 退出全屏按钮 -->
        <a-tooltip v-else title="退出全屏" placement="bottom">
          <a-button class="layout-center" @click="exitFullscreen">
            <template #icon>
              <FullscreenExitOutlined />
            </template>
          </a-button>
        </a-tooltip>

        <!-- 主题切换按钮 -->
        <a-tooltip
          :title="isDarkMode ? '切换到明亮模式' : '切换到暗黑模式'"
          placement="bottomRight"
        >
          <a-button class="layout-center" @click="toggleTheme">
            <template #icon>
              <BulbFilled v-if="isDarkMode" />
              <BulbOutlined v-else />
            </template>
          </a-button>
        </a-tooltip>
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

      <!-- 搜索结果面板 -->
      <div v-if="showSearchResults" class="search-results-panel" @click.stop>
        <div class="search-results-header">
          <span>搜索结果 ({{ searchResults.length }})</span>
          <a-button
            type="text"
            size="small"
            @click="closeSearchResults"
            class="close-btn"
          >
            <template #icon>
              <CloseOutlined />
            </template>
          </a-button>
        </div>
        <div class="search-results-list">
          <div
            v-for="result in searchResults"
            :key="result.id"
            class="search-result-item"
            @click="handleSearchResultClick(result)"
          >
            <div class="result-info">
              <div class="result-name">
                <span class="result-type-badge device">
                  {{ result.type }}
                </span>
                {{ result.name }}
              </div>
              <div class="result-details">
                <span class="result-ip">{{ result.ip || '-' }}</span>
                <span class="result-status" :class="result.status">
                  {{ result.status === 'online' ? '在线' : '离线' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  onMounted,
  onUnmounted,
  nextTick,
  computed,
  shallowRef,
  useTemplateRef,
  watch
} from 'vue'
import { LogicFlow } from '@logicflow/core'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'
import { default as customNodes } from '@/common/node/index'
import { default as customEdges } from '@/common/edge/index'
import { setTheme } from '@/common/node/nodeConfig'
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
  FullscreenExitOutlined,
  BulbOutlined,
  BulbFilled,
  SearchOutlined,
  CloseOutlined
} from '@ant-design/icons-vue'
import DeviceNodeDetailPopover from '../../components/network/DeviceNodeDetailPopover.vue'
import SwitchNodeDetailPopover from '../../components/network/SwitchNodeDetailPopover.vue'
import { formatLocalDateTime, handleCenterView } from '@/common/utils/Utils'

const containerRef = useTemplateRef('containerRef')
const networkWrapperRef = useTemplateRef('networkWrapperRef')
const networkContainerRef = useTemplateRef('networkContainerRef')
const searchInputRef = useTemplateRef('searchInputRef')
const devices = ref([])
const switches = ref([])
// 使用 ref 确保响应式更新能够正确触发
let lf = null
const loading = ref(false)
const topologyData = shallowRef({ nodes: [], edges: [] })
const deviceStatusMap = reactive(new Map()) // 存储设备状态 {device_id: 'online'|'offline'}
const edgeDataMap = shallowRef(new Map()) // 存储边的数据传输状态 {edgeId: hasData}
const isComponentMounted = ref(false)

// 优化：使用 Map 加速设备查找
const deviceIdMap = shallowRef(new Map()) // {id/client_id: device}
const switchIdMap = shallowRef(new Map()) // {id/switch_id: switch}

// 全屏相关状态
const isFullscreen = ref(false)
const fullscreenMode = ref('') // 'page' | 'screen'

// 主题模式状态
const isDarkMode = ref(false)
const THEME_STORAGE_KEY = 'network-theme-mode'

// 设备列表 Popover 状态
const onlinePopoverVisible = ref(false)
const offlinePopoverVisible = ref(false)

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

// 搜索相关
const searchValue = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const searchResultsPosition = ref({ x: 0, y: 0 })
let searchDebounceTimer = null // 搜索防抖定时器

// 执行搜索（内部函数，不防抖）
const performSearch = (searchText) => {
  if (!searchText) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }

  const results = []

  // 搜索设备
  for (const device of devices.value) {
    const hostname = (device.hostname || '').toLowerCase()
    const alias = (device.alias || '').toLowerCase()
    const ip = device.ip || device.networks?.[0]?.ip_address || ''

    if (
      hostname.includes(searchText) ||
      alias.includes(searchText) ||
      ip.includes(searchText)
    ) {
      results.push({
        id: device.client_id || device.id,
        name: device.alias || device.hostname || '未命名设备',
        ip: ip,
        type: device.type,
        status: device.online ? 'online' : 'offline'
      })
    }
  }

  // 搜索交换机
  for (const switchDevice of switches.value) {
    const name = (switchDevice.device_name || '').toLowerCase()
    const alias = (switchDevice.alias || '').toLowerCase()
    const ip = (switchDevice.ip || '').toLowerCase()

    if (
      name.includes(searchText) ||
      alias.includes(searchText) ||
      ip.includes(searchText)
    ) {
      results.push({
        id: switchDevice.switch_id || switchDevice.id,
        name:
          switchDevice.alias ||
          switchDevice.device_name ||
          '未命名' + switchDevice.device_type,
        ip: switchDevice.ip,
        type: switchDevice.device_type,
        status: switchDevice.online ? 'online' : 'offline'
      })
    }
  }

  searchResults.value = results
  showSearchResults.value = results.length > 0

  // 计算搜索结果框位置（在搜索框下方）
  calculateSearchResultsPosition()

  // 只在有搜索文本且没有结果时提示
  if (results.length === 0) {
    message.info('未找到匹配的设备')
  }
}

// 搜索处理函数（带防抖）
const handleSearch = (value) => {
  // 清除之前的定时器
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }

  // 处理不同的输入情况：
  // 1. @search 事件传入字符串
  // 2. @input 事件传入事件对象
  // 3. 直接调用时传入字符串
  let searchText = ''

  if (typeof value === 'string') {
    searchText = value.trim().toLowerCase()
  } else if (value && typeof value === 'object' && 'target' in value) {
    // 事件对象，从 target.value 获取
    searchText = (value.target?.value || '').trim().toLowerCase()
  } else {
    // 使用 searchValue.value
    searchText = (searchValue.value || '').trim().toLowerCase()
  }

  // 如果搜索文本为空，立即清空结果，不需要防抖
  if (!searchText) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }

  // 对于 @input 事件，使用防抖（300ms）
  searchDebounceTimer = setTimeout(() => {
    performSearch(searchText)
  }, 300)
}

// 立即搜索（用于 @search 事件和快捷键）
const handleSearchImmediate = (value) => {
  // 清除防抖定时器
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }

  let searchText = ''
  if (typeof value === 'string') {
    searchText = value.trim().toLowerCase()
  } else {
    searchText = (searchValue.value || '').trim().toLowerCase()
  }

  performSearch(searchText)
}

// 计算搜索结果框位置
const calculateSearchResultsPosition = () => {
  // 搜索框在控制面板中，位于右上角
  // 我们将结果框显示在搜索框下方
  const controlPanel = document.querySelector('.control-panel')
  if (controlPanel) {
    const rect = controlPanel.getBoundingClientRect()
    searchResultsPosition.value = {
      x: rect.left,
      y: rect.bottom + 8
    }
  }
}

// 点击搜索结果
const handleSearchResultClick = (result) => {
  if (!lf) return

  // 关闭搜索结果
  showSearchResults.value = false
  searchValue.value = ''

  // 查找对应的节点
  const graphData = lf.getGraphData()
  const node = graphData.nodes.find(
    (n) => n.properties?.data?.id === result.id || n.id === result.id
  )

  if (node) {
    // 居中显示节点
    lf.focusOn({
      id: node.id,
      coordinate: {
        x: node.x,
        y: node.y
      }
    })

    // 延迟一点再触发节点详情
    setTimeout(() => {
      // 模拟点击事件数据
      const container = containerRef.value
      if (container) {
        const containerRect = container.getBoundingClientRect()
        const transform = lf.getTransform()

        // 计算节点在画布中的位置
        const nodeCanvasX = node.x * transform.SCALE_X + transform.TRANSLATE_X
        const nodeCanvasY = node.y * transform.SCALE_Y + transform.TRANSLATE_Y

        // 创建模拟的事件对象
        const mockEvent = {
          clientX: containerRect.left + nodeCanvasX,
          clientY: containerRect.top + nodeCanvasY
        }

        // 触发节点点击处理
        handleNodeClick(node, mockEvent)
      }
    }, 100)
  } else {
    message.warning('该设备未在拓扑图中显示')
  }
}

// 关闭搜索结果
const closeSearchResults = () => {
  showSearchResults.value = false
}

// 点击容器外部关闭搜索结果
const handleClickOutside = (event) => {
  if (!showSearchResults.value) return

  const searchPanel = document.querySelector('.search-results-panel')
  const searchInput = document.querySelector('.control-panel .ant-input-search')

  if (searchPanel && searchInput) {
    const clickedInsidePanel = searchPanel.contains(event.target)
    const clickedInsideInput = searchInput.contains(event.target)

    if (!clickedInsidePanel && !clickedInsideInput) {
      closeSearchResults()
    }
  }
}

// 点击设备列表项（在线/离线面板）定位到拓扑节点
const handleDeviceListItemClick = (device) => {
  if (!lf || !device) return

  try {
    // 关闭对应的 Popover
    onlinePopoverVisible.value = false
    offlinePopoverVisible.value = false

    // 查找节点（优先 properties.data.id，其次节点 id）
    const graphData = lf.getGraphData()
    const node = graphData.nodes.find(
      (n) => n.properties?.data?.id === device.id || n.id === device.id
    )

    if (node) {
      // 聚焦到该节点
      lf.focusOn({
        id: node.id,
        coordinate: { x: node.x, y: node.y }
      })

      // 延迟触发节点详情弹窗，模拟点击位置
      setTimeout(() => {
        const container = containerRef.value
        if (container) {
          const containerRect = container.getBoundingClientRect()
          const transform = lf.getTransform()

          const nodeCanvasX = node.x * transform.SCALE_X + transform.TRANSLATE_X
          const nodeCanvasY = node.y * transform.SCALE_Y + transform.TRANSLATE_Y

          const mockEvent = {
            clientX: containerRect.left + nodeCanvasX,
            clientY: containerRect.top + nodeCanvasY
          }

          handleNodeClick(node, mockEvent)
        }
      }, 300)

      message.success(
        `已定位到: ${device.name || device.hostname || device.ip || device.id}`
      )
    } else {
      message.warning('该设备未在拓扑图中显示')
    }
  } catch (error) {
    console.error('定位设备失败:', error)
    message.error('定位设备失败')
  }
}

// 处理 Ctrl+F 快捷键聚焦搜索框
const handleKeyboardShortcut = (event) => {
  // Ctrl+F 或 Command+F（Mac）聚焦搜索框
  if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
    event.preventDefault() // 阻止浏览器默认的查找功能

    // 使用 nextTick 确保 DOM 已渲染
    nextTick(() => {
      if (searchInputRef.value) {
        // 方法1: 尝试通过 focus 方法聚焦（Ant Design Vue 3.x）
        if (typeof searchInputRef.value.focus === 'function') {
          searchInputRef.value.focus()

          // 如果有内容，延迟一点再全选
          if (searchValue.value) {
            setTimeout(() => {
              const inputElement =
                searchInputRef.value?.input ||
                searchInputRef.value?.$el?.querySelector('input')
              if (inputElement) {
                inputElement.select()
              }
            }, 50)
          }
        }
        // 方法2: 直接访问原生 input 元素
        else {
          const inputElement =
            searchInputRef.value.input ||
            searchInputRef.value.$el?.querySelector('input')
          if (inputElement) {
            inputElement.focus()
            // 如果有内容，全选文本方便用户直接输入新内容
            if (searchValue.value) {
              inputElement.select()
            }
          }
        }
      }
    })
  }
}

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

// 切换主题模式
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  // 同步更新主题配置
  setTheme(isDarkMode.value ? 'dark' : 'light')
  // 保存到 localStorage
  try {
    localStorage.setItem(THEME_STORAGE_KEY, isDarkMode.value ? 'dark' : 'light')
    message.success(`已切换到${isDarkMode.value ? '暗黑' : '明亮'}模式`)
  } catch (error) {
    console.error('保存主题设置失败:', error)
  }
}

// 监听主题切换，重新渲染节点文字颜色
watch(isDarkMode, (newValue) => {
  // 立即更新主题配置
  setTheme(newValue ? 'dark' : 'light')

  if (lf) {
    // 等待 DOM 更新完成后再重新渲染
    nextTick(() => {
      const graphData = lf.getGraphData()
      lf.render(graphData)
    })
  }
})

// 加载主题设置
const loadThemeSettings = () => {
  try {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
    if (savedTheme === 'dark') {
      isDarkMode.value = true
    }
    // 同步设置主题配置
    setTheme(isDarkMode.value ? 'dark' : 'light')
  } catch (error) {
    console.error('加载主题设置失败:', error)
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

// 统计信息（仅统计拓扑图中的节点）
const stats = computed(() => {
  // 过滤掉分组节点，仅统计实际设备/交换机节点
  const graphNodes = topologyData.value.nodes.filter(
    (node) => node.type !== 'customGroup'
  )

  const totalNodes = graphNodes.length

  // 仅统计在拓扑图中的节点的在线状态
  const allowedIds = new Set(
    graphNodes.map((n) => n.properties?.data?.id || n.id)
  )

  let onlineNodes = 0
  for (const [deviceId, status] of deviceStatusMap.entries()) {
    if (allowedIds.has(deviceId) && status === 'online') {
      onlineNodes++
    }
  }

  return {
    totalNodes,
    onlineNodes,
    offlineNodes: totalNodes - onlineNodes
  }
})

// 在线设备列表（仅展示拓扑图中的节点）
const onlineDevicesList = computed(() => {
  const list = []

  const graphNodes = topologyData.value.nodes.filter(
    (node) => node.type !== 'customGroup'
  )
  const allowedIds = new Set(
    graphNodes.map((n) => n.properties?.data?.id || n.id)
  )

  // 收集在线设备（仅拓扑节点）
  for (const device of devices.value) {
    const id = device.client_id || device.id
    const status = deviceStatusMap.get(id)
    if (allowedIds.has(id) && status === 'online') {
      list.push({
        id,
        hostname: device.hostname,
        name: device.alias || device.hostname,
        ip: device.ip || device.networks?.[0]?.ip_address,
        type: 'device'
      })
    }
  }

  // 收集在线交换机（仅拓扑节点）
  for (const switchDevice of switches.value) {
    const id = switchDevice.switch_id || switchDevice.id
    const status = deviceStatusMap.get(id)
    if (allowedIds.has(id) && status === 'online') {
      list.push({
        id,
        hostname: switchDevice.name || switchDevice.ip,
        name: switchDevice.alias || switchDevice.name,
        ip: switchDevice.ip,
        type: 'switch'
      })
    }
  }

  return list
})

// 离线设备列表（仅展示拓扑图中的节点）
const offlineDevicesList = computed(() => {
  const list = []

  const graphNodes = topologyData.value.nodes.filter(
    (node) => node.type !== 'customGroup'
  )
  const allowedIds = new Set(
    graphNodes.map((n) => n.properties?.data?.id || n.id)
  )

  // 收集离线设备（仅拓扑节点）
  for (const device of devices.value) {
    const id = device.client_id || device.id
    const status = deviceStatusMap.get(id)
    if (allowedIds.has(id) && status === 'offline') {
      list.push({
        id,
        hostname: device.hostname,
        name: device.alias || device.hostname,
        ip: device.ip || device.networks?.[0]?.ip_address,
        type: 'device'
      })
    }
  }

  // 收集离线交换机（仅拓扑节点）
  for (const switchDevice of switches.value) {
    const id = switchDevice.switch_id || switchDevice.id
    const status = deviceStatusMap.get(id)
    if (allowedIds.has(id) && status === 'offline') {
      list.push({
        id,
        hostname: switchDevice.name || switchDevice.ip,
        name: switchDevice.alias || switchDevice.name,
        ip: switchDevice.ip,
        type: 'switch'
      })
    }
  }

  return list
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
          const isVirtual = !!(node.properties && node.properties.isVirtual)

          // 优化：使用 Map 查找而非 find
          const device = deviceIdMap.value.get(deviceId)
          const switchDevice = switchIdMap.value.get(deviceId)

          let status = 'offline'
          if (isVirtual) {
            status = 'online'
          } else if (device) {
            status = device.online ? 'online' : 'offline'
          } else if (switchDevice) {
            status = switchDevice.online ? 'online' : 'offline'
          } else {
            status = node.properties?.status || 'offline'
          }

          deviceStatusMap.set(deviceId, status)
          if (node.properties) {
            node.properties.status = status
          } else {
            node.properties = { status }
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
      const interfaces = Array.isArray(switchDevice.interface_info)
        ? switchDevice.interface_info
        : []

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

  if (deviceIndex.value === -1 && switchIndex.value === -1) {
    message.error('该节点为虚拟设备，不支持查看详情!')
    return
  }

  // 计算 Popover 位置（使用鼠标点击位置）
  const container = containerRef.value
  if (container && event) {
    const containerRect = container.getBoundingClientRect()
    const transform = lf.getTransform()

    // 获取鼠标点击位置（相对于容器）
    const mouseX = event.clientX - containerRect.left
    const mouseY = event.clientY - containerRect.top

    // 计算节点在画布中的位置（考虑缩放和平移）
    const nodeCanvasX = nodeData.x * transform.SCALE_X + transform.TRANSLATE_X
    const nodeCanvasY = nodeData.y * transform.SCALE_Y + transform.TRANSLATE_Y

    // 智能计算 Popover 位置和方向（传入鼠标点击位置和节点位置）
    calculatePopoverPosition(
      mouseX,
      mouseY,
      nodeCanvasX,
      nodeCanvasY,
      containerRect
    )
  }

  // 显示 Popover
  popoverVisible.value = true
}

// 智能计算 Popover 位置和方向
const calculatePopoverPosition = (
  mouseX,
  mouseY,
  nodeX,
  nodeY,
  containerRect
) => {
  // 安全边距（像素）
  const SAFE_MARGIN = 1
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

  // 计算各个方向的可用空间（基于节点位置）
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

  console.log(
    `Popover弹出方向: ${placement}, 位置: (${finalX}, ${finalY})，鼠标位置: (${mouseX}, ${mouseY}), 节点位置: (${nodeX}, ${nodeY}), 箭头偏移: ${popoverArrowOffset.value}px`
  )
}

// 处理Popover关闭
const handlePopoverClose = () => {
  popoverVisible.value = false
  selectedNode.value = null
}

// 检查两个IP是否在同一网段（简单判断：前三段相同）
const isSameSubnet = (ip1, ip2) => {
  if (!ip1 || !ip2) return false
  const parts1 = ip1.split('.')
  const parts2 = ip2.split('.')
  if (parts1.length !== 4 || parts2.length !== 4) return false
  // 比较前三段
  return (
    parts1[0] === parts2[0] &&
    parts1[1] === parts2[1] &&
    parts1[2] === parts2[2]
  )
}

// 查找目标节点（降级策略）
const findTargetNode = (currentDeviceNode, gatewayIp, nodeByIp, graphData) => {
  // 策略 1: 直接根据网关IP查找
  let targetNode = nodeByIp.get(gatewayIp)
  if (targetNode) {
    console.log(`策略1: 直接找到网关节点 ${targetNode.id} (IP: ${gatewayIp})`)
    return targetNode
  }

  // 策略 2: 查找同网段的第一个节点
  const currentIp = currentDeviceNode.properties?.data?.ip
  if (currentIp) {
    for (const [ip, node] of nodeByIp) {
      if (node.id !== currentDeviceNode.id && isSameSubnet(currentIp, ip)) {
        console.log(
          `策略2: 找到同网段节点 ${node.id} (IP: ${ip}, 当前IP: ${currentIp})`
        )
        return node
      }
    }
  }

  // 策略 3: 查找所属连线的第一个节点
  if (graphData?.edges) {
    const connectedEdge = graphData.edges.find(
      (edge) =>
        edge.sourceNodeId === currentDeviceNode.id ||
        edge.targetNodeId === currentDeviceNode.id
    )
    if (connectedEdge) {
      const targetNodeId =
        connectedEdge.sourceNodeId === currentDeviceNode.id
          ? connectedEdge.targetNodeId
          : connectedEdge.sourceNodeId
      targetNode = graphData.nodes.find((node) => node.id === targetNodeId)
      if (targetNode) {
        // console.log(
        //   `策略3: 找到连线的节点 ${targetNode.id} (连线ID: ${connectedEdge.id})`
        // )
        return targetNode
      }
    }
  }

  console.warn(
    `所有策略均未找到目标节点 (网关IP: ${gatewayIp}, 当前IP: ${currentIp})`
  )
  return null
}

// 更新节点状态
const updateNodeStatus = (deviceId, status) => {
  if (!lf) return

  try {
    // 更新状态映射
    // 若节点为虚拟节点，强制在线
    const graphData = lf.getGraphData()
    const node = graphData.nodes.find(
      (n) => n.properties?.data?.id === deviceId || n.id === deviceId
    )
    const isVirtual = !!(node && node.properties && node.properties.isVirtual)
    const finalStatus = isVirtual ? 'online' : status
    deviceStatusMap.set(deviceId, finalStatus)

    // 查找对应的节点
    // graphData 已在上方获取

    if (node) {
      // 更新节点属性
      const nodeModel = lf.getNodeModelById(node.id)
      if (nodeModel) {
        nodeModel.setProperties({
          ...node.properties,
          status: finalStatus
        })
      } else {
        console.warn(`无法获取节点模型: ${node.id}`)
      }
      // 如果设备离线,停止所有与该节点相连的边的动画
      if (finalStatus === 'offline') {
        stopNodeRelatedEdgesAnimation(node.id, graphData)
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
      for (const edge of relatedEdges) {
        // 检查边的当前状态
        const currentState = edgeDataMap.value.get(edge.id)

        // 如果已经是关闭状态，则跳过操作
        if (currentState === false) {
          continue
        }

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
      // 查找源节点和目标节点
      const sourceNode = graphData.nodes.find((n) => n.id === sourceId)
      const targetNode = graphData.nodes.find((n) => n.id === targetId)

      // 检查节点在线状态
      const sourceStatus = sourceNode?.properties?.status || 'offline'
      const targetStatus = targetNode?.properties?.status || 'offline'
      const bothOnline = sourceStatus === 'online' && targetStatus === 'online'

      // 如果任意一个节点离线，强制关闭动画
      let finalHasData = hasData
      if (!bothOnline) {
        finalHasData = false
        // console.log(
        //   `边 ${edge.id} 的节点不全在线 (源: ${sourceStatus}, 目标: ${targetStatus})，关闭动画`
        // )
      }

      // 检查边的当前状态
      const currentState = edgeDataMap.value.get(edge.id)

      // 如果当前状态和需要更新的状态一致，则跳过更新
      if (currentState === finalHasData) {
        // console.log(`边 ${edge.id} 状态未变化 (${finalHasData})，跳过更新`)
        return
      }

      // console.log(`更新边 ${edge.id} 状态: ${currentState} -> ${finalHasData}`)

      // 更新状态映射
      edgeDataMap.value.set(edge.id, finalHasData)

      // 根据状态开启或关闭动画
      if (finalHasData) {
        lf?.openEdgeAnimation(edge.id)
      } else {
        lf?.closeEdgeAnimation(edge.id)
      }
    }
  } catch (error) {
    console.error('更新边数据状态失败:', error)
  }
}

// 处理设备状态更新（优化：使用 Map 加速查找）
const handleDeviceStatusUpdate = (data) => {
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
      device.last_seen = formatLocalDateTime()
    }

    const switchDevice = switchIdMap.value.get(deviceId)
    if (switchDevice) {
      switchDevice.status = status
      switchDevice.online = status === 'online'
      switchDevice.last_seen = formatLocalDateTime()
    }
    console.log('设备列表已更新:', devices.value)

    // 同步更新与该设备相关的边颜色，避免延迟
    updateEdgesByDeviceStatus(deviceId)
  }
}

// 根据端点在线状态更新与设备相关的边颜色（移除接口流量判断，仅按在线状态）
const updateEdgesByDeviceStatus = (deviceId) => {
  if (!lf || !deviceId) return

  try {
    const graphData = lf.getGraphData()
    // 兼容 properties.data.id 与节点 id
    const node = graphData.nodes.find(
      (n) => n.properties?.data?.id === deviceId || n.id === deviceId
    )
    if (!node) return

    const nodeId = node.id

    // 构建节点索引以加速查找
    const nodeById = new Map()
    for (let i = 0, len = graphData.nodes.length; i < len; i++) {
      const n = graphData.nodes[i]
      nodeById.set(n.id, n)
    }

    // 查找与该节点相连的所有边
    const relatedEdges = graphData.edges.filter(
      (e) => e.sourceNodeId === nodeId || e.targetNodeId === nodeId
    )
    if (relatedEdges.length === 0) return

    for (let i = 0, len = relatedEdges.length; i < len; i++) {
      const edge = relatedEdges[i]
      const otherId =
        edge.sourceNodeId === nodeId ? edge.targetNodeId : edge.sourceNodeId

      const srcNode = node
      const dstNode = nodeById.get(otherId)
      if (!dstNode) continue

      const srcStatus =
        deviceStatusMap.get(srcNode.properties?.data?.id || srcNode.id) ||
        srcNode.properties?.status ||
        'offline'
      const dstStatus =
        deviceStatusMap.get(dstNode.properties?.data?.id || dstNode.id) ||
        dstNode.properties?.status ||
        'offline'

      const active = srcStatus === 'online' && dstStatus === 'online'
      const current = !!edge.properties?.hasData
      if (current === active) continue

      const edgeModel = lf.getEdgeModelById(edge.id)
      if (edgeModel) {
        edgeModel.setProperties({
          ...(edge.properties || {}),
          // 两端都在线：设置为活跃颜色(#1890ff)，否则灰色(#999)
          hasData: active
        })
      }
    }
  } catch (error) {
    console.error('根据节点在线状态更新边颜色失败:', error)
  }
}

// 处理SNMP设备更新（包含接口流量数据）
const handleSnmpDeviceUpdate = (data) => {
  if (!data) return

  const deviceId = data.switch_id || data.device_id

  // 更新交换机在线状态以及列表中的对应数据（优化：使用 Map 查找）
  if (deviceId) {
    // 更新设备在线状态
    updateNodeStatus(deviceId, data?.type === 'success' ? 'online' : 'offline')
    const switchDevice = switchIdMap.value.get(deviceId)

    if (switchDevice) {
      Object.assign(switchDevice, data, {
        status: data?.type === 'success' ? 'online' : 'offline',
        last_updated: formatLocalDateTime()
      })
    } else {
      // 新交换机，添加到列表
      const newSwitch = {
        ...data,
        status: data?.type === 'success' ? 'online' : 'offline',
        id: deviceId,
        last_updated: formatLocalDateTime()
      }
      switches.value.push(newSwitch)
      // 更新 Map
      updateSwitchIdMap()
    }
    // 按端点在线状态更新与该设备相关的边颜色
    updateEdgesByDeviceStatus(deviceId)
  }
}

const handleSnmpInterfaceUpdate = (data) => {
  if (!data) return

  const deviceId = data.switch_id || data.device_id

  // 更新接口流量数据（优化：使用 Map 查找）
  if (deviceId) {
    const switchDevice = switchIdMap.value.get(deviceId)
    if (switchDevice) {
      switchDevice.interface_info = data.interface_info
      switchDevice.interface_update_time = formatLocalDateTime()
    }
  }
}

// 处理客户端设备信息更新（包含网络流量数据）
const handleDeviceInfoUpdate = (data) => {
  if (!data) return

  const deviceId = data.client_id || data.device_id || data.id

  // 更新设备列表中的对应数据（优化：使用 Map 查找）
  if (deviceId) {
    updateNodeStatus(deviceId, 'online')

    const device = deviceIdMap.value.get(deviceId)
    if (device) {
      Object.assign(device, data, {
        status: 'online',
        last_updated: formatLocalDateTime()
      })
    } else {
      // 新设备，添加到列表
      const newDevice = {
        ...data,
        id: deviceId,
        status: 'online',
        last_updated: formatLocalDateTime()
      }
      devices.value.push(newDevice)
      // 更新 Map
      updateDeviceIdMap()
    }
    // 按端点在线状态更新与该设备相关的边颜色
    updateEdgesByDeviceStatus(deviceId)
  }
}

// 初始化PubSub订阅
const initPubSubSubscriptions = () => {
  try {
    // 订阅设备状态更新
    PubSub.subscribe(wsCode.DEVICE_STATUS, handleDeviceStatusUpdate)

    // 订阅SNMP设备更新
    PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, handleSnmpDeviceUpdate)

    // 订阅客户端设备信息更新（按在线状态更新边）
    PubSub.subscribe(wsCode.DEVICE_INFO, handleDeviceInfoUpdate)

    // 订阅SNMP设备信息更新（按在线状态更新边）
    PubSub.subscribe(wsCode.SNMP_INTERFACE_UPDATE, handleSnmpInterfaceUpdate)

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
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }

  // 移除全局点击事件监听
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

    // 加载主题设置
    loadThemeSettings()

    // 初始化LogicFlow
    initLogicFlow()

    // 初始化 ResizeObserver
    initResizeObserver()

    // 添加全屏状态监听
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('msfullscreenchange', handleFullscreenChange)

    // 添加点击外部事件监听
    document.addEventListener('click', handleClickOutside)

    // 添加键盘快捷键监听
    document.addEventListener('keydown', handleKeyboardShortcut)
  })
})

onUnmounted(() => {
  // 移除全屏状态监听
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)

  // 移除点击外部事件监听
  document.removeEventListener('click', handleClickOutside)

  // 移除键盘快捷键监听
  document.removeEventListener('keydown', handleKeyboardShortcut)

  // 组件销毁时清理资源
  cleanup()
})
</script>

<style lang="less">
@import './style.less';
</style>
