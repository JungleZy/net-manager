<template>
  <a-modal
    :open="modalVisible"
    title="发现交换机"
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
import SwitchApi from '@/common/api/switch.js'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'ok', 'cancel'])

// 表单引用
const formRef = ref()

// 表单状态
const formState = reactive({
  network: '192.168.1.0/24',
  snmp_version: '2c',
  community: 'public',
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

// 重置表单
const resetForm = () => {
  formState.network = '192.168.1.0/24'
  formState.snmp_version = '2c'
  formState.community = 'public'
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
              ? [formState.community]
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

        confirmLoading.value = false
        message.success(
          `扫描完成，发现 ${response.data.length} 个支持SNMP的设备`
        )
        emit('ok', response.data)
      } catch (error) {
        confirmLoading.value = false
        console.error('SNMP扫描失败:', error)
        message.error(
          'SNMP扫描失败: ' + (error.response?.data?.message || error.message)
        )
      }
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
