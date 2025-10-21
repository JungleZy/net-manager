<template>
  <a-modal
    v-model:open="processVisible"
    title="进程管理"
    width="600px"
    @ok="onOk"
    @cancel="processVisible = false"
  >
    <a-textarea
      placeholder="请输入需要监控的进程名称，多个进程用英文逗号隔开或者换行"
      v-model:value="processStr"
      :auto-size="{ minRows: 10, maxRows: 10 }"
    ></a-textarea>
  </a-modal>
</template>

<script>
export default {
  name: ''
}
</script>
<script setup>
import { ref } from 'vue'

const processVisible = defineModel('open')
const processStr = ref('')

const onOk = () => {
  if (!processStr.value || !processStr.value.trim()) {
    processVisible.value = false
    return
  }

  // 支持英文逗号和换行符分割
  const processList = processStr.value
    .split(/[,\n]+/) // 使用正则匹配英文逗号或换行符
    .map((item) => item.trim()) // 去除每项的首尾空格
    .filter((item) => item.length > 0) // 过滤空字符串

  console.log('进程列表:', processList)


  // 清空输入并关闭弹窗
  processStr.value = ''
  processVisible.value = false
}
</script>
