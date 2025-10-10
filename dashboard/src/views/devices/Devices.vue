<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[12px] pt-[0]">
      <a-tabs class="size-full" v-model:activeKey="activeKey">
        <a-tab-pane class="size-full" key="1" tab="普通设备">
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
              row-key="mac_address"
              @change="handleTableChange"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.dataIndex === 'hostname'">
                  {{ record.hostname || '未知设备' }}
                </template>
                <template v-else-if="column.dataIndex === 'ip_address'">
                  {{ record.ip_address || '未知' }}
                </template>
                <template v-else-if="column.dataIndex === 'mac_address'">
                  {{ record.mac_address || '未知' }}
                </template>
                <template v-else-if="column.dataIndex === 'os_info'">
                  {{ formatOSInfo(record) }}
                </template>
                <template v-else-if="column.dataIndex === 'type'">
                  {{ record.type || '未设置' }}
                </template>
                <template v-else-if="column.dataIndex === 'services_count'">
                  <a
                    @click="handleShowServices(record)"
                    style="color: #1890ff; cursor: pointer"
                  >
                    {{
                      record.services_count !== undefined
                        ? record.services_count
                        : 0
                    }}
                  </a>
                </template>
                <template v-else-if="column.dataIndex === 'processes_count'">
                  <a
                    @click="handleShowProcesses(record)"
                    style="color: #1890ff; cursor: pointer"
                  >
                    {{
                      record.processes_count !== undefined
                        ? record.processes_count
                        : 0
                    }}
                  </a>
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
                    >编辑</a-button
                  >
                  <a-popconfirm
                    title="确定要删除这个设备吗？"
                    @confirm="deleteDevice(record.mac_address)"
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
        <a-tab-pane key="2" tab="交换设备" force-render>
          <div class="mb-[12px] layout-side">
            <div></div>
            <a-button
              class="layout-center"
              type="primary"
              @click="openCreateSwitchModal"
            >
              <template #icon>
                <PlusOutlined />
              </template>
              添加交换机
            </a-button>
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

      <!-- 创建/编辑交换机模态框 -->
      <SwitchAddModal
        v-model:visible="showSwitchModal"
        :is-editing="isSwitchEditing"
        :switch-data="currentSwitch"
        @ok="saveSwitch"
        @cancel="closeSwitchModal"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import DeviceApi from '@/common/api/device.js'
import SwitchApi from '@/common/api/switch.js'
import ServiceDetailModal from '@/components/devices/ServiceDetailModal.vue'
import ProcessDetailModal from '@/components/devices/ProcessDetailModal.vue'
import DeviceAddModal from '@/components/devices/DeviceAddModal.vue'
import SwitchAddModal from '@/components/devices/SwitchAddModal.vue'
import { message } from 'ant-design-vue'
import { onBeforeRouteLeave } from 'vue-router'
import { formatOSInfo } from '@/common/utils/Utils.js'

// 设备列表
const devices = ref([])
const switches = ref([])

// 从localStorage获取保存的标签页状态，如果没有则默认为'1'
const savedActiveKey = localStorage.getItem('devices-active-tab') || '1'
const activeKey = ref(savedActiveKey)

// 详情模态框相关
const showServicesModal = ref(false)
const showProcessesModal = ref(false)
const servicesList = ref([])
const processesList = ref([])
const currentDeviceName = ref('')

// 表格列定义
const columns = [
  {
    title: '设备名称',
    dataIndex: 'hostname',
    align: 'center',
    key: 'hostname'
  },
  {
    title: 'IP地址',
    dataIndex: 'ip_address',
    align: 'center',
    key: 'ip_address'
  },
  {
    title: 'MAC地址',
    dataIndex: 'mac_address',
    align: 'center',
    key: 'mac_address'
  },
  {
    title: '服务数量',
    dataIndex: 'services_count',
    align: 'center',
    key: 'services_count'
  },
  {
    title: '进程数量',
    dataIndex: 'processes_count',
    align: 'center',
    key: 'processes_count'
  },
  {
    title: '在线状态',
    dataIndex: 'online',
    align: 'center',
    key: 'online'
  },
  {
    title: '操作系统',
    dataIndex: 'os_info',
    align: 'center',
    key: 'os_info'
  },
  {
    title: '设备类型',
    dataIndex: 'type',
    align: 'center',
    key: 'type'
  },
  {
    title: '操作',
    dataIndex: 'action',
    align: 'center',
    key: 'action',
    width: 120
  }
]

// 表格分页和加载状态
const pagination = {
  pageSize: 10
}
const loading = ref(false)

// 筛选类型
const filterType = ref('')

// 模态框相关
const showModal = ref(false)
const showSwitchModal = ref(false)
const isEditing = ref(false)
const isSwitchEditing = ref(false)
const currentDevice = ref({
  mac_address: '',
  hostname: '',
  ip_address: '',
  type: '',
  os_name: '',
  os_version: '',
  gateway: '',
  netmask: '',
  os_architecture: '',
  machine_type: ''
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
    const response = await DeviceApi.getDeviceInfo(record.mac_address)
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
      currentDeviceName.value = record.hostname || record.mac_address
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
    const response = await DeviceApi.getDeviceInfo(record.mac_address)
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
      currentDeviceName.value = record.hostname || record.mac_address
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
  isEditing.value = false
  currentDevice.value = {
    mac_address: '',
    hostname: '',
    ip_address: '',
    type: '',
    os_name: '',
    os_version: '',
    gateway: '',
    netmask: '',
    os_architecture: '',
    machine_type: ''
  }
  showModal.value = true
}

// 打开编辑设备模态框
const openEditModal = (device) => {
  isEditing.value = true
  currentDevice.value = { ...device }
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
const deleteDevice = async (macAddress) => {
  try {
    const response = await DeviceApi.deleteDevice({ mac_address: macAddress })
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
</script>

<style lang="less" scoped>
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
</style>
