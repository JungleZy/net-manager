<template>
  <a-modal
    :open="visible"
    :title="'服务详情 - ' + deviceName"
    @cancel="handleCancel"
    @update:open="handleUpdateOpen"
    centered
    width="660px"
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
          找到 {{ filteredServicesList.length }} 条结果
        </div>
      </div>
      <div
        class="flex-1 overflow-hidden"
        v-if="filteredServicesList.length > 0"
      >
        <VList
          class="scroller"
          :data="filteredServicesList"
          #default="{ item, index }"
        >
          <div class="service-item">
            <div
              style="
                width: 100%;
                padding: 12px 0;
                border-bottom: 1px solid #f0f0f0;
              "
            >
              <div>
                <strong>{{ index + 1 }}. PID: {{ item.pid || 'N/A' }}</strong>
                - {{ item.process_name || '未知进程' }}
                <span style="margin-left: 10px; font-size: 12px; color: #666"
                  >({{ item.status }})</span
                >
              </div>
              <div style="font-size: 12px; color: #666">
                协议: {{ item.protocol }} | 地址: {{ item.local_address }}
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
  servicesList: {
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

// 过滤后的服务列表
const filteredServicesList = computed(() => {
  if (!searchText.value) {
    return props.servicesList
  }

  const keyword = searchText.value.toLowerCase().trim()
  return props.servicesList.filter((item) => {
    const pid = (item.pid || '').toString().toLowerCase()
    const processName = (item.process_name || '').toLowerCase()
    const protocol = (item.protocol || '').toLowerCase()
    const localAddress = (item.local_address || '').toLowerCase()
    const status = (item.status || '').toLowerCase()

    return (
      pid.includes(keyword) ||
      processName.includes(keyword) ||
      protocol.includes(keyword) ||
      localAddress.includes(keyword) ||
      status.includes(keyword)
    )
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

.service-item {
  min-height: 66px;
}
</style>
