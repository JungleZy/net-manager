<template>
  <div class="size-full">
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
        bordered
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
    <!-- SNMP扫描模态框 -->
    <SNMPScanModal
      v-model:visible="showDiscoverSwitchModal"
      @scan-complete="() => emit('fetchSwitches')"
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
</template>

<script setup>
import { ref } from 'vue'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons-vue'
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
  device_name: ''
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
    title: '设备名称',
    dataIndex: 'device_name',
    align: 'center',
    key: 'device_name'
  },
  {
    title: 'IP地址',
    dataIndex: 'ip',
    align: 'center',
    key: 'ip',
    width: 120
  },
  {
    title: 'SNMP版本',
    dataIndex: 'snmp_version',
    align: 'center',
    key: 'snmp_version',
    width: 90
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
    key: 'created_at',
    width: 146
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    align: 'center',
    key: 'updated_at',
    width: 146
  },
  {
    title: '操作',
    dataIndex: 'action',
    align: 'center',
    key: 'action',
    width: 150
  }
]

// 打开发现交换机模态框
const openDiscoverSwitchModal = () => {
  showDiscoverSwitchModal.value = true
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
