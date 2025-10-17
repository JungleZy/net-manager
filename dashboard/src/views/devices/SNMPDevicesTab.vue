<template>
  <div class="size-full">
    <!-- 筛选区域 -->
    <div class="mb-[12px] flex items-center gap-3">
      <a-input
        v-model:value="filters.deviceName"
        placeholder="设备名称"
        allow-clear
        style="width: 200px"
        @change="handleFilterChange"
      />
      <a-input
        v-model:value="filters.alias"
        placeholder="设备别名"
        allow-clear
        style="width: 200px"
        @change="handleFilterChange"
      />
      <a-select
        v-model:value="filters.deviceType"
        placeholder="设备类型"
        allow-clear
        style="width: 150px"
        @change="handleFilterChange"
      >
        <a-select-option value="打印机">打印机</a-select-option>
        <a-select-option value="防火墙">防火墙</a-select-option>
        <a-select-option value="路由器">路由器</a-select-option>
        <a-select-option value="交换机">交换机</a-select-option>
        <a-select-option value="其他">其他</a-select-option>
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
import { ref, computed } from 'vue'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import SNMPScanModal from '@/components/devices/SNMPScanModal.vue'
import SwitchAddModal from '@/components/devices/SwitchAddModal.vue'
import SwitchApi from '@/common/api/switch.js'
import { message } from 'ant-design-vue'

// 定义组件属性
const props = defineProps({
  switches: {
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

// 筛选条件
const filters = ref({
  deviceName: '',
  alias: '',
  deviceType: undefined
})

// 过滤后的交换机列表
const filteredSwitches = computed(() => {
  let result = props.switches

  // 按设备名称筛选
  if (filters.value.deviceName) {
    result = result.filter((item) =>
      item.device_name
        ?.toLowerCase()
        .includes(filters.value.deviceName.toLowerCase())
    )
  }

  // 按设备别名筛选
  if (filters.value.alias) {
    result = result.filter((item) =>
      item.alias?.toLowerCase().includes(filters.value.alias.toLowerCase())
    )
  }

  // 按设备类型筛选
  if (filters.value.deviceType) {
    result = result.filter(
      (item) => item.device_type === filters.value.deviceType
    )
  }

  return result
})

// 处理筛选变化
const handleFilterChange = () => {
  // 筛选条件变化时，计算属性会自动更新
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    deviceName: '',
    alias: '',
    deviceType: undefined
  }
}

// SNMP扫描模态框相关
const showDiscoverSwitchModal = ref(false)

// 交换机添加/编辑模态框相关
const showSwitchModal = ref(false)
const isSwitchEditing = ref(false)
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
  device_name: '',
  device_type: ''
})

// 定义组件事件
const emit = defineEmits([
  'update:switches',
  'update:loading',
  'fetchSwitches',
  'deleteSwitch',
  'handleTableChange'
])

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
    title: '描述',
    dataIndex: 'description',
    align: 'center',
    key: 'description',
    ellipsis: true
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    align: 'center',
    key: 'created_at',
    width: 136
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

// 打开发现交换机模态框
const openDiscoverSwitchModal = () => {
  showDiscoverSwitchModal.value = true
}

// 处理扫描完成事件
const handleScanComplete = () => {
  emit('fetchSwitches')
}

// 处理自动发现模态框关闭事件
const handleDiscoverModalCancel = () => {
  // 关闭模态框时刷新表格数据
  emit('fetchSwitches')
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
    device_name: '',
    device_type: ''
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

// 处理手动添加/编辑模态框关闭事件
const handleSwitchModalCancel = () => {
  closeSwitchModal()
  // 关闭模态框时刷新表格数据
  emit('fetchSwitches')
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
        emit('fetchSwitches')
      } else {
        message.error('交换机更新失败: ' + response.message)
      }
    } else {
      // 创建交换机
      const response = await SwitchApi.createSwitch(switchData)
      if (response.status === 'success') {
        message.success('交换机创建成功')
        closeSwitchModal()
        emit('fetchSwitches')
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
      emit('fetchSwitches')
    } else {
      message.error('交换机删除失败: ' + response.message)
    }
  } catch (error) {
    console.error('删除交换机失败:', error)
    message.error('删除交换机失败: ' + error.message)
  }
}

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  emit('handleTableChange', pag, filters, sorter)
}
</script>
