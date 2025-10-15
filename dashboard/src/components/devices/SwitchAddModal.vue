<template>
  <a-modal
    :open="modalVisible"
    :title="isEditing ? '编辑交换机' : '添加交换机'"
    :confirm-loading="confirmLoading"
    @ok="handleOk"
    @cancel="handleCancel"
    :width="600"
  >
    <a-form
      ref="formRef"
      :model="formState"
      :rules="rules"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 16 }"
    >
      <a-form-item label="设备名称" name="device_name">
        <a-input
          v-model:value="formState.device_name"
          placeholder="请输入设备名称"
        />
      </a-form-item>
      <a-form-item label="设备类型" name="device_type">
        <a-select
          v-model:value="formState.device_type"
          placeholder="请选择设备类型"
        >
          <a-select-option value="">请选择设备类型</a-select-option>
          <a-select-option value="交换机">交换机</a-select-option>
          <a-select-option value="路由器">路由器</a-select-option>
          <a-select-option value="防火墙">防火墙</a-select-option>
          <a-select-option value="服务器">服务器</a-select-option>
          <a-select-option value="其他">其他</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="IP地址" name="ip">
        <a-input
          v-model:value="formState.ip"
          placeholder="请输入交换机IP地址"
        />
      </a-form-item>

      <a-form-item label="描述" name="description">
        <a-textarea
          v-model:value="formState.description"
          placeholder="请输入交换机描述"
          :auto-size="{ minRows: 3, maxRows: 3 }"
          :rows="3"
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

      <!-- SNMPv3 配置 -->
      <template v-if="formState.snmp_version === '3'">
        <a-form-item label="用户名" name="user">
          <a-input v-model:value="formState.user" placeholder="请输入用户名" />
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
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
  },
  switchData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'ok', 'cancel'])

// 表单引用
const formRef = ref()

// 表单状态
const formState = reactive({
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

// 表单验证规则
const rules = {
  ip: [
    { required: true, message: '请输入IP地址' },
    { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: '请输入有效的IP地址' }
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
      // 如果是编辑模式，填充表单数据
      if (props.isEditing && props.switchData) {
        Object.keys(formState).forEach((key) => {
          if (props.switchData.hasOwnProperty(key)) {
            formState[key] = props.switchData[key]
          }
        })
      }
    }
  },
  { immediate: true }
)

// 重置表单
const resetForm = () => {
  Object.keys(formState).forEach((key) => {
    if (key === 'snmp_version') {
      formState[key] = '2c'
    } else if (key === 'device_name' || key === 'device_type') {
      formState[key] = ''
    } else {
      formState[key] = ''
    }
  })
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
  formRef.value
    .validate()
    .then(() => {
      confirmLoading.value = true
      // 模拟异步操作
      setTimeout(() => {
        confirmLoading.value = false
        const data = { ...formState }
        // 如果不是编辑模式，删除id字段
        if (!props.isEditing) {
          delete data.id
        }
        emit('ok', data)
      }, 500)
    })
    .catch((error) => {
      console.error('表单验证失败:', error)
      message.error('请检查表单填写是否正确')
    })
}

// 取消按钮处理
const handleCancel = () => {
  emit('update:visible', false)
  emit('cancel')
}
</script>

<style scoped>
/* 可以在这里添加自定义样式 */
</style>
