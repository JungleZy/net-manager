<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[12px] pt-[0]">
      <a-tabs class="size-full" v-model:activeKey="activeKey">
        <a-tab-pane class="size-full" key="1" tab="探针设备">
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
            <a-button
              class="layout-center"
              type="primary"
              @click="openCreateModal"
            >
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
              @change="handleTableChange"
            >
              <template #bodyCell="{ column, record, index }">
                <template v-if="column.dataIndex === 'hostname'">
                  {{ record.hostname || '未知设备' }}
                </template>
                <template v-else-if="column.dataIndex === 'index'">
                  {{ index + 1 }}
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
                  <a-button
                    type="link"
                    size="small"
                    @click="openEditModal(record)"
                    style="padding: 0"
                    >编辑</a-button
                  >
                  <a-popconfirm
                    title="确定要删除这个设备吗？"
                    @confirm="deleteDevice(record.id)"
                    ok-text="确定"
                    cancel-text="取消"
                  >
                    <a-button
                      type="link"
                      style="padding: 0; margin-left: 6px"
                      size="small"
                      danger
                      >删除</a-button
                    >
                  </a-popconfirm>
                </template>
              </template>
            </a-table>
          </div>
        </a-tab-pane>
        <a-tab-pane key="2" tab="SNMP设备" force-render>
          <div class="mb-[12px] layout-side">
            <div></div>
            <div class="layout-right-center">
              <a-space-compact block>
                <a-button
                  class="layout-center mr-2"
                  type="primary"
                  @click="openDiscoverSwitchModal"
                >
                  <template #icon>
                    <SearchOutlined />
                  </template>
                  自动发现
                </a-button>
                <a-button
                  class="layout-center"
                  type="primary"
                  @click="openCreateSwitchModal"
                >
                  <template #icon>
                    <PlusOutlined />
                  </template>
                  手动添加
                </a-button>
              </a-space-compact>
            </div>
          </div>
          <!-- 交换机列表 -->
          <div class="w-full h-[calc(100%-44px)] overflow-auto">
            <a-table
              :columns="switchColumns"
              :data-source="switches"
              :pagination="pagination"
              :loading="loading"
              size="small"
              row-key="id"
              @change="handleTableChange"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.dataIndex === 'action'">
                  <a-button
                    type="link"
                    size="small"
                    @click="openEditSwitchModal(record)"
                    >编辑</a-button
                  >
                  <a-popconfirm
                    title="确定要删除这个交换机吗？"
                    @confirm="deleteSwitch(record.id)"
                    ok-text="确定"
                    cancel-text="取消"
                  >
                    <a-button type="link" size="small" danger>删除</a-button>
                  </a-popconfirm>
                </template>
              </template>
            </a-table>
          </div>
        </a-tab-pane>
      </a-tabs>

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
          size="small"
        />
        <template #footer>
          <a-button @click="closeNetworksModal">关闭</a-button>
        </template>
      </a-modal>

      <!-- 创建/编辑交换机模态框 -->
      <SwitchAddModal
        v-model:visible="showSwitchModal"
        :is-editing="isSwitchEditing"
        :switch-data="currentSwitch"
        @ok="saveSwitch"
        @cancel="closeSwitchModal"
      />

      <!-- SNMP扫描模态框 -->
      <SNMPScanModal
        v-model:visible="showDiscoverSwitchModal"
        @scan-complete="fetchSwitches"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, h } from 'vue'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons-vue'
import DeviceApi from '@/common/api/device.js'
import SwitchApi from '@/common/api/switch.js'
import ServiceDetailModal from '@/components/devices/ServiceDetailModal.vue'
import ProcessDetailModal from '@/components/devices/ProcessDetailModal.vue'
import DeviceAddModal from '@/components/devices/DeviceAddModal.vue'
import SwitchAddModal from '@/components/devices/SwitchAddModal.vue'
import SNMPScanModal from '@/components/devices/SNMPScanModal.vue'
import { message, Tooltip } from 'ant-design-vue'
import { onBeforeRouteLeave } from 'vue-router'
import { formatOSInfo, formatMachineType } from '@/common/utils/Utils.js'
import { wsCode } from '@/common/ws/Ws.js'
import { PubSub } from '@/common/utils/PubSub.js'

// 设备列表
const devices = ref([])
const switches = ref([])

// 从localStorage获取保存的标签页状态，如果没有则默认为'1'
const savedActiveKey = localStorage.getItem('devices-active-tab') || '1'
const activeKey = ref(savedActiveKey)

// 详情模态框相关
const showServicesModal = ref(false)
const showProcessesModal = ref(false)
const showNetworksModal = ref(false) // 添加网口详情模态框状态
const servicesList = ref([])
const processesList = ref([])
const networksList = ref([]) // 添加网口列表
const currentDeviceName = ref('')

// 表格列定义
const columns = [
  {
    title: '序号',
    dataIndex: 'index',
    align: 'center',
    key: 'index',
    width: 60
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
        return text[0]
      }
      // 如果有多个IP地址，显示第一个并提示还有更多
      return h('div', [
        h('span', text[0]),
        h(
          Tooltip,
          {
            title: text.join(', ')
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
    width: 100
  },
  {
    title: '内存使用率',
    dataIndex: 'memory_usage',
    align: 'center',
    key: 'memory_usage',
    width: 100
  },
  {
    title: '磁盘使用率',
    dataIndex: 'disk_usage',
    align: 'center',
    key: 'disk_usage',
    width: 100
  },
  {
    title: '服务数量',
    dataIndex: 'services_count',
    align: 'center',
    key: 'services_count',
    customRender: ({ text, record }) => {
      return h(
        'a',
        {
          onClick: () => {
            if (record.services_count > 0) {
              handleShowServices(record)
            }
          },
          style: {
            color: record.services_count > 0 ? '#1890ff' : '#00000040',
            cursor: record.services_count > 0 ? 'pointer' : 'not-allowed'
          }
        },
        text
      )
    }
  },
  {
    title: '进程数量',
    dataIndex: 'processes_count',
    align: 'center',
    key: 'processes_count',
    customRender: ({ text, record }) => {
      return h(
        'a',
        {
          onClick: () => {
            if (record.processes_count > 0) {
              handleShowProcesses(record)
            }
          },
          style: {
            color: record.processes_count > 0 ? '#1890ff' : '#00000040',
            cursor: record.processes_count > 0 ? 'pointer' : 'not-allowed'
          }
        },
        text
      )
    }
  },
  {
    title: '网口数量',
    dataIndex: 'networks_count',
    align: 'center',
    key: 'networks_count',
    customRender: ({ text, record }) => {
      return h(
        'a',
        {
          onClick: () => {
            if (record.networks_count > 0) {
              handleShowNetworks(record)
            }
          },
          style: {
            color: record.networks_count > 0 ? '#1890ff' : '#00000040',
            cursor: record.networks_count > 0 ? 'pointer' : 'not-allowed'
          }
        },
        text
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
              changedTimestamps.value[key] = false
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
    width: 86
  }
]

// 表格分页和加载状态
const pagination = {
  pageSize: 10
}
const loading = ref(false)

// 用于跟踪时间戳变更状态
const changedTimestamps = ref({})

// 筛选类型
const filterType = ref('')

// 模态框相关
const showModal = ref(false)
const showSwitchModal = ref(false)
const showDiscoverSwitchModal = ref(false)
const isEditing = ref(false)
const isSwitchEditing = ref(false)
const currentDevice = ref({
  id: '',
  hostname: '',
  ip_address: '',
  device_type: '',
  os_info: '',
  last_seen: ''
})
const currentSwitch = ref({
  id: undefined,
  ip: '',
  snmp_version: '2c',
  community: '',
  user: '',
  auth_key: '',
  auth_protocol: '',
  priv_key: '',
  priv_protocol: '',
  description: '',
  device_name: ''
})

// 计算筛选后的设备列表
const filteredDevices = computed(() => {
  if (!filterType.value) {
    return devices.value
  }
  // 特殊处理"未设置"类型
  if (filterType.value === '__unset__') {
    return devices.value.filter((device) => !device.type)
  }
  return devices.value.filter((device) => device.type === filterType.value)
})

// 清除筛选
const clearFilter = () => {
  filterType.value = ''
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

// 分页处理已移至独立组件中

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  // 可以在这里处理分页、排序和筛选逻辑
  console.log('Table changed:', pag, filters, sorter)
}

// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await DeviceApi.getDevicesList()
    devices.value = response.data || []
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

// 打开创建设备模态框
const openCreateModal = () => {
  isEditMode.value = false
  currentDevice.value = {
    id: '',
    hostname: '',
    ip_address: '',
    device_type: '',
    os_info: '',
    last_seen: ''
  }
  switchOptionsEditing.value = []
  isSwitchEditing.value = false
  showModal.value = true
}

// 打开编辑设备模态框
const openEditModal = (device) => {
  isEditing.value = true
  // 过滤掉device中的mac_address字段
  const { mac_address, ...deviceWithoutMac } = device
  currentDevice.value = { ...deviceWithoutMac }
  showModal.value = true
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

// 删除设备
const deleteDevice = async (id) => {
  try {
    const response = await DeviceApi.deleteDevice({ id: id })
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

// 交换机表格列定义
const switchColumns = [
  {
    title: '设备名称',
    dataIndex: 'device_name',
    align: 'center',
    key: 'device_name'
  },
  {
    title: 'IP地址',
    dataIndex: 'ip',
    align: 'center',
    key: 'ip'
  },
  {
    title: 'SNMP版本',
    dataIndex: 'snmp_version',
    align: 'center',
    key: 'snmp_version'
  },
  {
    title: '描述',
    dataIndex: 'description',
    align: 'center',
    key: 'description'
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    align: 'center',
    key: 'created_at'
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    align: 'center',
    key: 'updated_at'
  },
  {
    title: '操作',
    dataIndex: 'action',
    align: 'center',
    key: 'action',
    width: 150
  }
]

// 监听activeKey变化，保存到localStorage
watch(activeKey, (newVal) => {
  localStorage.setItem('devices-active-tab', newVal)
})

// 路由离开前重置devices-active-tab为1
onBeforeRouteLeave((to, from) => {
  localStorage.setItem('devices-active-tab', '1')
})

// 页面挂载时获取数据
onMounted(() => {
  fetchDevices()
  fetchSwitches()
  PubSub.subscribe(wsCode.DEVICE_INFO, (deviceInfo) => {
    // 处理设备信息更新
    console.log('收到设备信息更新:', deviceInfo)
    // 可以根据需要更新设备列表
    // 例如：
    const index = devices.value.findIndex((dev) => dev.id === deviceInfo.id)
    if (index !== -1) {
      // 检查时间戳是否发生变化
      const oldTimestamp = devices.value[index].timestamp
      const newTimestamp = deviceInfo.timestamp

      // 更新设备信息
      devices.value[index] = { ...devices.value[index], ...deviceInfo }

      // 如果时间戳发生变化，标记变更状态
      if (oldTimestamp !== newTimestamp) {
        const key = `timestamp-${deviceInfo.id}`
        changedTimestamps.value[key] = true

        // 3秒后自动清除变更标记
        setTimeout(() => {
          if (changedTimestamps.value[key]) {
            changedTimestamps.value[key] = false
          }
        }, 3000)
      }
    }
  })
})
// 获取交换机列表
const fetchSwitches = async () => {
  try {
    const response = await SwitchApi.getSwitchesList()
    switches.value = response.data || []
  } catch (error) {
    console.error('获取交换机列表失败:', error)
    message.error('获取交换机列表失败: ' + error.message)
  }
}

// 打开创建交换机模态框
const openCreateSwitchModal = () => {
  isSwitchEditing.value = false
  currentSwitch.value = {
    id: undefined,
    ip: '',
    snmp_version: '2c',
    community: '',
    user: '',
    auth_key: '',
    auth_protocol: '',
    priv_key: '',
    priv_protocol: '',
    description: '',
    device_name: ''
  }
  showSwitchModal.value = true
}

// 打开发现交换机模态框
const openDiscoverSwitchModal = () => {
  showDiscoverSwitchModal.value = true
}

// 打开编辑交换机模态框
const openEditSwitchModal = (switchData) => {
  isSwitchEditing.value = true
  currentSwitch.value = { ...switchData }
  showSwitchModal.value = true
}

// 关闭交换机模态框
const closeSwitchModal = () => {
  showSwitchModal.value = false
}

// 保存交换机（创建或更新）
const saveSwitch = async (switchData) => {
  try {
    if (isSwitchEditing.value) {
      // 更新交换机
      const response = await SwitchApi.updateSwitch(switchData)
      if (response.status === 'success') {
        message.success('交换机更新成功')
        closeSwitchModal()
        fetchSwitches()
      } else {
        message.error('交换机更新失败: ' + response.message)
      }
    } else {
      // 创建交换机
      const response = await SwitchApi.createSwitch(switchData)
      if (response.status === 'success') {
        message.success('交换机创建成功')
        closeSwitchModal()
        fetchSwitches()
      } else {
        message.error('交换机创建失败: ' + response.message)
      }
    }
  } catch (error) {
    console.error('保存交换机失败:', error)
    message.error('保存交换机失败: ' + error.message)
  }
}

// 删除交换机
const deleteSwitch = async (switchId) => {
  try {
    const response = await SwitchApi.deleteSwitch({ id: switchId })
    if (response.status === 'success') {
      message.success('交换机删除成功')
      fetchSwitches()
    } else {
      message.error('交换机删除失败: ' + response.message)
    }
  } catch (error) {
    console.error('删除交换机失败:', error)
    message.error('删除交换机失败: ' + error.message)
  }
}

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
    key: 'mac_address'
  },
  {
    title: '网关',
    dataIndex: 'gateway',
    key: 'gateway'
  },
  {
    title: '子网掩码',
    dataIndex: 'netmask',
    key: 'netmask'
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
</script>

<style lang="less">
.modal-max-height {
  :deep(.ant-modal) {
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }

  :deep(.ant-modal-content) {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-height: 90vh;
  }

  :deep(.ant-modal-body) {
    flex: 1;
    overflow-y: auto;
    max-height: calc(90vh - 110px); // 减去标题和footer的高度
  }
}

// 添加flex相关的工具类
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.flex-1 {
  flex: 1;
}

.overflow-auto {
  overflow: auto;
}

.border-t {
  border-top-width: 1px;
}

.border-gray-200 {
  border-color: #e5e7eb;
}

.pt-2 {
  padding-top: 0.5rem;
}

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
