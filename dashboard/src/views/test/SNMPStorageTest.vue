<template>
  <div class="snmp-storage-test">
    <h1>SNMP本地存储测试</h1>

    <div class="section">
      <h2>统计信息</h2>
      <div v-if="summary">
        <p>总设备数: {{ summary.total }}</p>
        <p>在线设备: {{ summary.success }}</p>
        <p>离线设备: {{ summary.error }}</p>
        <p>最后更新: {{ summary.lastUpdateTime }}</p>
      </div>
      <button @click="loadSummary">刷新统计</button>
    </div>

    <div class="section">
      <h2>设备数量统计</h2>
      <div v-if="deviceCount">
        <p>总数: {{ deviceCount.total }}</p>
        <p>在线: {{ deviceCount.online }}</p>
        <p>离线: {{ deviceCount.offline }}</p>
      </div>
      <button @click="loadDeviceCount">刷新数量</button>
    </div>

    <div class="section">
      <h2>设备搜索</h2>
      <input
        v-model="searchText"
        placeholder="输入IP或设备名称..."
        @input="handleSearch"
      />
      <p>找到 {{ searchResults.length }} 个设备</p>
      <ul>
        <li v-for="device in searchResults.slice(0, 5)" :key="device.ip">
          {{ device.ip }} - {{ device.device_info?.name || '未知' }} [{{
            device.type === 'success' ? '在线' : '离线'
          }}]
        </li>
      </ul>
    </div>

    <div class="section">
      <h2>在线设备列表</h2>
      <button @click="loadOnlineDevices">加载在线设备</button>
      <p>在线设备数: {{ onlineDevices.length }}</p>
      <ul>
        <li v-for="device in onlineDevices.slice(0, 10)" :key="device.ip">
          {{ device.ip }} - {{ device.device_info?.name || '未知' }}
        </li>
      </ul>
    </div>

    <div class="section">
      <h2>离线设备列表</h2>
      <button @click="loadOfflineDevices">加载离线设备</button>
      <p>离线设备数: {{ offlineDevices.length }}</p>
      <ul>
        <li v-for="device in offlineDevices.slice(0, 10)" :key="device.ip">
          {{ device.ip }} - {{ device.error }}
        </li>
      </ul>
    </div>

    <div class="section">
      <h2>所有设备</h2>
      <button @click="loadAllDevices">加载所有设备</button>
      <p>设备总数: {{ Object.keys(allDevices).length }}</p>
    </div>

    <div class="section">
      <h2>数据管理</h2>
      <button @click="clearAllData" style="background-color: #ff4d4f">
        清除所有数据
      </button>
      <button @click="exportData">导出数据</button>
    </div>

    <div class="section">
      <h2>WebSocket监听</h2>
      <p>接收消息数: {{ wsMessageCount }}</p>
      <p>最后更新: {{ lastWsUpdate }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import SNMPStorage from '@/common/utils/SNMPStorage'
import { PubSub } from '@/common/utils/PubSub'
import { wsCode } from '@/common/ws/Ws'

const summary = ref(null)
const deviceCount = ref(null)
const searchText = ref('')
const searchResults = ref([])
const onlineDevices = ref([])
const offlineDevices = ref([])
const allDevices = ref({})
const wsMessageCount = ref(0)
const lastWsUpdate = ref('')

let unsubscribe = null

// 加载统计信息
const loadSummary = async () => {
  summary.value = await SNMPStorage.getSummary()
  console.log('统计信息:', summary.value)
}

// 加载设备数量
const loadDeviceCount = async () => {
  deviceCount.value = await SNMPStorage.getDeviceCount()
  console.log('设备数量:', deviceCount.value)
}

// 搜索设备
const handleSearch = async () => {
  searchResults.value = await SNMPStorage.searchDevices(searchText.value)
  console.log('搜索结果:', searchResults.value.length)
}

// 加载在线设备
const loadOnlineDevices = async () => {
  onlineDevices.value = await SNMPStorage.getOnlineDevices()
  console.log('在线设备:', onlineDevices.value.length)
}

// 加载离线设备
const loadOfflineDevices = async () => {
  offlineDevices.value = await SNMPStorage.getOfflineDevices()
  console.log('离线设备:', offlineDevices.value.length)
}

// 加载所有设备
const loadAllDevices = async () => {
  allDevices.value = await SNMPStorage.getAllDevices()
  console.log('所有设备:', Object.keys(allDevices.value).length)
}

// 清除所有数据
const clearAllData = async () => {
  if (confirm('确定要清除所有SNMP设备数据吗？')) {
    await SNMPStorage.clearAll()
    // 重新加载
    await loadAllData()
    alert('数据已清除')
  }
}

// 导出数据
const exportData = async () => {
  const devices = await SNMPStorage.getAllDevices()
  const summaryData = await SNMPStorage.getSummary()

  const exportObj = {
    devices,
    summary: summaryData,
    exportTime: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(exportObj, null, 2)], {
    type: 'application/json'
  })

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `snmp-devices-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 加载所有数据
const loadAllData = async () => {
  await loadSummary()
  await loadDeviceCount()
  await loadAllDevices()
}

onMounted(() => {
  // 初始加载
  loadAllData()

  // 订阅WebSocket消息
  unsubscribe = PubSub.subscribe(wsCode.SNMP_DEVICE_BATCH, async (data) => {
    wsMessageCount.value++
    lastWsUpdate.value = new Date().toLocaleString('zh-CN')
    console.log('收到SNMP批量更新:', data)

    // 重新加载数据
    await loadAllData()
  })
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
})
</script>

<style scoped>
.snmp-storage-test {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #1890ff;
  margin-bottom: 30px;
}

.section {
  background: #fff;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 10px;
}

button {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
  margin-bottom: 10px;
}

button:hover {
  background-color: #40a9ff;
}

input {
  width: 300px;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-bottom: 10px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 8px;
  background: #f5f5f5;
  margin-bottom: 5px;
  border-radius: 4px;
}

p {
  margin: 10px 0;
  color: #666;
}
</style>
