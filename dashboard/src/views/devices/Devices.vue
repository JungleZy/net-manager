<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[12px]">
      <div class="mb-4 layout-side">
        <div>
          <span class="mr-2 font-medium">设备类型:</span>
          <a-select
            v-model:value="filterType"
            style="width: 200px; margin-right: 12px"
            allow-clear
          >
            <a-select-option value="">全部类型</a-select-option>
            <a-select-option value="__unset__">未设置</a-select-option>
            <a-select-option value="计算机">计算机</a-select-option>
            <a-select-option value="服务器">服务器</a-select-option>
            <a-select-option value="交换机">交换机</a-select-option>
            <a-select-option value="路由器">路由器</a-select-option>
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
                record.services_count !== undefined ? record.services_count : 0
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
            <a-button type="link" size="small" @click="openEditModal(record)"
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

      <!-- 创建/编辑设备模态框 -->
      <a-modal
        v-model:open="showModal"
        :title="isEditing ? '编辑设备' : '添加设备'"
        @ok="saveDevice"
        @cancel="closeModal"
        :confirm-loading="confirmLoading"
        :destroyOnClose="true"
      >
        <a-form :model="currentDevice" layout="vertical">
          <a-form-item label="设备类型">
            <a-select
              v-model:value="currentDevice.type"
              placeholder="请选择设备类型"
            >
              <a-select-option value="">请选择设备类型</a-select-option>
              <a-select-option value="__unset__">未设置</a-select-option>
              <a-select-option value="计算机">计算机</a-select-option>
              <a-select-option value="服务器">服务器</a-select-option>
              <a-select-option value="交换机">交换机</a-select-option>
              <a-select-option value="路由器">路由器</a-select-option>
              <a-select-option value="其他">其他</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="设备名称">
            <a-input
              v-model:value="currentDevice.hostname"
              placeholder="请输入设备名称"
            />
          </a-form-item>
          <a-form-item label="IP地址">
            <a-input
              v-model:value="currentDevice.ip_address"
              placeholder="请输入IP地址"
            />
          </a-form-item>
          <a-form-item label="MAC地址">
            <a-input
              v-model:value="currentDevice.mac_address"
              placeholder="请输入MAC地址"
              :disabled="isEditing"
            />
          </a-form-item>
          <a-form-item label="操作系统">
            <a-input
              v-model:value="currentDevice.os_name"
              placeholder="请输入操作系统"
            />
          </a-form-item>
          <a-form-item label="系统版本">
            <a-input
              v-model:value="currentDevice.os_version"
              placeholder="请输入系统版本"
            />
          </a-form-item>
        </a-form>
      </a-modal>

      <!-- 服务详情模态框 -->
      <a-modal
        v-model:open="showServicesModal"
        :title="'服务详情 - ' + currentDeviceName"
        @cancel="closeServicesModal"
        centered
        width="600px"
        :body-style="{ height: height - 120 + 'px' }"
        :footer="null"
        :destroyOnClose="true"
      >
        <div class="flex flex-col size-full">
          <div class="flex-1 overflow-auto">
            <a-list :data-source="paginatedServices" :pagination="false">
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <div style="width: 100%">
                    <div>
                      <strong
                        >{{
                          (servicesPagination.current - 1) *
                            servicesPagination.pageSize +
                          index +
                          1
                        }}. {{ item.process_name || '未知进程' }}</strong
                      >
                    </div>
                    <div style="font-size: 12px; color: #666">
                      协议: {{ item.protocol }} | 地址:
                      {{ item.local_address }} | 状态: {{ item.status }} | PID:
                      {{ item.pid || 'N/A' }}
                    </div>
                  </div>
                </a-list-item>
              </template>
            </a-list>
          </div>
          <div class="border-t border-gray-200 pt-[12px]">
            <a-pagination
              v-model:current="servicesPagination.current"
              v-model:page-size="servicesPagination.pageSize"
              :total="servicesList.length"
              show-size-changer
              @change="handleServicesPageChange"
            />
          </div>
        </div>
      </a-modal>

      <!-- 进程详情模态框 -->
      <a-modal
        v-model:open="showProcessesModal"
        :title="'进程详情 - ' + currentDeviceName"
        @cancel="closeProcessesModal"
        width="600px"
        centered
        :body-style="{ height: height - 120 + 'px' }"
        :footer="null"
        :destroyOnClose="true"
      >
        <div class="flex flex-col size-full">
          <div class="flex-1 overflow-auto">
            <a-list :data-source="paginatedProcesses" :pagination="false">
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <div style="width: 100%">
                    <div>
                      <strong
                        >{{
                          (processesPagination.current - 1) *
                            processesPagination.pageSize +
                          index +
                          1
                        }}. PID: {{ item.pid }}</strong
                      >
                      - {{ item.name }}
                      <span
                        style="margin-left: 10px; font-size: 12px; color: #999"
                        >({{ item.status }})</span
                      >
                    </div>
                    <div style="font-size: 12px; color: #666">
                      CPU: {{ item.cpu_percent }}% | 内存:
                      {{ item.memory_percent }}%
                    </div>
                    <!-- 显示端口信息 -->
                    <div
                      v-if="item.ports && item.ports.length > 0"
                      style="font-size: 12px; color: #888; margin-top: 5px"
                    >
                      <div
                        v-for="(port, portIndex) in item.ports"
                        :key="portIndex"
                      >
                        {{ port.protocol }}: {{ port.local_address }}
                      </div>
                    </div>
                  </div>
                </a-list-item>
              </template>
            </a-list>
          </div>
          <div class="border-t border-gray-200 pt-[12px]">
            <a-pagination
              v-model:current="processesPagination.current"
              v-model:page-size="processesPagination.pageSize"
              :total="processesList.length"
              show-size-changer
              @change="handleProcessesPageChange"
            />
          </div>
        </div>
      </a-modal>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import DeviceApi from '@/common/api/device.js'
import SystemApi from '@/common/api/system.js'
import { useWindowSize } from '@vueuse/core'

// 设备列表
const devices = ref([])

// 详情模态框相关
const showServicesModal = ref(false)
const showProcessesModal = ref(false)
const servicesList = ref([])
const processesList = ref([])
const currentDeviceName = ref('')
const { height } = useWindowSize()

// 分页相关数据
const servicesPagination = ref({
  current: 1,
  pageSize: 10
})

const processesPagination = ref({
  current: 1,
  pageSize: 10
})

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
const isEditing = ref(false)
const confirmLoading = ref(false)
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

// 计算分页后的服务列表
const paginatedServices = computed(() => {
  const start =
    (servicesPagination.value.current - 1) * servicesPagination.value.pageSize
  const end = start + servicesPagination.value.pageSize
  return servicesList.value.slice(start, end)
})

// 计算分页后的进程列表
const paginatedProcesses = computed(() => {
  const start =
    (processesPagination.value.current - 1) * processesPagination.value.pageSize
  const end = start + processesPagination.value.pageSize
  return processesList.value.slice(start, end)
})

// 清除筛选
const clearFilter = () => {
  filterType.value = ''
}

// 显示服务详情
const handleShowServices = async (record) => {
  try {
    // 获取设备详细信息
    const response = await SystemApi.getSystemInfo(record.mac_address)
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

      // 重置分页
      servicesPagination.value.current = 1
    }
  } catch (error) {
    console.error('获取服务详情失败:', error)
  }
}

// 显示进程详情
const handleShowProcesses = async (record) => {
  try {
    // 获取设备详细信息
    const response = await SystemApi.getSystemInfo(record.mac_address)
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

      // 重置分页
      processesPagination.value.current = 1
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

// 处理服务分页变化
const handleServicesPageChange = (page, pageSize) => {
  servicesPagination.value.current = page
  servicesPagination.value.pageSize = pageSize
}

// 处理进程分页变化
const handleProcessesPageChange = (page, pageSize) => {
  processesPagination.value.current = page
  processesPagination.value.pageSize = pageSize
}

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  // 可以在这里处理分页、排序和筛选逻辑
  console.log('Table changed:', pag, filters, sorter)
}

// 格式化操作系统信息
const formatOSInfo = (device) => {
  if (!device.os_name) return '未知'

  let osInfo = device.os_name
  if (device.os_version) {
    osInfo += ' ' + device.os_version
  }

  // 根据 machine_type 判断架构类型
  let architecture = device.os_architecture
  if (device.machine_type) {
    // 根据 machine_type 判断架构
    const machineType = device.machine_type.toLowerCase()
    if (machineType.includes('arm') || machineType.includes('aarch64')) {
      architecture += '-ARM'
    } else if (
      machineType.includes('x86') ||
      machineType.includes('amd64') ||
      machineType.includes('i386') ||
      machineType.includes('i686')
    ) {
      architecture += '-x86'
    } else {
      architecture = device.machine_type
    }
  }

  if (architecture) {
    osInfo += ' (' + architecture + ')'
  }

  return osInfo
}

// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await SystemApi.getSystemsList()
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
const saveDevice = async () => {
  try {
    if (isEditing.value) {
      // 更新设备
      const response = await DeviceApi.updateDevice(currentDevice.value)
      if (response.status === 'success') {
        alert('设备更新成功')
        closeModal()
        fetchDevices()
      } else {
        alert('设备更新失败: ' + response.message)
      }
    } else {
      // 创建设备
      const response = await DeviceApi.createDevice(currentDevice.value)
      if (response.status === 'success') {
        alert('设备创建成功')
        closeModal()
        fetchDevices()
      } else {
        alert('设备创建失败: ' + response.message)
      }
    }
  } catch (error) {
    console.error('保存设备失败:', error)
    alert('保存设备失败: ' + error.message)
  }
}

// 删除设备
const deleteDevice = async (macAddress) => {
  if (!confirm('确定要删除这个设备吗？')) {
    return
  }

  try {
    const response = await DeviceApi.deleteDevice({ mac_address: macAddress })
    if (response.status === 'success') {
      alert('设备删除成功')
      fetchDevices()
    } else {
      alert('设备删除失败: ' + response.message)
    }
  } catch (error) {
    console.error('删除设备失败:', error)
    alert('删除设备失败: ' + error.message)
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchDevices()
})
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
