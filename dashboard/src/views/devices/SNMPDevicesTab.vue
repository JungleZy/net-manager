<template>
  <div class="size-full">
    <!-- 筛选区域 -->
    <div class="mb-[12px] flex items-center gap-3">
      <a-input
        v-model:value="filters.deviceName"
        placeholder="设备名称"
        allow-clear
        style="width: 200px"
      />
      <a-input
        v-model:value="filters.alias"
        placeholder="设备别名"
        allow-clear
        style="width: 200px"
      />
      <a-select
        v-model:value="filters.deviceType"
        placeholder="设备类型"
        allow-clear
        style="width: 150px"
      >
        <a-select-option
          v-for="type in DEVICE_TYPE_OPTIONS"
          :key="type"
          :value="type"
        >
          {{ type }}
        </a-select-option>
      </a-select>
      <a-select
        v-model:value="filters.status"
        placeholder="状态"
        allow-clear
        style="width: 120px"
      >
        <a-select-option value="success">在线</a-select-option>
        <a-select-option value="error">离线</a-select-option>
        <a-select-option value="unknown">未知</a-select-option>
      </a-select>
      <a-button @click="resetFilters">重置</a-button>
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
    <!-- 交换机列表 -->
    <div class="w-full h-[calc(100%-56px)] overflow-auto">
      <a-table
        :columns="switchColumns"
        :data-source="filteredSwitches"
        :pagination="pagination"
        :loading="loading"
        size="small"
        row-key="id"
        bordered
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'if_count'">
            <a-popover
              v-if="record.if_count > 0"
              placement="left"
              :overlayStyle="{ width: '800px', maxWidth: '90vw' }"
            >
              <template #content>
                <div>
                  <div class="mb-3">
                    <a-descriptions bordered size="small" :column="2">
                      <a-descriptions-item label="设备名称">
                        {{ record.device_name }}
                      </a-descriptions-item>
                      <a-descriptions-item label="IP地址">
                        {{ record.ip }}
                      </a-descriptions-item>
                      <a-descriptions-item label="设备类型">
                        {{ record.device_type }}
                      </a-descriptions-item>
                      <a-descriptions-item label="端口总数">
                        {{ record.if_count }}
                      </a-descriptions-item>
                    </a-descriptions>
                  </div>

                  <a-table
                    :columns="interfaceColumns"
                    :data-source="getInterfaceList(record.id)"
                    :pagination="false"
                    :scroll="{ y: 400 }"
                    size="small"
                    row-key="index"
                    bordered
                  >
                    <template #bodyCell="{ column, record: ifRecord }">
                      <template v-if="column.dataIndex === 'admin_status_text'">
                        <a-tag
                          :color="
                            ifRecord.admin_status === 1 ? 'success' : 'default'
                          "
                          style="margin: 0"
                        >
                          {{ ifRecord.admin_status_text }}
                        </a-tag>
                      </template>
                      <template v-if="column.dataIndex === 'oper_status_text'">
                        <a-tag
                          :color="
                            ifRecord.oper_status === 1 ? 'success' : 'error'
                          "
                          style="margin: 0"
                        >
                          {{ ifRecord.oper_status_text }}
                        </a-tag>
                      </template>
                    </template>
                  </a-table>
                </div>
              </template>
              <a style="color: #1677ff; cursor: pointer">
                {{ record.if_count }}
              </a>
            </a-popover>
            <span v-else>-</span>
          </template>
          <template v-if="column.dataIndex === 'status'">
            <a-tag
              v-if="record.status === 'success'"
              color="success"
              style="margin: 0"
              :title="
                record.lastUpdate
                  ? `最后更新: ${new Date(record.lastUpdate).toLocaleString(
                      'zh-CN'
                    )}`
                  : ''
              "
            >
              在线
            </a-tag>
            <a-tag
              v-else-if="record.status === 'error'"
              style="margin: 0"
              color="error"
              :title="record.errorMsg || '设备离线'"
            >
              离线
            </a-tag>
            <a-tag v-else color="default" style="margin: 0"> 未知 </a-tag>
          </template>
          <template v-if="column.dataIndex === 'action'">
            <EditOutlined
              @click="openEditSwitchModal(record)"
              style="font-size: 16px; color: #1677ff"
              class="cursor-pointer"
            />
            <a-popconfirm
              title="确定要删除这个交换机吗？"
              @confirm="deleteSwitch(record.id)"
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
    <!-- SNMP扫描模态框 -->
    <SNMPScanModal
      v-model:visible="showDiscoverSwitchModal"
      @scan-complete="handleScanComplete"
      @cancel="handleDiscoverModalCancel"
    />

    <!-- 创建/编辑交换机模态框 -->
    <SwitchAddModal
      v-model:visible="showSwitchModal"
      :is-editing="isSwitchEditing"
      :switch-data="currentSwitch"
      @ok="saveSwitch"
      @cancel="handleSwitchModalCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, shallowRef } from 'vue'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import SNMPScanModal from '@/components/devices/SNMPScanModal.vue'
import SwitchAddModal from '@/components/devices/SwitchAddModal.vue'
import SwitchApi from '@/common/api/switch.js'
import SNMPStorage from '@/common/utils/SNMPStorage.js'
import { PubSub } from '@/common/utils/PubSub'
import { wsCode } from '@/common/ws/Ws'
import { message } from 'ant-design-vue'

// 常量定义
const STATUS_TEXT_MAP = {
  success: '在线',
  error: '离线',
  unknown: '未知'
}

const DEVICE_TYPE_OPTIONS = ['打印机', '防火墙', '路由器', '交换机', '其他']

const DEFAULT_SWITCH_DATA = {
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
  device_name: '',
  device_type: ''
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

// 设备列表
const switches = ref([])
// 筛选条件
const filters = ref({
  deviceName: '',
  alias: '',
  deviceType: undefined,
  status: undefined
})

// SNMP设备状态数据 - 使用 shallowRef 优化大对象性能（以switch_id为key）
const snmpDevicesStatus = shallowRef({})

// 设备列表增强状态 - 根据switch_id匹配状态
const switchesWithStatus = computed(() => {
  const statusData = snmpDevicesStatus.value
  return switches.value.map((sw) => {
    // 使用switch_id（数据库主键）匹配状态
    const snmpData = statusData[sw.id]
    return {
      ...sw,
      status: snmpData?.type || 'unknown',
      statusText: STATUS_TEXT_MAP[snmpData?.type] || STATUS_TEXT_MAP.unknown,
      lastUpdate: snmpData?.updateTime || null,
      errorMsg: snmpData?.error || null,
      if_count: snmpData?.device_info?.if_count || 0,
      uptime: snmpData?.device_info?.uptime || ''
    }
  })
})

// 格式化运行时长（将SNMP TimeTicks转换为易读格式）- 优化性能
const formatUptime = (uptime) => {
  if (!uptime || uptime === '' || uptime === '0') return '-'

  const ticks = parseInt(uptime, 10)
  if (isNaN(ticks) || ticks === 0) return '-'

  // 转换为秒
  const totalSeconds = Math.floor(ticks / 100)
  if (totalSeconds === 0) return '-'

  // 计算天、小时、分钟、秒
  const days = Math.floor(totalSeconds / 86400)
  const hours = Math.floor((totalSeconds % 86400) / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  // 构建显示字符串
  const parts = []
  if (days > 0) parts.push(`${days}天`)
  if (hours > 0) parts.push(`${hours}时`)
  if (minutes > 0) parts.push(`${minutes}分`)
  if (seconds > 0 && days === 0 && hours === 0) parts.push(`${seconds}秒`)

  return parts.length > 0 ? parts.join('') : '-'
}

// 过滤后的交换机列表 - 优化筛选逻辑
const filteredSwitches = computed(() => {
  const { deviceName, alias, deviceType, status } = filters.value

  // 如果没有任何筛选条件，直接返回
  if (!deviceName && !alias && !deviceType && !status) {
    return switchesWithStatus.value
  }

  // 预处理搜索词（小写化）
  const lowerDeviceName = deviceName?.toLowerCase()
  const lowerAlias = alias?.toLowerCase()

  return switchesWithStatus.value.filter((item) => {
    // 设备名称筛选
    if (
      lowerDeviceName &&
      !item.device_name?.toLowerCase().includes(lowerDeviceName)
    ) {
      return false
    }
    // 设备别名筛选
    if (lowerAlias && !item.alias?.toLowerCase().includes(lowerAlias)) {
      return false
    }
    // 设备类型筛选
    if (deviceType && item.device_type !== deviceType) {
      return false
    }
    // 状态筛选
    if (status && item.status !== status) {
      return false
    }
    return true
  })
})

// 处理筛选变化 - 移除空函数，直接使用计算属性自动更新
// const handleFilterChange = () => {}

// 重置筛选条件 - 优化对象创建
const resetFilters = () => {
  filters.value.deviceName = ''
  filters.value.alias = ''
  filters.value.deviceType = undefined
  filters.value.status = undefined
}
// SNMP扫描模态框相关
const showDiscoverSwitchModal = ref(false)

// 交换机添加/编辑模态框相关
const showSwitchModal = ref(false)
const isSwitchEditing = ref(false)
const currentSwitch = ref(null)

// 定义组件事件
const emit = defineEmits([
  'update:loading',
  'deleteSwitch',
  'handleTableChange'
])

// 接口表格列定义
const interfaceColumns = [
  {
    title: '序号',
    dataIndex: 'index',
    align: 'center',
    key: 'index',
    width: 44
  },
  {
    title: '接口描述',
    dataIndex: 'description',
    align: 'center',
    key: 'description',
    ellipsis: true,
    customRender: ({ text }) => {
      return text || '-'
    }
  },
  {
    title: '接口类型',
    dataIndex: 'type_text',
    align: 'center',
    key: 'type_text',
    width: 100
  },
  {
    title: '物理地址',
    dataIndex: 'address',
    align: 'center',
    key: 'address',
    width: 130,
    customRender: ({ text }) => {
      return text || '-'
    }
  },
  {
    title: '速度',
    dataIndex: 'speed_text',
    align: 'center',
    key: 'speed_text',
    width: 80,
    sorter: (a, b) => (a.speed || 0) - (b.speed || 0)
  },
  {
    title: '管理状态',
    dataIndex: 'admin_status_text',
    align: 'center',
    key: 'admin_status_text',
    width: 88,
    sorter: (a, b) => (a.admin_status || 0) - (b.admin_status || 0)
  },
  {
    title: '运行状态',
    dataIndex: 'oper_status_text',
    align: 'center',
    key: 'oper_status_text',
    width: 88,
    sorter: (a, b) => (a.oper_status || 0) - (b.oper_status || 0)
  }
]

// 交换机表格列定义
const switchColumns = [
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
    dataIndex: 'device_name',
    align: 'center',
    key: 'device_name',
    ellipsis: true,
    width: 150
  },
  {
    title: '设备别名',
    dataIndex: 'alias',
    align: 'center',
    key: 'alias',
    ellipsis: true,
    width: 150,
    customRender: ({ text }) => {
      if (!text || text.length === 0) {
        return '无'
      }
      return text
    }
  },
  {
    title: '设备类型',
    dataIndex: 'device_type',
    align: 'center',
    key: 'device_type',
    width: 70
  },
  {
    title: 'IP地址',
    dataIndex: 'ip',
    align: 'center',
    key: 'ip',
    width: 110
  },
  {
    title: '版本',
    dataIndex: 'snmp_version',
    align: 'center',
    key: 'snmp_version',
    width: 60
  },
  {
    title: '端口数量',
    dataIndex: 'if_count',
    align: 'center',
    key: 'if_count',
    width: 70
  },
  {
    title: '运行时长',
    dataIndex: 'uptime',
    align: 'center',
    key: 'uptime',
    width: 120,
    ellipsis: true,
    customRender: ({ text }) => {
      return formatUptime(text)
    }
  },
  {
    title: '描述',
    dataIndex: 'description',
    align: 'center',
    key: 'description',
    ellipsis: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    align: 'center',
    key: 'status',
    width: 60
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    align: 'center',
    key: 'updated_at',
    width: 136
  },
  {
    title: '操作',
    dataIndex: 'action',
    align: 'center',
    key: 'action',
    width: 60
  }
]
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
// 打开发现交换机模态框
const openDiscoverSwitchModal = () => {
  showDiscoverSwitchModal.value = true
}

// 处理扫描完成事件
const handleScanComplete = () => {
  fetchSwitches()
}

// 处理自动发现模态框关闭事件
const handleDiscoverModalCancel = () => {
  // 关闭模态框时刷新表格数据
  fetchSwitches()
}

// 打开创建交换机模态框 - 使用常量优化
const openCreateSwitchModal = () => {
  isSwitchEditing.value = false
  currentSwitch.value = { ...DEFAULT_SWITCH_DATA }
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

// 处理手动添加/编辑模态框关闭事件
const handleSwitchModalCancel = () => {
  closeSwitchModal()
  // 关闭模态框时刷新表格数据
  fetchSwitches()
}

// 保存交换机（创建或更新）- 优化逻辑复用
const saveSwitch = async (switchData) => {
  const isEdit = isSwitchEditing.value
  const action = isEdit ? SwitchApi.updateSwitch : SwitchApi.createSwitch
  const actionName = isEdit ? '更新' : '创建'

  try {
    const response = await action(switchData)
    if (response?.status === 'success') {
      message.success(`交换机${actionName}成功`)
      closeSwitchModal()
      fetchSwitches()
    } else {
      message.error(
        `交换机${actionName}失败: ${response?.message || '未知错误'}`
      )
    }
  } catch (error) {
    console.error(`保存交换机失败:`, error)
    message.error(`保存交换机失败: ${error?.message || '未知错误'}`)
  }
}

// 删除交换机 - 增强错误处理
const deleteSwitch = async (switchId) => {
  try {
    const response = await SwitchApi.deleteSwitch({ id: switchId })
    if (response?.status === 'success') {
      message.success('交换机删除成功')
      fetchSwitches()
    } else {
      message.error(`交换机删除失败: ${response?.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('删除交换机失败:', error)
    message.error(`删除交换机失败: ${error?.message || '未知错误'}`)
  }
}

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  emit('handleTableChange', pag, filters, sorter)
}

// 根据设备ID获取接口列表（用于Popover）
const getInterfaceList = (deviceId) => {
  const snmpData = snmpDevicesStatus.value[deviceId]
  if (
    snmpData &&
    snmpData.interface_info &&
    Array.isArray(snmpData.interface_info)
  ) {
    return snmpData.interface_info
  }
  return []
}

// 加载SNMP设备状态 - 使用新的buildStatusMap方法
const loadSNMPDevicesStatus = async () => {
  try {
    const statusMap = await SNMPStorage.buildStatusMap()
    if (statusMap && typeof statusMap === 'object') {
      snmpDevicesStatus.value = statusMap
      const count = Object.keys(statusMap).length
      if (count > 0) {
        console.log(`加载SNMP设备状态: ${count}个设备`)
      }
    }
  } catch (error) {
    console.error('加载SNMP设备状态失败:', error)
    // 失败时保持原有数据，不清空
  }
}

// WebSocket消息处理器 - 处理单设备实时更新
const handleDeviceUpdate = async (deviceData) => {
  try {
    const switchId = deviceData.switch_id
    if (!switchId) {
      console.warn('设备数据缺少switch_id:', deviceData)
      return
    }

    // 获取当前状态映射
    const currentStatus = { ...snmpDevicesStatus.value }

    // 如果该switch_id不存在，初始化结构
    if (!currentStatus[switchId]) {
      currentStatus[switchId] = {
        type: 'unknown',
        updateTime: null,
        error: null,
        device_info: {},
        interface_info: []
      }
    }

    // 更新设备信息状态
    currentStatus[switchId].type = deviceData.type
    currentStatus[switchId].updateTime = new Date().toISOString()
    currentStatus[switchId].error = deviceData.error || null
    currentStatus[switchId].device_info = deviceData.device_info || {}

    // 更新状态
    snmpDevicesStatus.value = currentStatus

    console.debug(
      `设备状态更新: switch_id=${switchId}, status=${deviceData.type}`
    )
  } catch (error) {
    console.error('处理设备更新失败:', error)
  }
}

// WebSocket消息处理器 - 处理单接口实时更新
const handleInterfaceUpdate = async (interfaceData) => {
  try {
    const switchId = interfaceData.switch_id
    if (!switchId) {
      console.warn('接口数据缺少switch_id:', interfaceData)
      return
    }

    // 获取当前状态映射
    const currentStatus = { ...snmpDevicesStatus.value }

    // 如果该switch_id不存在，初始化结构
    if (!currentStatus[switchId]) {
      currentStatus[switchId] = {
        type: 'unknown',
        updateTime: null,
        error: null,
        device_info: {},
        interface_info: []
      }
    }

    // 更新接口信息状态（仅当设备信息不存在时更新type）
    if (
      !currentStatus[switchId].device_info ||
      Object.keys(currentStatus[switchId].device_info).length === 0
    ) {
      currentStatus[switchId].type = interfaceData.type
    }
    currentStatus[switchId].updateTime = new Date().toISOString()
    currentStatus[switchId].interface_info = interfaceData.interface_info || []

    // 更新状态
    snmpDevicesStatus.value = currentStatus

    console.debug(
      `接口状态更新: switch_id=${switchId}, 接口数=${
        interfaceData.interface_info?.length || 0
      }`
    )
  } catch (error) {
    console.error('处理接口更新失败:', error)
  }
}

// 组件挂载 - 订阅实时消息
onMounted(() => {
  fetchSwitches()
  // 异步加载SNMP状态，不阻塞组件渲染
  loadSNMPDevicesStatus().catch((err) => {
    console.error('初始化SNMP状态失败:', err)
  })

  // 订阅SNMP设备实时更新
  PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, handleDeviceUpdate)
  // 订阅SNMP接口实时更新
  PubSub.subscribe(wsCode.SNMP_INTERFACE_UPDATE, handleInterfaceUpdate)
  console.log('SNMP实时状态订阅已启动')
})

// 组件卸载 - 清理资源
onUnmounted(() => {
  PubSub.unsubscribe(wsCode.SNMP_DEVICE_UPDATE)
  PubSub.unsubscribe(wsCode.SNMP_INTERFACE_UPDATE)
  // 清空状态，释放内存
  snmpDevicesStatus.value = {}
  console.log('SNMP实时状态订阅已取消')
})
</script>
