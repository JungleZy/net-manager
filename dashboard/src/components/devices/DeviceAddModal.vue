<template>
  <a-modal
    :open="visible"
    :title="isEditing ? '编辑设备' : '添加设备'"
    @ok="handleOk"
    @cancel="handleCancel"
    :confirm-loading="confirmLoading"
    :destroyOnClose="true"
  >
    <a-form :model="form" layout="vertical">
      <a-form-item label="设备类型">
        <a-select v-model:value="form.type" placeholder="请选择设备类型">
          <a-select-option value="">请选择设备类型</a-select-option>
          <a-select-option value="台式机">台式机</a-select-option>
          <a-select-option value="笔记本">笔记本</a-select-option>
          <a-select-option value="服务器">服务器</a-select-option>
          <a-select-option value="其他">其他</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="设备名称">
        <a-input
          v-model:value="form.hostname"
          placeholder="请输入设备名称"
          :disabled="isEditing"
        />
      </a-form-item>
      <a-form-item label="IP地址">
        <a-input
          v-model:value="form.ip_address"
          placeholder="请输入IP地址"
          :disabled="isEditing"
        />
      </a-form-item>
      <a-form-item label="设备ID">
        <a-input
          v-model:value="form.id"
          placeholder="请输入设备ID"
          :disabled="isEditing"
        />
      </a-form-item>
      <a-form-item label="操作系统">
        <a-input
          v-model:value="form.os_name"
          placeholder="请输入操作系统"
          :disabled="isEditing"
        />
      </a-form-item>
      <a-form-item label="系统版本">
        <a-input
          v-model:value="form.os_version"
          placeholder="请输入系统版本"
          :disabled="isEditing"
        />
      </a-form-item>
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
  deviceData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'ok', 'cancel'])

// 表单数据
const form = reactive({
  id: '',
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

// 确认加载状态
const confirmLoading = ref(false)

// 监听设备数据变化，更新表单
watch(
  () => props.deviceData,
  (newVal) => {
    if (newVal) {
      Object.assign(form, newVal)
    }
  },
  { immediate: true, deep: true }
)

// 处理确认按钮点击
const handleOk = async () => {
  try {
    confirmLoading.value = true
    // 验证表单数据
    if (!form.id) {
      message.error('请输入设备ID')
      confirmLoading.value = false
      return
    }

    // 发送事件给父组件处理保存逻辑
    emit('ok', { ...form })
    confirmLoading.value = false
  } catch (error) {
    console.error('保存设备失败:', error)
    message.error('保存设备失败: ' + error.message)
    confirmLoading.value = false
  }
}

// 处理取消按钮点击
const handleCancel = () => {
  emit('update:visible', false)
  emit('cancel')
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: '',
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
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>
