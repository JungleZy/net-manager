<template>
  <a-modal
    :open="modalVisible"
    title="发现交换机"
    :confirm-loading="confirmLoading"
    @ok="handleOk"
    @cancel="handleCancel"
    :width="660"
    centered
    :destroy-on-close="true"
    :mask-closable="false"
    :okText="okText"
    :body-style="{ height: height - 120 + 'px' }"
  >
    <div class="modal-content-container">
      <a-form
        ref="formRef"
        :model="formState"
        :rules="rules"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 20 }"
        class="form-container"
      >
        <a-form-item label="IP段" name="network">
          <a-input
            v-model:value="formState.network"
            placeholder="请输入IP段，例如：192.168.1.0/24"
          />
        </a-form-item>

        <a-form-item label="SNMP版本" name="snmp_version">
          <a-select
            v-model:value="formState.snmp_version"
            placeholder="请选择SNMP版本"
            @change="handleSnmpVersionChange"
          >
            <a-select-option value="1">SNMPv1</a-select-option>
            <a-select-option value="2c">SNMPv2c</a-select-option>
            <a-select-option value="3">SNMPv3</a-select-option>
          </a-select>
        </a-form-item>

        <!-- SNMPv2c 配置 -->
        <template v-if="formState.snmp_version === '2c'">
          <a-form-item label="团体名" name="community">
            <a-input
              v-model:value="formState.community"
              placeholder="请输入团体名"
            />
          </a-form-item>
        </template>

        <!-- SNMPv1 配置 -->
        <template v-if="formState.snmp_version === '1'">
          <a-form-item label="团体名" name="community">
            <a-input
              v-model:value="formState.community"
              placeholder="请输入团体名"
            />
          </a-form-item>
        </template>

        <!-- SNMPv3 配置 -->
        <template v-if="formState.snmp_version === '3'">
          <a-form-item label="用户名" name="user">
            <a-input
              v-model:value="formState.user"
              placeholder="请输入用户名"
            />
          </a-form-item>

          <a-form-item label="认证密钥" name="auth_key">
            <a-input-password
              v-model:value="formState.auth_key"
              placeholder="请输入认证密钥"
            />
          </a-form-item>

          <a-form-item label="认证协议" name="auth_protocol">
            <a-select
              v-model:value="formState.auth_protocol"
              placeholder="请选择认证协议"
            >
              <a-select-option value="MD5">MD5</a-select-option>
              <a-select-option value="SHA">SHA</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="隐私密钥" name="priv_key">
            <a-input-password
              v-model:value="formState.priv_key"
              placeholder="请输入隐私密钥"
            />
          </a-form-item>

          <a-form-item label="隐私协议" name="priv_protocol">
            <a-select
              v-model:value="formState.priv_protocol"
              placeholder="请选择隐私协议"
            >
              <a-select-option value="DES">DES</a-select-option>
              <a-select-option value="AES">AES</a-select-option>
            </a-select>
          </a-form-item>
        </template>
      </a-form>
      <div
        class="w-full layout-center bottom-area"
        v-if="scanTaskId && (!scanTaskData || scanTaskData.length === 0)"
      >
        <div class="scan-animation">
          <svg class="spinner" viewBox="0 0 50 50">
            <circle
              class="path"
              cx="25"
              cy="25"
              r="20"
              fill="none"
              stroke-width="5"
            ></circle>
          </svg>
          <p>SNMP扫描中...</p>
        </div>
      </div>
      <div
        class="w-full bottom-area table-container"
        v-else-if="!scanTaskId && scanTaskData && scanTaskData.length > 0"
      >
        <a-table
          :dataSource="scanTaskData"
          :columns="columns"
          :pagination="false"
          :scroll="{ y: '100%' }"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'description'">
              <div class="whitespace-pre-line">{{ record.description }}</div>
            </template>
            <template v-else-if="column.dataIndex === 'action'">
              <a-button
                type="primary"
                size="small"
                @click="addToSwitches(record)"
                >添加</a-button
              >
            </template>
          </template>
        </a-table>
      </div>
      <div class="w-full layout-center bottom-area" v-else>
        <a-empty description="暂无扫描数据" />
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import SwitchApi from '@/common/api/switch.js'
import { useWindowSize } from '@vueuse/core'
import localforage from 'localforage'
import { wsCode } from '@/common/ws/Ws.js'
import { PubSub } from '@/common/utils/PubSub.js'
import { deriveDeviceName } from '@/common/utils/Utils.js'

const { height } = useWindowSize()

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'ok', 'cancel'])

// 表单引用
const formRef = ref()
const okText = ref('发起扫描')

// 表单状态
const formState = reactive({
  network: '192.168.43.0/24',
  snmp_version: '2c',
  community: 'wjkjv2user',
  user: '',
  auth_key: '',
  auth_protocol: 'MD5',
  priv_key: '',
  priv_protocol: 'DES'
})

// 表单验证规则
const rules = {
  network: [
    { required: true, message: '请输入IP段' },
    {
      pattern: /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/,
      message: '请输入有效的IP段，例如：192.168.1.0/24'
    }
  ],
  snmp_version: [{ required: true, message: '请选择SNMP版本' }],
  community: [{ required: true, message: '请输入团体名', trigger: 'blur' }],
  user: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  auth_key: [{ required: true, message: '请输入认证密钥', trigger: 'blur' }],
  auth_protocol: [{ required: true, message: '请选择认证协议' }],
  priv_key: [{ required: true, message: '请输入隐私密钥', trigger: 'blur' }],
  priv_protocol: [{ required: true, message: '请选择隐私协议' }]
}

// 模态框可见性
const modalVisible = ref(false)

// 确认按钮加载状态
const confirmLoading = ref(false)

// 监听visible属性变化
watch(
  () => props.visible,
  (newVal) => {
    modalVisible.value = newVal
    if (newVal) {
      // 重置表单
      resetForm()
    }
  },
  { immediate: true }
)
const scanTaskId = ref('')

onMounted(() => {
  localforage.getItem('scanTaskId').then((value) => {
    scanTaskId.value = value
  })
})

const scanTaskData = ref([])
PubSub.subscribe(wsCode.SCAN_TASK, (data) => {
  if (data.event === 'scan_completed') {
    scanTaskData.value = data.data
    scanTaskId.value = undefined
    confirmLoading.value = false
    okText.value = '发起扫描'
  } else if (data.event === 'scan_error') {
    scanTaskId.value = undefined
    confirmLoading.value = false
    okText.value = '发起扫描'
  }
})

// 表列定义
const columns = [
  {
    title: 'IP地址',
    dataIndex: 'ip',
    key: 'ip',
    align: 'center',
    width: 120
  },
  {
    title: '团体名',
    dataIndex: 'community',
    key: 'community',
    align: 'center',
    width: 120
  },
  {
    title: '设备描述',
    dataIndex: 'description',
    key: 'description',
    align: 'center'
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    align: 'center',
    width: 80
  }
]
// 重置表单
const resetForm = () => {
  formState.network = '192.168.43.0/24'
  formState.snmp_version = '2c'
  formState.community = 'wjkjv2user'
  formState.user = ''
  formState.auth_key = ''
  formState.auth_protocol = 'MD5'
  formState.priv_key = ''
  formState.priv_protocol = 'DES'
}

// SNMP版本变更处理
const handleSnmpVersionChange = (value) => {
  // 清除与特定版本相关的字段
  if (value === '1' || value === '2c') {
    formState.user = ''
    formState.auth_key = ''
    formState.auth_protocol = ''
    formState.priv_key = ''
    formState.priv_protocol = ''
  } else if (value === '3') {
    formState.community = ''
  }
}

// 确定按钮处理
const handleOk = () => {
  okText.value = '扫描中'
  scanTaskData.value = []
  message.loading({
    content: '扫描中...',
    duration: 0,
    key: 'scanLoading'
  })
  formRef.value
    .validate()
    .then(async () => {
      confirmLoading.value = true
      try {
        // 调用SNMP扫描接口
        const scanParams = {
          network: formState.network,
          version:
            formState.snmp_version === '2c' ? 'v2c' : formState.snmp_version,
          communities:
            formState.snmp_version === '2c' || formState.snmp_version === '1'
              ? formState.community.split(',')
              : undefined,
          user: formState.snmp_version === '3' ? formState.user : undefined,
          auth_key:
            formState.snmp_version === '3' ? formState.auth_key : undefined,
          auth_protocol:
            formState.snmp_version === '3'
              ? formState.auth_protocol.toLowerCase()
              : undefined,
          priv_key:
            formState.snmp_version === '3' ? formState.priv_key : undefined,
          priv_protocol:
            formState.snmp_version === '3' ? formState.priv_protocol : undefined
        }

        // 过滤掉undefined的参数
        const filteredParams = Object.fromEntries(
          Object.entries(scanParams).filter(([_, v]) => v !== undefined)
        )

        // 调用后端SNMP扫描接口
        const response = await SwitchApi.scanNetworkDevices(filteredParams)

        console.log(response)

        scanTaskId.value = response.task_id
        message.success({
          content: `发起扫描成功，请等待扫描完成`,
          key: 'scanLoading'
        })
        emit('ok', response.data)
      } catch (error) {
        confirmLoading.value = false
        okText.value = '发起扫描'
        console.error('SNMP扫描失败:', error)
        message.error({
          content:
            'SNMP扫描失败: ' + (error.response?.data?.message || error.message),
          key: 'scanLoading'
        })
      }
    })
    .catch((error) => {
      console.error('表单验证失败:', error)
      okText.value = '发起扫描'
      message.error({
        content: '请检查表单填写是否正确',
        key: 'scanLoading'
      })
    })
}

// 取消按钮处理
const handleCancel = () => {
  emit('update:visible', false)
  emit('cancel')
}

// 添加到交换机列表
const addToSwitches = async (record) => {
  try {
    // 构造交换机数据
    const switchData = {
      ip: record.ip,
      snmp_version: formState.snmp_version,
      community: record.community || formState.community,
      description: record.description || '',
      device_name: deriveDeviceName(record.description)
    }

    // 如果是SNMPv3，添加相关字段
    if (formState.snmp_version === '3') {
      switchData.user = formState.user
      switchData.auth_key = formState.auth_key
      switchData.auth_protocol = formState.auth_protocol
      switchData.priv_key = formState.priv_key
      switchData.priv_protocol = formState.priv_protocol
    }

    // 调用API添加交换机
    const response = await SwitchApi.createSwitch(switchData)

    if (response.status === 'success') {
      message.success('交换机添加成功')
      // 从扫描结果中移除已添加的记录
      const index = scanTaskData.value.findIndex(
        (item) => item.ip === record.ip
      )
      if (index > -1) {
        scanTaskData.value.splice(index, 1)
      }
    } else {
      message.error('交换机添加失败: ' + response.message)
    }
  } catch (error) {
    console.error('添加交换机失败:', error)
    message.error(
      '添加交换机失败: ' + (error.response?.data?.message || error.message)
    )
  }
}
</script>

<style scoped>
.modal-content-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.form-container {
  flex-shrink: 0;
}

.bottom-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.table-container {
  overflow: hidden;
}

.table-container :deep(.ant-table) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.table-container :deep(.ant-table-container) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.table-container :deep(.ant-table-body) {
  flex: 1;
}

.scan-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.scan-animation p {
  margin-top: 20px;
  font-size: 16px;
  color: #666;
}

.spinner {
  animation: rotate 2s linear infinite;
  width: 50px;
  height: 50px;
}

.path {
  stroke: #1890ff;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
</style>
