<template>
  <a-modal
    v-model:open="processVisible"
    title="进程管理"
    width="600px"
    :confirmLoading="loading"
    @ok="onOk"
    @cancel="processVisible = false"
  >
    <a-spin :spinning="loadingData" tip="加载中...">
      <a-textarea
        placeholder="请输入需要监控的进程名称，多个进程用英文逗号隔开或者换行"
        v-model:value="processStr"
        :auto-size="{ minRows: 10, maxRows: 10 }"
      ></a-textarea>
    </a-spin>
  </a-modal>
</template>

<script>
export default {
  name: ''
}
</script>
<script setup>
import { ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import ResidentProcessApi from '@/common/api/residentProcess.js'

const processVisible = defineModel('open')
const processStr = ref('')
const loading = ref(false)
const loadingData = ref(false)

// 监听弹窗打开，加载已保存的进程列表
watch(processVisible, async (newVal) => {
  if (newVal) {
    await loadProcessList()
  }
})

// 加载已保存的进程列表
const loadProcessList = async () => {
  try {
    loadingData.value = true
    const response = await ResidentProcessApi.getResidentProcessList()

    if (response?.status === 'success') {
      const processes = response.data || []
      // 将进程列表转换为换行分隔的字符串
      processStr.value = processes.map((p) => p.name).join('\n')
    }
  } catch (error) {
    console.error('加载进程列表失败:', error)
    // 加载失败不显示错误提示，只在控制台记录
  } finally {
    loadingData.value = false
  }
}

const onOk = async () => {
  if (!processStr.value || !processStr.value.trim()) {
    processVisible.value = false
    return
  }

  // 支持英文逗号和换行符分割
  const processList = processStr.value
    .split(/[,\n]+/) // 使用正则匹配英文逗号或换行符
    .map((item) => item.trim()) // 去除每项的首尾空格
    .filter((item) => item.length > 0) // 过滤空字符串

  if (processList.length === 0) {
    message.warning('请输入至少一个进程名称')
    return
  }

  try {
    loading.value = true

    // 调用批量创建API
    const response = await ResidentProcessApi.batchCreateResidentProcesses(
      processList
    )

    if (response?.status === 'success') {
      const result = response.data

      // 构建提示消息
      const messageParts = []
      if (result.success_count > 0) {
        messageParts.push(`新增: ${result.success_count} 个`)
      }
      if (result.skipped_count > 0) {
        messageParts.push(`已存在: ${result.skipped_count} 个`)
      }
      if (result.deleted_count > 0) {
        messageParts.push(`删除: ${result.deleted_count} 个`)
      }
      if (result.failed_count > 0) {
        messageParts.push(`失败: ${result.failed_count} 个`)
      }

      const successMessage =
        messageParts.length > 0
          ? `保存完成！${messageParts.join('，')}`
          : '保存完成！'

      message.success(successMessage)

      // 如果有失败的，显示失败原因
      if (result.failed_count > 0 && result.details) {
        const failedProcesses = result.details.filter(
          (d) => d.status === 'failed'
        )
        if (failedProcesses.length > 0) {
          console.warn('失败的进程:', failedProcesses)
        }
      }

      // 保存成功后重新加载进程列表
      await loadProcessList()
      processVisible.value = false
    } else {
      message.error(response?.message || '保存失败')
    }
  } catch (error) {
    console.error('保存常驻进程失败:', error)
    message.error(error?.response?.message || '保存失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>
