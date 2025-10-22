<template>
  <a-modal
    :open="visible"
    :title="'进程详情 - ' + deviceName"
    @cancel="handleCancel"
    @update:open="handleUpdateOpen"
    width="660px"
    centered
    :body-style="{ height: height - 300 + 'px', minHeight: '300px' }"
    :footer="null"
    :destroyOnClose="true"
  >
    <div class="flex flex-col size-full">
      <!-- 搜索框 -->
      <div class="mb-3">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索进程名、PID、协议或地址..."
          allow-clear
          @change="handleSearch"
        />
        <div v-if="searchText" class="text-xs text-gray-500 mt-1">
          找到 {{ filteredProcessesList.length }} 条结果
        </div>
      </div>
      <div class="flex-1 overflow-hidden">
        <VList
          class="scroller"
          :data="filteredProcessesList"
          #default="{ item, index }"
        >
          <div class="process-item">
            <div
              style="
                width: 100%;
                padding: 12px 0;
                border-bottom: 1px solid #f0f0f0;
              "
            >
              <div>
                <strong>{{ index + 1 }}. PID: {{ item.pid }}</strong>
                - {{ item.name }}
                <span style="margin-left: 10px; font-size: 12px; color: #666"
                  >({{ item.status }})</span
                >
              </div>
              <div style="font-size: 12px; color: #666">
                CPU: {{ item.cpu_percent }}% | 内存: {{ item.memory_percent }}%
              </div>
              <!-- 显示端口信息 -->
              <div
                v-if="item.ports && item.ports.length > 0"
                style="font-size: 12px; color: #888; margin-top: 5px"
              >
                <div v-for="(port, portIndex) in item.ports" :key="portIndex">
                  {{ port.protocol }}: {{ port.local_address }}
                </div>
              </div>
            </div>
          </div>
        </VList>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { VList } from 'virtua/vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  processesList: {
    type: Array,
    default: () => []
  },
  deviceName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:visible', 'cancel'])

const { height } = useWindowSize()
const searchText = ref('')

// 过滤后的进程列表
const filteredProcessesList = computed(() => {
  if (!searchText.value) {
    return props.processesList
  }

  const keyword = searchText.value.toLowerCase().trim()
  return props.processesList.filter((item) => {
    const pid = (item.pid || '').toString().toLowerCase()
    const name = (item.name || '').toLowerCase()
    const status = (item.status || '').toLowerCase()
    const cpuPercent = (item.cpu_percent || '').toString().toLowerCase()
    const memoryPercent = (item.memory_percent || '').toString().toLowerCase()

    // 搜索基本信息
    let matched =
      pid.includes(keyword) ||
      name.includes(keyword) ||
      status.includes(keyword) ||
      cpuPercent.includes(keyword) ||
      memoryPercent.includes(keyword)

    // 搜索端口信息
    if (!matched && item.ports && item.ports.length > 0) {
      matched = item.ports.some((port) => {
        const protocol = (port.protocol || '').toLowerCase()
        const localAddress = (port.local_address || '').toLowerCase()
        return protocol.includes(keyword) || localAddress.includes(keyword)
      })
    }

    return matched
  })
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑由 computed 自动处理
}

// 关闭模态框
const handleCancel = () => {
  emit('update:visible', false)
  emit('cancel')
}

// 处理模态框开启状态变化
const handleUpdateOpen = (open) => {
  emit('update:visible', open)
}
</script>

<style lang="less" scoped>
.scroller {
  height: 100%;
}

.process-item {
  min-height: 66px;
}
</style>
