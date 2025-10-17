<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[12px] pt-[0]">
      <a-tabs class="size-full" v-model:activeKey="activeKey">
        <a-tab-pane class="size-full" key="1" tab="探针设备">
          <ProbeDevicesTab
            :loading="loading"
            :pagination="pagination"
            v-model:changedTimestamps="changedTimestamps"
            @handleTableChange="handleTableChange"
            @clearFilter="clearFilter"
          />
        </a-tab-pane>
        <a-tab-pane key="2" tab="SNMP设备" force-render>
          <SNMPDevicesTab
            :switches="switches"
            :loading="loading"
            :pagination="pagination"
            @fetchSwitches="fetchSwitches"
            @handleTableChange="handleTableChange"
          />
        </a-tab-pane>
      </a-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import DeviceApi from '@/common/api/device.js'
import SwitchApi from '@/common/api/switch.js'
import { message } from 'ant-design-vue'
import { onBeforeRouteLeave } from 'vue-router'
import ProbeDevicesTab from './ProbeDevicesTab.vue'
import SNMPDevicesTab from './SNMPDevicesTab.vue'

// 设备列表
const switches = ref([])

// 从localStorage获取保存的标签页状态，如果没有则默认为'1'
const savedActiveKey = localStorage.getItem('devices-active-tab') || '1'
const activeKey = ref(savedActiveKey)

// 表格分页和加载状态
const pagination = {
  pageSize: 30
}
const loading = ref(false)

// 用于跟踪时间戳变更状态
const changedTimestamps = ref({})

// 清除筛选
const clearFilter = () => {
  // 在这里可以添加清除筛选的逻辑
}

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  // 可以在这里处理分页、排序和筛选逻辑
  console.log('Table changed:', pag, filters, sorter)
}

// 监听activeKey变化，保存到localStorage
watch(activeKey, (newVal) => {
  localStorage.setItem('devices-active-tab', newVal)
})

// 路由离开前重置devices-active-tab为1
onBeforeRouteLeave((to, from) => {
  localStorage.setItem('devices-active-tab', '1')
})

// 获取交换机列表
const fetchSwitches = async () => {
  try {
    const response = await SwitchApi.getSwitchesList()
    switches.value = response.data || []
  } catch (error) {
    console.error('获取交换机列表失败:', error)
    message.error('获取交换机列表失败: ' + error.message)
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchSwitches()
})
</script>

<style lang="less">
.modal-max-height {
  :deep(.ant-modal) {
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }

  :deep(.ant-modal-content) {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-height: 90vh;
  }

  :deep(.ant-modal-body) {
    flex: 1;
    overflow-y: auto;
    max-height: calc(90vh - 110px); // 减去标题和footer的高度
  }
}

// 添加flex相关的工具类
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.flex-1 {
  flex: 1;
}

.overflow-auto {
  overflow: auto;
}

.border-t {
  border-top-width: 1px;
}

.border-gray-200 {
  border-color: #e5e7eb;
}

.pt-2 {
  padding-top: 0.5rem;
}
</style>
