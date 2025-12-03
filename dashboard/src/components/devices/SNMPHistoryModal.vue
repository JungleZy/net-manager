<template>
  <a-modal
    :open="showSNMPHistoryModal"
    title="历史记录"
    @cancel="handleCancel"
    centered
    :body-style="{ height: '90vh' }"
    :width="1000"
  >
    <div class="h-full w-full p-2 flex flex-col">
      <div class="mb-2 flex items-center gap-2">
        <a-input-number
          v-model:value="limit"
          :min="10"
          :max="1000"
          :step="10"
          style="width: 140px"
          @change="reload"
        />
        <a-button @click="reload">刷新</a-button>
        <a-popconfirm
          title="确定清空当前设备的SNMP历史记录吗？"
          ok-text="确定"
          cancel-text="取消"
          @confirm="clearCurrent"
        >
          <a-button type="primary" danger>清空当前</a-button>
        </a-popconfirm>
      </div>
      <div class="flex-1 overflow-auto">
        <div
          v-if="!loading && historyRows.length === 0"
          class="w-full h-full flex items-center justify-center"
        >
          <a-empty description="暂无历史记录" />
        </div>
        <a-table
          v-else
          :dataSource="historyRows"
          :columns="columns"
          :pagination="false"
          :loading="loading"
          size="small"
          :scroll="{ y: '100%' }"
          rowKey="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'status'">
              <a-tag
                :color="
                  record.status === 'online'
                    ? 'green'
                    : record.status === 'offline'
                    ? 'red'
                    : 'default'
                "
              >
                {{ statusText(record.status) }}
              </a-tag>
            </template>
            <template v-else-if="column.dataIndex === 'poll_type'">
              <a-tag>{{
                record.poll_type === 'device' ? '设备' : '接口'
              }}</a-tag>
            </template>
            <template v-else-if="column.dataIndex === 'interface_count'">
              <a-popover
                v-if="
                  record.interface_count > 0 &&
                  Array.isArray(record.interface_info) &&
                  record.interface_info.length > 0
                "
                placement="left"
                :overlayStyle="{ width: '800px', maxWidth: '90vw' }"
              >
                <template #content>
                  <a-table
                    :columns="interfaceColumns"
                    :data-source="record.interface_info"
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
                            (ifRecord.admin_status || 0) === 1
                              ? 'success'
                              : 'default'
                          "
                          style="margin: 0"
                        >
                          {{ ifRecord.admin_status_text || '-' }}
                        </a-tag>
                      </template>
                      <template
                        v-else-if="column.dataIndex === 'oper_status_text'"
                      >
                        <a-tag
                          :color="
                            (ifRecord.oper_status || 0) === 1
                              ? 'success'
                              : 'error'
                          "
                          style="margin: 0"
                        >
                          {{ ifRecord.oper_status_text || '-' }}
                        </a-tag>
                      </template>
                    </template>
                  </a-table>
                </template>
                <a style="color: #1677ff; cursor: pointer">{{
                  record.interface_count
                }}</a>
              </a-popover>
              <span v-else>-</span>
            </template>
          </template>
        </a-table>
      </div>
    </div>
    <template #footer>
      <a-button @click="handleCancel">取消</a-button>
    </template>
  </a-modal>
</template>

<script>
export default {
  name: ''
}
</script>
<script setup>
import { ref, defineModel, watch } from 'vue'
import dayjs from 'dayjs'
import SnmpApi from '@/common/api/snmp.js'
import { message } from 'ant-design-vue'
// 模态框可见性
const currentSwitch = defineModel('currentSwitch')
const showSNMPHistoryModal = defineModel('showSNMPHistoryModal')

const handleCancel = () => {
  showSNMPHistoryModal.value = false
}

const loading = ref(false)
const limit = ref(100)
const historyRows = ref([])

const statusText = (s) =>
  s === 'online' ? '在线' : s === 'offline' ? '离线' : s || '未知'
const formatTime = (t) => (t ? dayjs(t).format('YYYY-MM-DD HH:mm:ss') : '')
const formatInterfaceInfo = (info) => {
  try {
    if (Array.isArray(info)) {
      return info
        .slice(0, 3)
        .map((i) => `${i.description || i.name || i.index || ''}`)
        .join('\n')
    }
    return typeof info === 'string' ? info : JSON.stringify(info)
  } catch (e) {
    return String(info)
  }
}

const columns = [
  {
    title: '设备名称',
    dataIndex: 'device_name',
    key: 'device_name',
    align: 'center',
    customRender: () => {
      const v = currentSwitch?.value?.device_name
      return v && v.length > 0 ? v : '无'
    }
  },
  {
    title: '设备别名',
    dataIndex: 'alias',
    key: 'alias',
    align: 'center',
    customRender: () => {
      const v = currentSwitch?.value?.alias
      return v && v.length > 0 ? v : '无'
    }
  },
  { title: 'IP', dataIndex: 'ip', key: 'ip', width: 140, align: 'center' },
  {
    title: '类型',
    dataIndex: 'poll_type',
    key: 'poll_type',
    width: 60,
    align: 'center'
  },
  {
    title: '更新时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
    align: 'center',
    customRender: ({ text }) => formatTime(text)
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 60,
    align: 'center'
  },
  {
    title: '端口数',
    dataIndex: 'interface_count',
    key: 'interface_count',
    width: 100,
    align: 'center'
  }
]

const interfaceColumns = [
  {
    title: '序号',
    dataIndex: 'index',
    align: 'center',
    key: 'index',
    width: 60
  },
  {
    title: '接口描述',
    dataIndex: 'description',
    align: 'center',
    key: 'description',
    ellipsis: true
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
    width: 140
  },
  {
    title: '速率',
    children: [
      {
        title: '最大',
        dataIndex: 'speed_text',
        align: 'center',
        key: 'speed_text',
        width: 90
      },
      {
        title: '下载',
        dataIndex: 'download_readable',
        align: 'center',
        key: 'download_readable',
        width: 90
      },
      {
        title: '上传',
        dataIndex: 'upload_readable',
        align: 'center',
        key: 'upload_readable',
        width: 90
      }
    ]
  },
  {
    title: '状态',
    children: [
      {
        title: '管理',
        dataIndex: 'admin_status_text',
        align: 'center',
        key: 'admin_status_text',
        width: 80
      },
      {
        title: '运行',
        dataIndex: 'oper_status_text',
        align: 'center',
        key: 'oper_status_text',
        width: 80
      }
    ]
  }
]

const loadHistory = async () => {
  loading.value = true
  try {
    const sid =
      currentSwitch?.value?.id ||
      currentSwitch?.value?.switch_id ||
      currentSwitch?.value
    if (!sid) {
      historyRows.value = []
      return
    }
    const resp = await SnmpApi.getHistory(sid, {
      limit: limit.value
    })
    const data = resp?.data?.data ?? resp?.data ?? []
    historyRows.value = Array.isArray(data) ? data : []
  } catch (e) {
    historyRows.value = []
    console.warn('加载历史记录失败:', e)
  } finally {
    loading.value = false
  }
}

const clearCurrent = async () => {
  loading.value = true
  try {
    const sid =
      currentSwitch?.value?.id ||
      currentSwitch?.value?.switch_id ||
      currentSwitch?.value
    const resp = await SnmpApi.clearHistory(sid)
    const ok = resp?.data?.status === 'success' || resp?.status === 'success'
    if (ok) {
      message.success('已清空当前设备SNMP历史记录')
      await loadHistory()
    } else {
      message.error('清空当前设备历史记录失败')
    }
  } catch (e) {
    message.error('清空当前设备历史记录失败: ' + (e?.message || String(e)))
  } finally {
    loading.value = false
  }
}

watch(
  () => showSNMPHistoryModal.value,
  (open) => {
    if (open) loadHistory()
  }
)
</script>
