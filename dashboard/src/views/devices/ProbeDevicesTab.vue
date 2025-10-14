<template>
  <div class="size-full">
    <div class="mb-[12px] layout-side">
      <div>
        <span class="mr-2 font-medium">设备类型:</span>
        <a-select
          v-model:value="filterType"
          style="width: 200px; margin-right: 12px"
          allow-clear
        >
          <a-select-option value="">全部类型</a-select-option>
          <a-select-option value="__unset__">未设置</a-select-option>
          <a-select-option value="台式机">台式机</a-select-option>
          <a-select-option value="笔记本">笔记本</a-select-option>
          <a-select-option value="服务器">服务器</a-select-option>
          <a-select-option value="其他">其他</a-select-option>
        </a-select>
        <a-button @click="clearFilter">重置</a-button>
      </div>
      <a-button class="layout-center" type="primary" @click="openCreateModal">
        <template #icon>
          <PlusOutlined />
        </template>
        添加设备
      </a-button>
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
            {{ record.type || '未设置' }}
          </template>
          <template v-else-if="column.dataIndex === 'cpu_usage'">
            {{
              record.cpu_info.usage_percent !== undefined
                ? record.cpu_info.usage_percent + '%'
                : '未知'
            }}
          </template>
          <template v-else-if="column.dataIndex === 'memory_usage'">
            {{
              record.memory_info.percentage !== undefined
                ? record.memory_info.percentage + '%'
                : '未知'
            }}
          </template>
          <template v-else-if="column.dataIndex === 'disk_usage'">
            {{
              record.disk_info.percentage !== undefined
                ? record.disk_info.percentage + '%'
                : '未知'
            }}
          </template>
          <template v-else-if="column.dataIndex === 'online'">
            <a-tag :color="record.online ? 'green' : 'red'">
              {{ record.online ? '在线' : '离线' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <EditOutlined
              @click="openEditModal(record)"
              style="font-size: 16px"
              class="cursor-pointer"
            />
            <a-popconfirm
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined
} from '@ant-design/icons-vue'
import { formatMachineType } from '@/common/utils/Utils.js'
import { message, Tooltip } from 'ant-design-vue'
import { h } from 'vue'
import DeviceAddModal from '@/components/devices/DeviceAddModal.vue'
import ServiceDetailModal from '@/components/devices/ServiceDetailModal.vue'
import ProcessDetailModal from '@/components/devices/ProcessDetailModal.vue'
import DeviceApi from '@/common/api/device.js'
import { wsCode } from '@/common/ws/Ws.js'
import { PubSub } from '@/common/utils/PubSub.js'

// 定义组件属性
const props = defineProps({
  devices: {
    type: Array,
    default: () => []
  },
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
  'update:devices',
  'update:loading',
  'fetchDevices',
  'handleTableChange',
  'handleShowServices',
  'handleShowProcesses',
  'handleShowNetworks',
  'clearFilter'
])

// 模态框相关
const showModal = ref(false)
const isEditing = ref(false)
const currentDevice = ref({
  id: '',
  hostname: '',
  ip_address: '',
  device_type: '',
  os_info: '',
  last_seen: ''
})

// 详情模态框相关
const showServicesModal = ref(false)
const showProcessesModal = ref(false)
const showNetworksModal = ref(false) // 添加网口详情模态框状态
const servicesList = ref([])
const processesList = ref([])
const networksList = ref([]) // 添加网口列表
const currentDeviceName = ref('')

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

// 格式化网络速率显示
const formatNetworkRate = (rate) => {
  if (rate === undefined || rate === null) {
    return '未知'
  }

  // 如果速率小于1000，显示为 Kbps
  if (rate < 1000) {
    return `${rate} Kbps`
  }

  // 如果速率小于1000000，显示为 Mbps，保留两位小数
  if (rate < 1000000) {
    return `${(rate / 1000).toFixed(2)} Mbps`
  }

  // 如果速率大于等于1000000，显示为 Gbps，保留两位小数
  return `${(rate / 1000000).toFixed(2)} Gbps`
}

// 筛选类型
const filterType = ref('')

// 计算筛选后的设备列表
const filteredDevices = computed(() => {
  if (!filterType.value) {
    return props.devices
  }
  // 特殊处理"未设置"类型
  if (filterType.value === '__unset__') {
    return props.devices.filter((device) => !device.type)
  }
  return props.devices.filter((device) => device.type === filterType.value)
})

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
    title: '设备名称',
    dataIndex: 'hostname',
    align: 'center',
    key: 'hostname'
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
    key: 'os_name'
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
    key: 'os_architecture'
  },
  {
    title: '硬件架构',
    dataIndex: 'machine_type',
    align: 'center',
    key: 'machine_type'
  },
  {
    title: 'CPU使用率',
    dataIndex: 'cpu_usage',
    align: 'center',
    key: 'cpu_usage',
    width: 86
  },
  {
    title: '内存使用率',
    dataIndex: 'memory_usage',
    align: 'center',
    key: 'memory_usage',
    width: 86
  },
  {
    title: '磁盘使用率',
    dataIndex: 'disk_usage',
    align: 'center',
    key: 'disk_usage',
    width: 86
  },
  {
    title: '服务数量',
    dataIndex: 'services_count',
    align: 'center',
    key: 'services_count',
    width: 70,
    customRender: ({ text, record }) => {
      return h(
        'a',
        {
          onClick: () => {
            if (record.services_count > 0 && record.online) {
              handleShowServices(record)
            }
          },
          style: {
            color:
              record.services_count > 0 && record.online
                ? '#1890ff'
                : '#00000040',
            cursor:
              record.services_count > 0 && record.online
                ? 'pointer'
                : 'not-allowed'
          }
        },
        record.services_count > 0 && record.online ? text : 0
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
      return h(
        'a',
        {
          onClick: () => {
            if (record.processes_count > 0 && record.online) {
              handleShowProcesses(record)
            }
          },
          style: {
            color:
              record.processes_count > 0 && record.online
                ? '#1890ff'
                : '#00000040',
            cursor:
              record.processes_count > 0 && record.online
                ? 'pointer'
                : 'not-allowed'
          }
        },
        record.processes_count > 0 && record.online ? text : 0
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
    title: '设备类型',
    dataIndex: 'type',
    align: 'center',
    key: 'type'
  },
  {
    title: '状态',
    dataIndex: 'online',
    align: 'center',
    key: 'online',
    width: 80
  },
  {
    title: '上报时间',
    dataIndex: 'timestamp',
    align: 'center',
    key: 'timestamp',
    width: 136,
    customRender: ({ text, record }) => {
      // 生成唯一key用于跟踪变更
      const key = `timestamp-${record.id}`
      // 检查是否是新变更的数据
      const isChanged = changedTimestamps.value[key] || false

      return h(
        'span',
        {
          class: isChanged ? 'timestamp-changed' : '',
          onAnimationEnd: () => {
            // 动画结束后清除标记
            if (changedTimestamps.value[key]) {
              const newChangedTimestamps = { ...changedTimestamps.value }
              newChangedTimestamps[key] = false
              changedTimestamps.value = newChangedTimestamps
            }
          }
        },
        text
      )
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

// 清除筛选
const clearFilter = () => {
  filterType.value = ''
  emit('clearFilter')
}

// 打开创建设备模态框
const openCreateModal = () => {
  isEditing.value = false
  currentDevice.value = {
    id: '',
    hostname: '',
    ip_address: '',
    device_type: '',
    os_info: '',
    last_seen: ''
  }
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
      emit('fetchDevices')
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

// 显示服务详情
const handleShowServices = async (record) => {
  try {
    // 获取设备详细信息
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response.data && response.data.services) {
      // 按PID排序服务列表
      const sortedServices = [...response.data.services].sort((a, b) => {
        // 处理PID为null的情况，将其排在最后
        if (a.pid === null && b.pid === null) return 0
        if (a.pid === null) return 1
        if (b.pid === null) return -1
        return a.pid - b.pid
      })
      servicesList.value = sortedServices
      currentDeviceName.value = record.hostname || record.id
      showServicesModal.value = true
    }
  } catch (error) {
    console.error('获取服务详情失败:', error)
  }
}

// 显示进程详情
const handleShowProcesses = async (record) => {
  try {
    // 获取设备详细信息
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response.data && response.data.processes) {
      // 按PID排序进程列表
      const sortedProcesses = [...response.data.processes].sort((a, b) => {
        // 处理PID为null的情况，将其排在最后
        if (a.pid === null && b.pid === null) return 0
        if (a.pid === null) return 1
        if (b.pid === null) return -1
        return a.pid - b.pid
      })
      processesList.value = sortedProcesses
      currentDeviceName.value = record.hostname || record.id
      showProcessesModal.value = true
    }
  } catch (error) {
    console.error('获取进程详情失败:', error)
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
    // 获取设备详细信息
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response.data && response.data.networks) {
      networksList.value = response.data.networks
      currentDeviceName.value = record.hostname || record.id
      showNetworksModal.value = true
    }
  } catch (error) {
    console.error('获取网口详情失败:', error)
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
        emit('fetchDevices')
      } else {
        message.error('设备更新失败: ' + response.message)
      }
    } else {
      // 创建设备
      const response = await DeviceApi.createDevice(deviceData)
      if (response.status === 'success') {
        message.success('设备创建成功')
        closeModal()
        emit('fetchDevices')
      } else {
        message.error('设备创建失败: ' + response.message)
      }
    }
  } catch (error) {
    console.error('保存设备失败:', error)
    message.error('保存设备失败: ' + error.message)
  }
}

// 页面挂载时订阅设备信息和状态更新
onMounted(() => {
  PubSub.subscribe(wsCode.DEVICE_INFO, (deviceInfo) => {
    // 处理设备信息更新
    const index = props.devices.findIndex((dev) => dev.id === deviceInfo.id)
    if (index !== -1) {
      // 检查时间戳是否发生变化
      const oldTimestamp = props.devices[index].timestamp
      const newTimestamp = deviceInfo.timestamp

      // 更新设备信息
      const updatedDevices = [...props.devices]
      updatedDevices[index] = { ...updatedDevices[index], ...deviceInfo }
      emit('update:devices', updatedDevices)

      // 如果时间戳发生变化，标记变更状态
      if (oldTimestamp !== newTimestamp) {
        const key = `timestamp-${deviceInfo.id}`
        const newChangedTimestamps = { ...changedTimestamps.value }
        newChangedTimestamps[key] = true
        changedTimestamps.value = newChangedTimestamps

        // 3秒后自动清除变更标记
        setTimeout(() => {
          const currentChangedTimestamps = { ...changedTimestamps.value }
          if (currentChangedTimestamps[key]) {
            currentChangedTimestamps[key] = false
            changedTimestamps.value = currentChangedTimestamps
          }
        }, 3000)
      }
    }
  })

  PubSub.subscribe(wsCode.DEVICE_STATUS, (data) => {
    // 处理设备状态更新
    console.log('收到设备状态更新:', data)
    // 可以根据需要更新设备列表
    // 例如：
    const index = props.devices.findIndex(
      (dev) => dev.client_id === data.client_id
    )
    if (index !== -1) {
      // 更新设备状态
      const updatedDevices = [...props.devices]
      updatedDevices[index].online = data.status === 'online'
      emit('update:devices', updatedDevices)
    }
  })
})

// 页面卸载时取消订阅
onUnmounted(() => {
  PubSub.unsubscribe(wsCode.DEVICE_INFO)
  PubSub.unsubscribe(wsCode.DEVICE_STATUS)
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
</style>
