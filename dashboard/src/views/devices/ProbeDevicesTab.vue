<template>
  <div class="size-full">
    <div class="mb-[12px] layout-side">
      <div>
        <span class="mr-2 font-medium">IP地址:</span>
        <a-input
          v-model:value="filterIP"
          placeholder="请输入IP地址"
          style="width: 200px; margin-right: 12px"
        />
        <span class="mr-2 font-medium">设备类型:</span>
        <a-select
          v-model:value="filterType"
          style="width: 100px; margin-right: 12px"
          allow-clear
        >
          <a-select-option value="">全部类型</a-select-option>
          <a-select-option value="台式机">台式机</a-select-option>
          <a-select-option value="笔记本">笔记本</a-select-option>
          <a-select-option value="服务器">服务器</a-select-option>
          <a-select-option value="__unset__">未知</a-select-option>
          <a-select-option value="其他">其他</a-select-option>
        </a-select>

        <span class="mr-2 font-medium">操作系统:</span>
        <a-select
          v-model:value="filterOS"
          style="width: 100px; margin-right: 12px"
          allow-clear
        >
          <a-select-option value="">全部系统</a-select-option>
          <a-select-option value="Windows">Windows</a-select-option>
          <a-select-option value="Linux">Linux</a-select-option>
        </a-select>

        <span class="mr-2 font-medium">状态:</span>
        <a-select
          v-model:value="filterStatus"
          style="width: 80px; margin-right: 12px"
          allow-clear
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="online">在线</a-select-option>
          <a-select-option value="offline">离线</a-select-option>
        </a-select>
        <a-button @click="clearFilter">重置</a-button>
      </div>
      <!-- <a-button class="layout-center" type="primary" @click="openCreateModal">
        <template #icon>
          <PlusOutlined />
        </template>
        添加设备
      </a-button> -->
    </div>
    <!-- 设备列表 -->
    <div class="w-full h-[calc(100%-44px)] overflow-auto">
      <a-table
        :columns="columns"
        :data-source="filteredDevices"
        :pagination="pagination"
        :loading="loading"
        size="small"
        row-key="id"
        bordered
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record, index }">
          <template v-if="column.dataIndex === 'hostname'">
            {{ record.hostname || '未知设备' }}
          </template>
          <template v-else-if="column.dataIndex === 'ip_address'">
            {{ record.ip_address || '未知' }}
          </template>
          <template v-else-if="column.dataIndex === 'id'">
            {{ record.id || '未知' }}
          </template>
          <template v-else-if="column.dataIndex === 'machine_type'">
            {{ formatMachineType(record.machine_type) }}
          </template>
          <template v-else-if="column.dataIndex === 'type'">
            <div class="flex items-center justify-center">
              <a-tooltip
                v-if="record.type && getDeviceIcon(record.type)"
                :title="record.type"
              >
                <div
                  v-html="getDeviceIcon(record.type)"
                  class="device-icon"
                  style="width: 32px; height: 32px; cursor: help"
                ></div>
              </a-tooltip>
              <span v-else>{{ record.type || '未设置' }}</span>
            </div>
          </template>
          <template v-else-if="column.dataIndex === 'online'">
            <a-tag :color="record.online ? 'green' : 'red'" style="margin: 0">
              {{ record.online ? '在线' : '离线' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <EditOutlined
              @click="openEditModal(record)"
              style="font-size: 16px; color: #1677ff"
              class="cursor-pointer"
            />
            <a-popconfirm
              placement="topRight"
              title="确定要删除这个设备吗？"
              @confirm="deleteDevice(record.id)"
              ok-text="确定"
              cancel-text="取消"
            >
              <DeleteOutlined
                style="font-size: 16px; color: red"
                class="cursor-pointer ml-2"
              />
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 创建/编辑设备模态框 -->
    <DeviceAddModal
      v-model:visible="showModal"
      :is-editing="isEditing"
      :device-data="currentDevice"
      @ok="saveDevice"
      @cancel="closeModal"
    />

    <!-- 服务详情模态框 -->
    <ServiceDetailModal
      v-model:visible="showServicesModal"
      :services-list="servicesList"
      :device-name="currentDeviceName"
      @cancel="closeServicesModal"
    />

    <!-- 进程详情模态框 -->
    <ProcessDetailModal
      v-model:visible="showProcessesModal"
      :processes-list="processesList"
      :device-name="currentDeviceName"
      @cancel="closeProcessesModal"
    />

    <!-- 网口详情模态框 -->
    <a-modal
      v-model:open="showNetworksModal"
      :title="`网口详情 - ${currentDeviceName}`"
      @cancel="closeNetworksModal"
      width="80%"
    >
      <a-table
        :dataSource="networksList"
        :columns="networkColumns"
        :pagination="false"
        bordered
        size="small"
      />
      <template #footer>
        <a-button @click="closeNetworksModal">关闭</a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef } from 'vue'
import { DeleteOutlined, EditOutlined } from '@ant-design/icons-vue'
import { formatMachineType } from '@/common/utils/Utils.js'
import { message, Tooltip } from 'ant-design-vue'
import { h } from 'vue'
import DeviceAddModal from '@/components/devices/DeviceAddModal.vue'
import ServiceDetailModal from '@/components/devices/ServiceDetailModal.vue'
import ProcessDetailModal from '@/components/devices/ProcessDetailModal.vue'
import DeviceApi from '@/common/api/device.js'
import { wsCode } from '@/common/ws/Ws.js'
import { PubSub } from '@/common/utils/PubSub.js'

// 导入设备类型SVG图标
import PCIcon from '@/assets/svg/TopologyPC.svg?raw'
import LaptopIcon from '@/assets/svg/TopologyLaptop.svg?raw'
import ServerIcon from '@/assets/svg/TopologyServer.svg?raw'
import PrinterIcon from '@/assets/svg/TopologyPrinter.svg?raw'
import FirewallIcon from '@/assets/svg/TopologyFireWall.svg?raw'
import RouterIcon from '@/assets/svg/TopologyRouter.svg?raw'
import SwitchIcon from '@/assets/svg/TopologySwitches.svg?raw'

// 常量定义
const ANIMATION_DURATION = 3000 // 动画持续时间
const CHANGE_KEYS = [
  'timestamp',
  'cpu_usage',
  'memory_usage',
  'disk_usage',
  'services_count',
  'processes_count'
] // 需要监听变化的字段

// 设备类型图标映射
const DEVICE_ICON_MAP = {
  台式机: PCIcon,
  笔记本: LaptopIcon,
  服务器: ServerIcon,
  打印机: PrinterIcon,
  防火墙: FirewallIcon,
  路由器: RouterIcon,
  交换机: SwitchIcon
}

/**
 * 获取设备类型对应的SVG图标
 * @param {string} type - 设备类型
 * @returns {string} SVG字符串
 */
const getDeviceIcon = (type) => {
  const icon = DEVICE_ICON_MAP[type]
  if (!icon) return null

  // 解析SVG并设置颜色
  const parser = new DOMParser()
  const svgDoc = parser.parseFromString(icon, 'image/svg+xml')
  const svgElement = svgDoc.documentElement

  // 移除宽度和高度属性，让CSS控制
  svgElement.removeAttribute('width')
  svgElement.removeAttribute('height')
  svgElement.setAttribute(
    'viewBox',
    svgElement.getAttribute('viewBox') || '0 0 1024 1024'
  )

  return new XMLSerializer().serializeToString(svgElement)
}

// 定义组件属性
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: () => ({})
  }
})

// 使用 defineModel 替代 changedTimestamps prop
const changedTimestamps = defineModel('changedTimestamps', {
  type: Object,
  default: () => ({})
})

// 定义组件事件
const emit = defineEmits([
  'update:loading',
  'handleTableChange',
  'handleShowServices',
  'handleShowProcesses',
  'handleShowNetworks',
  'clearFilter'
])
// 设备数据使用 shallowRef 优化大数组性能
const devices = shallowRef([])

// 模态框相关
const showModal = ref(false)
const isEditing = ref(false)
const currentDevice = ref(null)

// 详情模态框相关
const showServicesModal = ref(false)
const showProcessesModal = ref(false)
const showNetworksModal = ref(false)
const servicesList = shallowRef([])
const processesList = shallowRef([])
const networksList = shallowRef([])
const currentDeviceName = ref('')

// 定时器管理 - 用于清理
const animationTimers = new Map()

// 网口表格列定义
const networkColumns = [
  {
    title: '接口名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'IP地址',
    dataIndex: 'ip_address',
    key: 'ip_address'
  },
  {
    title: 'MAC地址',
    dataIndex: 'mac_address',
    key: 'mac_address',
    customRender: ({ text }) => {
      return text || '无'
    }
  },
  {
    title: '网关',
    dataIndex: 'gateway',
    key: 'gateway',
    customRender: ({ text }) => {
      return text || '无'
    }
  },
  {
    title: '子网掩码',
    dataIndex: 'netmask',
    key: 'netmask',
    customRender: ({ text }) => {
      return text || '无'
    }
  },
  {
    title: '上传速率',
    dataIndex: 'upload_rate',
    key: 'upload_rate',
    customRender: ({ text }) => formatNetworkRate(text)
  },
  {
    title: '下载速率',
    dataIndex: 'download_rate',
    key: 'download_rate',
    customRender: ({ text }) => formatNetworkRate(text)
  }
]

// 表格列定义
const columns = [
  {
    title: '序号',
    dataIndex: 'index',
    align: 'center',
    key: 'index',
    width: 44,
    customRender: ({ text, index }) => {
      return index + 1
    }
  },
  {
    title: '类型',
    dataIndex: 'type',
    align: 'center',
    key: 'type',
    width: 60
  },
  {
    title: '设备名称',
    dataIndex: 'hostname',
    align: 'center',
    key: 'hostname'
  },
  {
    title: '设备别名',
    dataIndex: 'alias',
    align: 'center',
    key: 'alias',
    customRender: ({ text }) => {
      if (!text || text.length === 0) {
        return '无'
      }
      return text
    }
  },
  {
    title: '设备地址',
    dataIndex: 'ips',
    align: 'center',
    key: 'ips',
    customRender: ({ text }) => {
      if (!text || !Array.isArray(text) || text.length === 0) {
        return '无'
      }
      // 如果只有一个IP地址，直接显示
      if (text.length === 1) {
        return text[0].split(':')[1]
      }
      // 如果有多个IP地址，显示第一个并提示还有更多，Tooltip中也一行显示一个IP
      return h('div', [
        h('span', text[0].split(':')[1]),
        h(
          Tooltip,
          {
            title: h(
              'div',
              {
                style: {
                  textAlign: 'left'
                }
              },
              text.map((ip) => h('div', ip))
            )
          },
          {
            default: () =>
              h(
                'span',
                {
                  style: {
                    color: '#1890ff',
                    marginLeft: '5px',
                    cursor: 'pointer'
                  }
                },
                `(+${text.length - 1})`
              )
          }
        )
      ])
    }
  },
  {
    title: '操作系统',
    dataIndex: 'os_name',
    align: 'center',
    key: 'os_name',
    width: 80
  },
  {
    title: '系统版本',
    dataIndex: 'os_version',
    align: 'center',
    key: 'os_version'
  },
  {
    title: '系统架构',
    dataIndex: 'os_architecture',
    align: 'center',
    key: 'os_architecture',
    width: 80
  },
  {
    title: '硬件架构',
    dataIndex: 'machine_type',
    align: 'center',
    key: 'machine_type',
    width: 80
  },
  {
    title: 'CPU使用率',
    dataIndex: 'cpu_usage',
    align: 'center',
    key: 'cpu_usage',
    width: 86,
    customRender: ({ record }) => {
      const displayValue = !record.online
        ? '0%'
        : record.cpu_info?.usage_percent != null
        ? `${record.cpu_info.usage_percent}%`
        : '未知'
      return createTextAnimationRenderer(displayValue, 'cpu_usage', record.id)
    }
  },
  {
    title: '内存使用率',
    dataIndex: 'memory_usage',
    align: 'center',
    key: 'memory_usage',
    width: 86,
    customRender: ({ record }) => {
      const displayValue = !record.online
        ? '0%'
        : record.memory_info?.percentage != null
        ? `${record.memory_info.percentage}%`
        : '未知'
      return createTextAnimationRenderer(
        displayValue,
        'memory_usage',
        record.id
      )
    }
  },
  {
    title: '磁盘使用率',
    dataIndex: 'disk_usage',
    align: 'center',
    key: 'disk_usage',
    width: 86,
    customRender: ({ record }) => {
      const displayValue = !record.online
        ? '0%'
        : record.disk_info?.percentage != null
        ? `${record.disk_info.percentage}%`
        : '未知'
      return createTextAnimationRenderer(displayValue, 'disk_usage', record.id)
    }
  },
  {
    title: '服务数量',
    dataIndex: 'services_count',
    align: 'center',
    key: 'services_count',
    width: 70,
    customRender: ({ text, record }) => {
      return createClickableRenderer(
        record.services_count,
        record.online,
        () => handleShowServices(record),
        'services_count',
        record.id
      )
    }
  },
  {
    title: '进程数量',
    dataIndex: 'processes_count',
    align: 'center',
    key: 'processes_count',
    width: 70,
    customRender: ({ text, record }) => {
      return createClickableRenderer(
        record.processes_count,
        record.online,
        () => handleShowProcesses(record),
        'processes_count',
        record.id
      )
    }
  },
  {
    title: '网口数量',
    dataIndex: 'networks_count',
    align: 'center',
    key: 'networks_count',
    width: 70,
    customRender: ({ text, record }) => {
      return h(
        'a',
        {
          onClick: () => {
            if (record.networks_count > 0 && record.online) {
              handleShowNetworks(record)
            }
          },
          style: {
            color:
              record.networks_count > 0 && record.online
                ? '#1890ff'
                : '#00000040',
            cursor:
              record.networks_count > 0 && record.online
                ? 'pointer'
                : 'not-allowed'
          }
        },
        record.networks_count > 0 && record.online ? text : 0
      )
    }
  },
  {
    title: '状态',
    dataIndex: 'online',
    align: 'center',
    key: 'online',
    width: 60
  },
  {
    title: '上报时间',
    dataIndex: 'timestamp',
    align: 'center',
    key: 'timestamp',
    width: 136,
    customRender: ({ text, record }) => {
      return createTextAnimationRenderer(text, 'timestamp', record.id)
    }
  },
  {
    title: '操作',
    dataIndex: 'action',
    align: 'center',
    key: 'action',
    width: 60
  }
]

// 格式化网络速率显示（优化性能）
const formatNetworkRate = (rate) => {
  if (rate == null) return '未知'
  if (rate < 1000) return `${rate} Kbps`
  if (rate < 1000000) return `${(rate / 1000).toFixed(2)} Mbps`
  return `${(rate / 1000000).toFixed(2)} Gbps`
}

// 创建动画处理器 - 提取公共逻辑
const createAnimationHandler = (key) => {
  return () => {
    if (changedTimestamps.value[key]) {
      changedTimestamps.value = { ...changedTimestamps.value, [key]: false }
    }
  }
}

// 创建可点击元素渲染器 - 复用逻辑
const createClickableRenderer = (
  count,
  online,
  handler,
  fieldKey,
  deviceId
) => {
  const displayValue = count > 0 && online ? count : 0
  const key = `${fieldKey}-${deviceId}`
  const isChanged = changedTimestamps.value[key] || false

  return h(
    'a',
    {
      onClick: () => count > 0 && online && handler(),
      class: isChanged ? 'timestamp-changed' : '',
      style: {
        color: count > 0 && online ? '#1890ff' : '#00000040',
        cursor: count > 0 && online ? 'pointer' : 'not-allowed'
      },
      onAnimationEnd: createAnimationHandler(key)
    },
    displayValue
  )
}

// 创建文本动画渲染器 - 复用逻辑
const createTextAnimationRenderer = (displayValue, fieldKey, deviceId) => {
  const key = `${fieldKey}-${deviceId}`
  const isChanged = changedTimestamps.value[key] || false

  return h(
    'span',
    {
      class: isChanged ? 'timestamp-changed' : '',
      onAnimationEnd: createAnimationHandler(key)
    },
    displayValue
  )
}

// 筛选状态
const filterType = ref('')
const filterIP = ref('')
const filterOS = ref('')
const filterStatus = ref('')

const fetchDevices = async () => {
  try {
    const response = await DeviceApi.getDevicesList()
    devices.value = response?.data || []
  } catch (error) {
    console.error('获取设备列表失败:', error)
    message.error('获取设备列表失败')
  }
}

// 计算筛选后的设备列表
const filteredDevices = computed(() => {
  let filtered = devices.value

  // 设备类型筛选
  if (filterType.value) {
    // 特殊处理"未设置"类型
    if (filterType.value === '__unset__') {
      filtered = filtered.filter((device) => !device.type)
    } else {
      filtered = filtered.filter((device) => device.type === filterType.value)
    }
  }

  // IP地址模糊匹配筛选
  if (filterIP.value) {
    filtered = filtered.filter((device) => {
      if (!device.ips || !Array.isArray(device.ips)) {
        return false
      }
      // 检查所有IP地址是否包含输入的IP片段
      return device.ips.some((ip) => {
        // ip格式为 "接口名: IP地址"，我们只检查IP地址部分
        const ipAddress = ip.split(': ')[1] || ip
        return ipAddress && ipAddress.includes(filterIP.value)
      })
    })
  }

  // 操作系统筛选
  if (filterOS.value) {
    if (filterOS.value === '__unset__') {
      // 筛选未设置操作系统的设备
      filtered = filtered.filter(
        (device) =>
          !device.os_name ||
          device.os_name === 'N/A' ||
          device.os_name === '未知'
      )
    } else {
      // 筛选指定操作系统的设备
      filtered = filtered.filter((device) => {
        if (!device.os_name) return false
        // 不区分大小写匹配
        return device.os_name
          .toLowerCase()
          .includes(filterOS.value.toLowerCase())
      })
    }
  }

  // 状态筛选
  if (filterStatus.value) {
    if (filterStatus.value === 'online') {
      filtered = filtered.filter((device) => device.online === true)
    } else if (filterStatus.value === 'offline') {
      filtered = filtered.filter((device) => device.online === false)
    }
  }

  return filtered
})

// 清除筛选
const clearFilter = () => {
  filterType.value = ''
  filterIP.value = ''
  filterOS.value = ''
  filterStatus.value = ''
  emit('clearFilter')
}

// 打开创建设备模态框
const openCreateModal = () => {
  isEditing.value = false
  currentDevice.value = null
  showModal.value = true
}

// 打开编辑设备模态框
const openEditModal = (device) => {
  isEditing.value = true
  currentDevice.value = { ...device }
  showModal.value = true
}

// 删除设备
const deleteDevice = async (id) => {
  try {
    const response = await DeviceApi.deleteDevice({ id })
    if (response.status === 'success') {
      message.success('设备删除成功')
      fetchDevices()
    } else {
      message.error('设备删除失败: ' + response.message)
    }
  } catch (error) {
    console.error('删除设备失败:', error)
    message.error('删除设备失败: ' + error.message)
  }
}

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  emit('handleTableChange', pag, filters, sorter)
}

// 通用排序函数 - 按PID排序
const sortByPid = (list) => {
  return [...list].sort((a, b) => {
    if (a.pid == null && b.pid == null) return 0
    if (a.pid == null) return 1
    if (b.pid == null) return -1
    return a.pid - b.pid
  })
}

// 显示服务详情
const handleShowServices = async (record) => {
  try {
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response?.data?.services) {
      servicesList.value = sortByPid(response.data.services)
      currentDeviceName.value = record.hostname || record.id
      showServicesModal.value = true
    }
  } catch (error) {
    console.error('获取服务详情失败:', error)
    message.error('获取服务详情失败')
  }
}

// 显示进程详情
const handleShowProcesses = async (record) => {
  try {
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response?.data?.processes) {
      processesList.value = sortByPid(response.data.processes)
      currentDeviceName.value = record.hostname || record.id
      showProcessesModal.value = true
    }
  } catch (error) {
    console.error('获取进程详情失败:', error)
    message.error('获取进程详情失败')
  }
}

// 关闭服务详情模态框
const closeServicesModal = () => {
  showServicesModal.value = false
}

// 关闭进程详情模态框
const closeProcessesModal = () => {
  showProcessesModal.value = false
}

// 显示网口详情
const handleShowNetworks = async (record) => {
  try {
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response?.data?.networks) {
      networksList.value = response.data.networks
      currentDeviceName.value = record.hostname || record.id
      showNetworksModal.value = true
    }
  } catch (error) {
    console.error('获取网口详情失败:', error)
    message.error('获取网口详情失败')
  }
}

// 关闭网口详情模态框
const closeNetworksModal = () => {
  showNetworksModal.value = false
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
}

// 保存设备（创建或更新）
const saveDevice = async (deviceData) => {
  try {
    if (isEditing.value) {
      // 更新设备
      const response = await DeviceApi.updateDevice(deviceData)
      if (response.status === 'success') {
        message.success('设备更新成功')
        closeModal()
        fetchDevices()
      } else {
        message.error('设备更新失败: ' + response.message)
      }
    } else {
      // 创建设备
      const response = await DeviceApi.createDevice(deviceData)
      if (response.status === 'success') {
        message.success('设备创建成功')
        closeModal()
        fetchDevices()
      } else {
        message.error('设备创建失败: ' + response.message)
      }
    }
  } catch (error) {
    console.error('保存设备失败:', error)
    message.error('保存设备失败: ' + error.message)
  }
}

// 清理所有动画定时器
const clearAllAnimationTimers = () => {
  animationTimers.forEach((timerId) => clearTimeout(timerId))
  animationTimers.clear()
}

// 设置动画定时器
const setAnimationTimer = (changeKey) => {
  // 清除旧的定时器
  if (animationTimers.has(changeKey)) {
    clearTimeout(animationTimers.get(changeKey))
  }

  // 设置新的定时器
  const timerId = setTimeout(() => {
    changedTimestamps.value = { ...changedTimestamps.value, [changeKey]: false }
    animationTimers.delete(changeKey)
  }, ANIMATION_DURATION)

  animationTimers.set(changeKey, timerId)
}

// 获取字段值的辅助函数
const getFieldValue = (device, key) => {
  switch (key) {
    case 'timestamp':
      return device.timestamp
    case 'cpu_usage':
      return device.cpu_info?.usage_percent
    case 'memory_usage':
      return device.memory_info?.percentage
    case 'disk_usage':
      return device.disk_info?.percentage
    case 'services_count':
      return device.services_count
    case 'processes_count':
      return device.processes_count
    default:
      return undefined
  }
}

// 处理设备信息更新
const handleDeviceInfoUpdate = (deviceInfo) => {
  const index = devices.value.findIndex((dev) => dev.id === deviceInfo.id)
  if (index === -1) return

  const oldDevice = devices.value[index]
  const newChangedTimestamps = { ...changedTimestamps.value }

  // 检查字段变化
  CHANGE_KEYS.forEach((key) => {
    const oldValue = getFieldValue(oldDevice, key)
    const newValue = getFieldValue(deviceInfo, key)

    // 严格检查值的变化
    if (oldValue !== newValue && newValue != null) {
      const changeKey = `${key}-${deviceInfo.id}`

      // 避免重复触发动画
      if (!newChangedTimestamps[changeKey]) {
        newChangedTimestamps[changeKey] = true
        setAnimationTimer(changeKey)
      }
    }
  })

  // 更新设备信息（使用浅拷贝优化性能）
  const updatedDevices = [...devices.value]
  updatedDevices[index] = { ...oldDevice, ...deviceInfo }
  devices.value = updatedDevices
  changedTimestamps.value = newChangedTimestamps
}

// 处理设备状态更新
const handleDeviceStatusUpdate = (data) => {
  const index = devices.value.findIndex(
    (dev) => dev.client_id === data.client_id
  )
  if (index === -1) return

  const updatedDevices = [...devices.value]
  updatedDevices[index] = {
    ...updatedDevices[index],
    online: data.status === 'online'
  }
  devices.value = updatedDevices
}

// 页面挂载时订阅设备信息和状态更新
onMounted(() => {
  fetchDevices()
  PubSub.subscribe(wsCode.DEVICE_INFO, handleDeviceInfoUpdate)
  PubSub.subscribe(wsCode.DEVICE_STATUS, handleDeviceStatusUpdate)
})

// 页面卸载时取消订阅并清理资源
onUnmounted(() => {
  PubSub.unsubscribe(wsCode.DEVICE_INFO)
  PubSub.unsubscribe(wsCode.DEVICE_STATUS)
  clearAllAnimationTimers() // 清理所有定时器
  changedTimestamps.value = {} // 清空变化标记
})
</script>

<style lang="less">
// 时间戳变更时的过渡色提示样式
.timestamp-changed {
  animation: highlightChange 3s ease-in-out;
}

@keyframes highlightChange {
  0% {
    background-color: rgba(255, 193, 7, 0.5); // 淡黄色背景
    color: #212529;
  }
  50% {
    background-color: rgba(40, 167, 69, 0.3); // 淡绿色背景
    color: #212529;
  }
  100% {
    background-color: transparent;
    color: inherit;
  }
}

// 设备图标样式
.device-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;

  /deep/ svg {
    width: 100%;
    height: 100%;
    display: block;
  }
}
</style>
