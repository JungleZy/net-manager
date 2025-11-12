<template>
  <div
    v-if="visible && index > -1"
    ref="popoverRef"
    class="custom-popover"
    :class="`popover-${placement}`"
    :style="{
      left: position.x + 'px',
      top: position.y + 'px',
      '--max-height': maxHeight + 'px',
      '--arrow-offset': arrowOffset + 'px'
    }"
    @click.stop
  >
    <div class="node-detail-popover">
      <!-- 头部 -->
      <div class="popover-header">
        <div class="header-top">
          <h4 class="popover-title">
            {{ device.hostname || '未命名设备' }}
            <span style="font-size: 14px">{{
              device.alias ? ' - ' + device.alias : ''
            }}</span>
          </h4>
          <span :class="['status-badge', device.online ? 'online' : 'offline']">
            {{ device.online ? '在线' : '离线' }}
          </span>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="popover-body">
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="section-title">基本信息</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">操作系统</span>
              <span class="value"
                >{{ device.os_name }} {{ device.os_version }}</span
              >
            </div>
            <div class="info-item">
              <span class="label">架构</span>
              <span class="value">{{ device.os_architecture }}</span>
            </div>
            <div class="info-item">
              <span class="label">机器类型</span>
              <span class="value">{{ device.machine_type }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后更新</span>
              <span class="value">{{ formatTime(device.timestamp) }}</span>
            </div>
          </div>
        </div>

        <!-- 性能监控 -->
        <div class="info-section">
          <div
            class="section-title"
            @click="performanceExpanded = !performanceExpanded"
          >
            <span>性能监控</span>
            <DownOutlined v-if="performanceExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>

          <div v-show="performanceExpanded" class="section-content">
            <!-- CPU -->
            <div class="metric-item">
              <div class="metric-row">
                <span class="metric-label">CPU</span>
                <a-progress
                  :percent="device.cpu_info?.usage_percent"
                  :show-info="false"
                  :stroke-color="
                    getProgressColor(device.cpu_info?.usage_percent)
                  "
                  class="metric-progress"
                />
                <span class="metric-value"
                  >{{ device.cpu_info?.usage_percent }}%</span
                >
              </div>
              <div class="metric-detail">
                {{ device.cpu_info?.physical_cores }} 核心 ({{
                  device.cpu_info?.cores
                }}
                逻辑处理器) @ {{ device.cpu_info?.current_frequency }} MHz
              </div>
            </div>

            <!-- 内存 -->
            <div class="metric-item">
              <div class="metric-row">
                <span class="metric-label">内存</span>
                <a-progress
                  :percent="device.memory_info?.percentage"
                  :show-info="false"
                  :stroke-color="
                    getProgressColor(device.memory_info?.percentage)
                  "
                  class="metric-progress"
                />
                <span class="metric-value"
                  >{{ device.memory_info?.percentage }}%</span
                >
              </div>
              <div class="metric-detail">
                {{ formatBytes(device.memory_info?.used) }} /
                {{ formatBytes(device.memory_info?.total) }}
              </div>
            </div>

            <!-- 磁盘 -->
            <div class="metric-item">
              <div class="metric-row">
                <span class="metric-label">磁盘</span>
                <a-progress
                  :percent="device.disk_info?.percentage"
                  :show-info="false"
                  :stroke-color="getProgressColor(device.disk_info?.percentage)"
                  class="metric-progress"
                />
                <span class="metric-value"
                  >{{ device.disk_info?.percentage?.toFixed(1) }}%</span
                >
              </div>
              <div class="metric-detail">
                {{ formatBytes(device.disk_info?.used) }} /
                {{ formatBytes(device.disk_info?.total) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 网络接口 -->
        <div class="info-section">
          <div
            class="section-title"
            @click="networkExpanded = !networkExpanded"
          >
            <span>网络接口 ({{ networkInterfaces.length }})</span>
            <DownOutlined v-if="networkExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>
          <div v-show="networkExpanded" class="section-content">
            <div class="network-list">
              <div
                class="network-item"
                v-for="(network, idx) in networkInterfaces"
                :key="idx"
              >
                <div class="network-header">
                  <span class="network-name">{{ network.name }}</span>
                  <span class="network-ip">{{ network.ip_address }}</span>
                </div>
                <div class="network-speeds">
                  <div class="speed-item upload">
                    <span class="speed-icon">⬆</span>
                    <span class="speed-value">{{
                      formatSpeed(network.upload_rate)
                    }}</span>
                  </div>
                  <div class="speed-item download">
                    <span class="speed-icon">⬇</span>
                    <span class="speed-value">{{
                      formatSpeed(network.download_rate)
                    }}</span>
                  </div>
                  <div
                    class="network-extra"
                    v-if="network.mac_address || network.gateway"
                  >
                    <span v-if="network.mac_address" class="extra-info"
                      >MAC: {{ network.mac_address }}</span
                    >
                    <span v-if="network.gateway" class="extra-info"
                      >网关: {{ network.gateway }}</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 磁盘分区 -->
        <div class="info-section" v-if="device.disk_info?.partitions?.length">
          <div
            class="section-title"
            @click="partitionExpanded = !partitionExpanded"
          >
            <span>磁盘分区 ({{ device.disk_info.partitions.length }})</span>
            <DownOutlined v-if="partitionExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>
          <div v-show="partitionExpanded" class="section-content">
            <div class="partition-list">
              <div
                class="partition-item"
                v-for="(partition, idx) in device.disk_info.partitions"
                :key="idx"
              >
                <div class="partition-header">
                  <span
                    class="partition-name truncate"
                    :title="partition.device"
                    >{{ partition.device }}</span
                  >
                  <a-progress
                    :percent="partition.percentage"
                    :show-info="false"
                    :stroke-color="getProgressColor(partition.percentage)"
                    size="small"
                    class="partition-progress"
                  />
                  <span class="partition-usage"
                    >{{ partition.percentage }}%</span
                  >
                </div>
                <div class="partition-detail">
                  {{ formatBytes(partition.used) }} /
                  {{ formatBytes(partition.total) }} ({{
                    partition.file_system
                  }})
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="info-section select-none">
          <div class="section-title">统计信息</div>
          <div class="stats-grid">
            <div class="stat-card clickable" @click="showServicesDetail">
              <div class="stat-value">{{ filteredServices.length || 0 }}</div>
              <div class="stat-label">服务数</div>
            </div>
            <div class="stat-card clickable" @click="showProcessesDetail">
              <div class="stat-value">{{ filteredProcesses.length || 0 }}</div>
              <div class="stat-label">进程数</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 服务详情弹窗 -->
    <div
      v-if="servicesDetailVisible"
      ref="servicesDetailRef"
      class="detail-expansion-popup"
      :class="servicesDetailPlacement"
      :style="{
        left: servicesDetailPosition.x + 'px',
        top: servicesDetailPosition.y + 'px'
      }"
      @click.stop
    >
      <div class="popup-header">
        <h4 class="popup-title">服务列表 ({{ filteredServices.length }})</h4>
        <a-input
          v-model:value="servicesSearchKeyword"
          placeholder="搜索协议、地址、状态或进程名..."
          allow-clear
          size="small"
          class="search-input"
        >
          <template #prefix>
            <SearchOutlined />
          </template>
        </a-input>
      </div>
      <div class="popup-body">
        <div v-if="filteredServices.length === 0" class="empty-state">
          <span v-if="servicesSearchKeyword">没有找到匹配的服务</span>
          <span v-else>暂无服务数据</span>
        </div>
        <div v-else class="list-content" style="height: 412px">
          <VList
            class="scroller h-full"
            :data="filteredServices"
            #default="{ item, index }"
          >
            <div
              class="list-item service-item"
              style="height: 60px; margin: 6px 0"
              :key="index"
            >
              <div class="item-header layout-side">
                <div class="layout-left-center">
                  <span class="protocol-tag">{{ item.protocol }}</span>
                  <span class="item-address layout-left-center">{{
                    item.local_address
                  }}</span>
                </div>
                <span :class="['status-tag', item.status?.toLowerCase()]">{{
                  formatServiceStatus(item.status)
                }}</span>
              </div>
              <div class="item-meta">
                <span class="item-pid"
                  >PID: {{ item.pid }} {{ item.process_name }}</span
                >
              </div>
            </div>
          </VList>
        </div>
      </div>
    </div>

    <!-- 进程详情弹窗 -->
    <div
      v-if="processesDetailVisible"
      ref="processesDetailRef"
      class="detail-expansion-popup"
      :class="processesDetailPlacement"
      :style="{
        left: processesDetailPosition.x + 'px',
        top: processesDetailPosition.y + 'px'
      }"
      @click.stop
    >
      <div class="popup-header">
        <h4 class="popup-title">进程列表 ({{ filteredProcesses.length }})</h4>
        <a-input
          v-model:value="processesSearchKeyword"
          placeholder="搜索进程名称、PID、用户名或状态..."
          allow-clear
          size="small"
          class="search-input"
        >
          <template #prefix>
            <SearchOutlined />
          </template>
        </a-input>
      </div>
      <div class="popup-body">
        <div v-if="filteredProcesses.length === 0" class="empty-state">
          <span v-if="processesSearchKeyword">没有找到匹配的进程</span>
          <span v-else>暂无进程数据</span>
        </div>
        <div v-else class="list-content" style="height: 412px">
          <VList
            class="scroller h-full"
            :data="filteredProcesses"
            #default="{ item, index }"
          >
            <div
              class="list-item process-item"
              style="margin: 3px 0"
              :key="index"
            >
              <div class="item-header">
                <span class="item-name">{{ item.name }}</span>
                <span :class="['status-tag', item.status?.toLowerCase()]">{{
                  formatProcessStatus(item.status, item)
                }}</span>
              </div>
              <div class="item-meta">
                <span class="item-pid"
                  >PID: {{ item.pid }}
                  {{ item.username }}
                </span>
              </div>
              <div
                class="item-stats"
                v-if="
                  item.cpu_percent !== undefined ||
                  item.memory_percent !== undefined
                "
              >
                <span
                  class="stat-item cpu"
                  v-if="item.cpu_percent !== undefined"
                >
                  <span class="stat-icon">⚡</span>
                  <span class="stat-label">CPU:</span>
                  <span class="stat-value"
                    >{{ formatPercent(item.cpu_percent) }}%</span
                  >
                </span>
                <span
                  class="stat-item memory"
                  v-if="item.memory_percent !== undefined"
                >
                  <span class="stat-icon">💾</span>
                  <span class="stat-label">内存:</span>
                  <span class="stat-value"
                    >{{ formatPercent(item.memory_percent) }}%</span
                  >
                </span>
              </div>
              <div
                class="item-ports"
                v-if="item.listening_ports && item.listening_ports.length > 0"
              >
                <span class="ports-label">监听端口:</span>
                <span class="ports-list">{{
                  formatListeningPorts(item.listening_ports)
                }}</span>
              </div>
            </div>
          </VList>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  watch,
  nextTick,
  onUnmounted,
  useTemplateRef,
  computed,
  ref,
  shallowRef
} from 'vue'
import { DownOutlined, UpOutlined, SearchOutlined } from '@ant-design/icons-vue'
import localforage from 'localforage'
import { VList } from 'virtua/vue'
import ResidentProcessApi from '@/common/api/residentProcess.js'

const statusMap = {
  running: '运行中',
  sleeping: '睡眠',
  'disk-sleep': '磁盘睡眠',
  stopped: '已停止',
  not_running: '未启动',
  'tracing-stop': '追踪停止',
  zombie: '僵尸进程',
  dead: '已终止',
  'wake-kill': '唤醒终止',
  waking: '唤醒中',
  idle: '空闲',
  locked: '已锁定',
  waiting: '等待中',
  suspended: '已挂起',
  parked: '已停泊'
}

// 展开/收起状态
const performanceExpanded = ref(true)
const networkExpanded = ref(true)
const partitionExpanded = ref(true)

// 优化：使用常量存储固定值，避免重复创建
const BYTES_UNITS = Object.freeze(['B/s', 'KB/s', 'MB/s', 'GB/s'])
const SIZE_UNITS = Object.freeze(['B', 'KB', 'MB', 'GB', 'TB'])
const BYTES_K = 1024
const LOG_K = Math.log(BYTES_K)

// Props定义
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  placement: {
    type: String,
    default: 'right',
    validator: (value) => ['right', 'left', 'top', 'bottom'].includes(value)
  },
  maxHeight: {
    type: Number,
    default: 600
  },
  arrowOffset: {
    type: Number,
    default: 0
  }
})
const list = defineModel()
const index = defineModel('index')

// Emits定义
const emit = defineEmits(['close'])

// 当前设备数据
const device = computed(() => {
  if (list.value && index.value > -1 && index.value < list.value.length) {
    console.log(list.value[index.value])
    return list.value[index.value]
  }
  return {}
})

// 设备ID（用于存储key）
const deviceId = computed(() => {
  return device.value.client_id || device.value.id || 'unknown'
})

// LocalForage 存储key
const STORAGE_KEY_PREFIX = 'device-popover-state-'

// 优化：存储防抖定时器
let saveStateDebounceTimer = null

// 加载设备的展开/收起状态
const loadDeviceState = async () => {
  if (!deviceId.value || deviceId.value === 'unknown') return

  try {
    const storageKey = STORAGE_KEY_PREFIX + deviceId.value
    const savedState = await localforage.getItem(storageKey)

    if (savedState) {
      performanceExpanded.value = savedState.performance ?? true
      networkExpanded.value = savedState.network ?? true
      partitionExpanded.value = savedState.partition ?? true
    }
  } catch (error) {
    console.warn('加载设备状态失败:', error)
  }
}

// 保存设备的展开/收起状态（优化：添加防抖）
const saveDeviceState = async () => {
  if (!deviceId.value || deviceId.value === 'unknown') return

  try {
    const storageKey = STORAGE_KEY_PREFIX + deviceId.value
    const state = {
      performance: performanceExpanded.value,
      network: networkExpanded.value,
      partition: partitionExpanded.value
    }

    await localforage.setItem(storageKey, state)
  } catch (error) {
    console.warn('保存设备状态失败:', error)
  }
}

// 防抖保存函数
const debouncedSaveDeviceState = () => {
  if (saveStateDebounceTimer) {
    clearTimeout(saveStateDebounceTimer)
  }
  saveStateDebounceTimer = setTimeout(() => {
    saveDeviceState()
  }, 300)
}

// 网络接口数据（按总速率降序排列）
const networkInterfaces = computed(() => {
  if (!device.value.networks) return []

  let interfaces = []

  // 如果是字符串，解析为JSON
  if (typeof device.value.networks === 'string') {
    try {
      interfaces = JSON.parse(device.value.networks)
    } catch (e) {
      console.warn('解析网络接口数据失败:', e)
      return []
    }
  } else if (Array.isArray(device.value.networks)) {
    // 如果已经是数组，直接使用
    interfaces = device.value.networks
  } else {
    return []
  }

  // 优化：按照上传+下载的总速率降序排列，使用一次遍历
  return interfaces.sort((a, b) => {
    const totalA = (a.upload_rate || 0) + (a.download_rate || 0)
    const totalB = (b.upload_rate || 0) + (b.download_rate || 0)
    return totalB - totalA
  })
})

// 格式化网络速率（优化：使用常量数组和数学计算）
const formatSpeed = (bytesPerSecond) => {
  if (!bytesPerSecond || bytesPerSecond === 0) return '0 B/s'

  const i = Math.floor(Math.log(bytesPerSecond) / LOG_K)
  return (
    (bytesPerSecond / Math.pow(BYTES_K, i)).toFixed(2) + ' ' + BYTES_UNITS[i]
  )
}

// 格式化字节大小（优化：使用常量数组和数学计算）
const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / LOG_K)
  return (bytes / Math.pow(BYTES_K, i)).toFixed(2) + ' ' + SIZE_UNITS[i]
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return timestamp
}

// 根据使用率获取进度条颜色（优化：直接返回，减少条件判断）
const getProgressColor = (percent) => {
  return percent < 60 ? '#52c41a' : percent < 80 ? '#faad14' : '#ff4d4f'
}

// 格式化百分比（处理超过100%的情况）
const formatPercent = (value) => {
  if (value === undefined || value === null) return '0.0'
  return Number(value).toFixed(1)
}

// 格式化监听端口（处理对象数组格式）
const formatListeningPorts = (ports) => {
  if (!ports || ports.length === 0) return ''

  // 如果是简单的端口号数组
  if (typeof ports[0] === 'number' || typeof ports[0] === 'string') {
    return ports.join(', ')
  }

  // 如果是对象数组 [{protocol: 'TCP', local_address: '127.0.0.1:8080'}, ...]
  if (typeof ports[0] === 'object' && ports[0].local_address) {
    return ports
      .map((port) => {
        // 提取端口号（从 '127.0.0.1:8080' 中提取 '8080'）
        const address = port.local_address || ''
        const parts = address.split(':')
        const portNum = parts[parts.length - 1] // 获取最后一部分（端口号）
        const protocol = port.protocol ? `${port.protocol}/` : ''
        return `${protocol}${portNum}`
      })
      .join(', ')
  }

  return ports.join(', ')
}

// 格式化进程状态为中文
const formatProcessStatus = (status, item) => {
  if (!status) return '未知'

  const lowerStatus = status.toLowerCase()
  if (item.name === 'mysqld.exe') {
    console.log(lowerStatus, item)
  }
  return statusMap[lowerStatus] || status
}

// 格式化服务状态为中文
const formatServiceStatus = (status) => {
  if (!status) return '未知'

  const statusMap = {
    listen: '监听中',
    listening: '监听中',
    established: '已建立',
    close_wait: '关闭等待',
    time_wait: '时间等待',
    syn_sent: '同步已发送',
    syn_recv: '同步接收',
    fin_wait1: '终止等待1',
    fin_wait2: '终止等待2',
    last_ack: '最后确认',
    closing: '关闭中',
    closed: '已关闭',
    none: '无',
    unknown: '未知'
  }

  const lowerStatus = status.toLowerCase()
  return statusMap[lowerStatus] || status
}

// Refs
const popoverRef = useTemplateRef('popoverRef')
const servicesDetailRef = useTemplateRef('servicesDetailRef')
const processesDetailRef = useTemplateRef('processesDetailRef')

// 服务和进程详情弹窗状态
const servicesDetailVisible = ref(false)
const processesDetailVisible = ref(false)
const servicesSearchKeyword = ref('')
const processesSearchKeyword = ref('')
const servicesDetailPosition = ref({ x: 0, y: 0 })
const processesDetailPosition = ref({ x: 0, y: 0 })
const servicesDetailPlacement = ref('popup-right')
const processesDetailPlacement = ref('popup-right')

// 服务列表
const servicesList = computed(() => {
  if (!device.value.services) return []
  if (Array.isArray(device.value.services)) return device.value.services
  if (typeof device.value.services === 'string') {
    try {
      return JSON.parse(device.value.services)
    } catch (e) {
      console.warn('解析服务数据失败:', e)
      return []
    }
  }
  return []
})

// 进程列表
const processesList = computed(() => {
  if (!device.value.processes) return []
  if (Array.isArray(device.value.processes)) return device.value.processes
  if (typeof device.value.processes === 'string') {
    try {
      return JSON.parse(device.value.processes)
    } catch (e) {
      console.warn('解析进程数据失败:', e)
      return []
    }
  }
  return []
})

// 常驻进程与合并展示处理
const residentProcesses = ref([])
const residentLoading = ref(false)
const residentError = ref(null)

const fetchResidentProcesses = async () => {
  residentLoading.value = true
  residentError.value = null
  try {
    const id = deviceId.value
    if (!id || id === 'unknown') {
      residentProcesses.value = []
    } else {
      const resp = await ResidentProcessApi.getResidentProcessList(id)
      const data = resp?.data?.data ?? resp?.data ?? []
      residentProcesses.value = Array.isArray(data) ? data : []
    }
  } catch (e) {
    console.warn('加载常驻进程失败:', e)
    residentError.value = e?.message || String(e)
    residentProcesses.value = []
  } finally {
    residentLoading.value = false
  }
}

const displayProcesses = computed(() => {
  const running = Array.isArray(processesList.value) ? processesList.value : []

  const residentNames = new Set(
    (residentProcesses.value || []).map((p) => (p.name || '').toLowerCase())
  )

  const runningAugmented = running.map((proc) => {
    const lower = (proc.name || '').toLowerCase()
    return { ...proc, isResident: residentNames.has(lower), isStarted: true }
  })

  const missingResident = []
  residentNames.forEach((name) => {
    const found = runningAugmented.some(
      (p) => (p.name || '').toLowerCase() === name
    )
    if (!found) {
      missingResident.push({
        name,
        pid: '',
        username: '',
        status: 'not_running',
        cpu_percent: 0,
        memory_percent: 0,
        listening_ports: [],
        isResident: true,
        isStarted: false
      })
    }
  })

  const merged = [...missingResident, ...runningAugmented]

  merged.sort((a, b) => {
    const ar = a.isResident ? 1 : 0
    const br = b.isResident ? 1 : 0
    if (ar !== br) return br - ar
    const as = a.isStarted ? 1 : 0
    const bs = b.isStarted ? 1 : 0
    if (as !== bs) return bs - as
    return (a.name || '').localeCompare(b.name || '')
  })

  return merged
})

// 过滤后的服务列表
const filteredServices = computed(() => {
  if (!servicesSearchKeyword.value) return servicesList.value

  const keyword = servicesSearchKeyword.value.toLowerCase()
  return servicesList.value.filter((service) => {
    const protocol = (service.protocol || '').toLowerCase()
    const localAddress = (service.local_address || '').toLowerCase()
    const status = (service.status || '').toLowerCase()
    const processName = (service.process_name || '').toLowerCase()
    const pid = String(service.pid || '')

    return (
      protocol.includes(keyword) ||
      localAddress.includes(keyword) ||
      status.includes(keyword) ||
      processName.includes(keyword) ||
      pid.includes(keyword)
    )
  })
})

// 过滤后的进程列表（基于合并展示列表）
const filteredProcesses = computed(() => {
  if (!processesSearchKeyword.value) return displayProcesses.value

  const keyword = processesSearchKeyword.value.toLowerCase()
  return displayProcesses.value.filter((process) => {
    const name = (process.name || '').toLowerCase()
    const pid = String(process.pid || '')
    const status = (process.status || '').toLowerCase()
    const username = (process.username || '').toLowerCase()

    return (
      name.includes(keyword) ||
      pid.includes(keyword) ||
      status.includes(keyword) ||
      username.includes(keyword)
    )
  })
})

// 显示服务详情
const showServicesDetail = (event) => {
  event.stopPropagation()

  // 如果已经显示，则关闭
  if (servicesDetailVisible.value) {
    servicesDetailVisible.value = false
    return
  }

  // 关闭进程详情
  processesDetailVisible.value = false

  // 计算弹窗位置
  const popoverElement = popoverRef.value
  if (!popoverElement) return

  const popoverRect = popoverElement.getBoundingClientRect()
  const targetRect = event.currentTarget.getBoundingClientRect()

  // 计算相对于 popover 的位置
  const relativeX = targetRect.left - popoverRect.left
  const relativeY = targetRect.top - popoverRect.top

  // 预估弹窗高度（根据实际内容可能会变化）
  const estimatedPopupHeight = 400
  const targetCenterY = relativeY + targetRect.height / 2

  // 判断弹出方向：优先在正上方或正下方
  // 检查下方空间
  const spaceBelow = popoverRect.height - (relativeY + targetRect.height)
  // 检查上方空间
  const spaceAbove = relativeY

  if (spaceBelow >= estimatedPopupHeight) {
    // 下方空间足够，在正下方弹出
    servicesDetailPlacement.value = 'popup-bottom'
    servicesDetailPosition.value = {
      x: relativeX + targetRect.width / 2, // 水平居中对齐
      y: relativeY + targetRect.height + 8 // 下方留8px间距
    }
  } else if (spaceAbove >= estimatedPopupHeight) {
    // 上方空间足够，在正上方弹出
    servicesDetailPlacement.value = 'popup-top'
    servicesDetailPosition.value = {
      x: relativeX + targetRect.width / 2, // 水平居中对齐
      y: relativeY - 8 // 上方留8px间距
    }
  } else {
    // 上下空间都不足，选择空间较大的一侧
    if (spaceBelow >= spaceAbove) {
      servicesDetailPlacement.value = 'popup-bottom'
      servicesDetailPosition.value = {
        x: relativeX + targetRect.width / 2,
        y: relativeY + targetRect.height + 8
      }
    } else {
      servicesDetailPlacement.value = 'popup-top'
      servicesDetailPosition.value = {
        x: relativeX + targetRect.width / 2,
        y: relativeY - 8
      }
    }
  }

  servicesSearchKeyword.value = ''
  servicesDetailVisible.value = true
}

// 显示进程详情
const showProcessesDetail = (event) => {
  event.stopPropagation()

  // 如果已经显示，则关闭
  if (processesDetailVisible.value) {
    processesDetailVisible.value = false
    return
  }

  // 关闭服务详情
  servicesDetailVisible.value = false

  // 计算弹窗位置
  const popoverElement = popoverRef.value
  if (!popoverElement) return

  const popoverRect = popoverElement.getBoundingClientRect()
  const targetRect = event.currentTarget.getBoundingClientRect()

  // 计算相对于 popover 的位置
  const relativeX = targetRect.left - popoverRect.left
  const relativeY = targetRect.top - popoverRect.top

  // 预估弹窗高度
  const estimatedPopupHeight = 400
  const targetCenterY = relativeY + targetRect.height / 2

  // 判断弹出方向：优先在正上方或正下方
  const spaceBelow = popoverRect.height - (relativeY + targetRect.height)
  const spaceAbove = relativeY

  if (spaceBelow >= estimatedPopupHeight) {
    // 下方空间足够，在正下方弹出
    processesDetailPlacement.value = 'popup-bottom'
    processesDetailPosition.value = {
      x: relativeX + targetRect.width / 2, // 水平居中对齐
      y: relativeY + targetRect.height + 8 // 下方留8px间距
    }
  } else if (spaceAbove >= estimatedPopupHeight) {
    // 上方空间足够，在正上方弹出
    processesDetailPlacement.value = 'popup-top'
    processesDetailPosition.value = {
      x: relativeX + targetRect.width / 2, // 水平居中对齐
      y: relativeY - 8 // 上方留8px间距
    }
  } else {
    // 上下空间都不足，选择空间较大的一侧
    if (spaceBelow >= spaceAbove) {
      processesDetailPlacement.value = 'popup-bottom'
      processesDetailPosition.value = {
        x: relativeX + targetRect.width / 2,
        y: relativeY + targetRect.height + 8
      }
    } else {
      processesDetailPlacement.value = 'popup-top'
      processesDetailPosition.value = {
        x: relativeX + targetRect.width / 2,
        y: relativeY - 8
      }
    }
  }

  processesSearchKeyword.value = ''
  processesDetailVisible.value = true
  fetchResidentProcesses()
}

// 优化：使用事件委托和防抖处理点击事件
let clickDebounceTimer = null

// 处理全局点击事件，点击外部关闭 Popover
const handleClickOutside = (event) => {
  // 如果 Popover 未显示，直接返回
  if (!props.visible) return

  // 检查点击是否在 Popover 内部
  const popoverElement = popoverRef.value
  if (popoverElement && popoverElement.contains(event.target)) {
    return
  }

  // 检查点击是否在服务详情弹窗内部
  const servicesDetailElement = servicesDetailRef.value
  if (servicesDetailElement && servicesDetailElement.contains(event.target)) {
    return
  }

  // 检查点击是否在进程详情弹窗内部
  const processesDetailElement = processesDetailRef.value
  if (processesDetailElement && processesDetailElement.contains(event.target)) {
    return
  }

  // 点击在所有弹窗外部，关闭所有弹窗
  servicesDetailVisible.value = false
  processesDetailVisible.value = false
  emit('close')
}

// 监听visible变化，动态添加/移除全局点击监听（优化：添加防抖）
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      // 加载设备状态
      loadDeviceState()

      // 使用 nextTick 确保 Popover 渲染完成后再添加全局监听
      nextTick(() => {
        // 移除旧的监听器
        document.removeEventListener('click', handleClickOutside)
        // 延迟添加新的监听器，防止当前点击立即触发关闭
        if (clickDebounceTimer) clearTimeout(clickDebounceTimer)
        clickDebounceTimer = setTimeout(() => {
          document.addEventListener('click', handleClickOutside)
        }, 100)
      })
    } else {
      // Popover关闭时移除监听器
      document.removeEventListener('click', handleClickOutside)
      if (clickDebounceTimer) {
        clearTimeout(clickDebounceTimer)
        clickDebounceTimer = null
      }
    }
  }
)

// 监听展开/收起状态变化，保存到 LocalForage（优化：使用防抖）
watch([performanceExpanded, networkExpanded, partitionExpanded], () => {
  if (props.visible) {
    debouncedSaveDeviceState()
  }
})

// 组件卸载时清理（优化：清理定时器）
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)

  // 清理防抖定时器
  if (saveStateDebounceTimer) {
    clearTimeout(saveStateDebounceTimer)
    saveStateDebounceTimer = null
  }
})
</script>

<style lang="less" scoped>
@import './stytle.less';
</style>
