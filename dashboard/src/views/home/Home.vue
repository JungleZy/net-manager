<template>
  <div class="p-[12px] size-full">
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-[12px]">
      <div class="bg-blue-100 rounded-lg p-4 shadow">
        <div class="text-2xl font-bold text-blue-800">
          {{ statistics.deviceCount }}
        </div>
        <div class="text-gray-600">总设备数</div>
      </div>
      <div class="bg-green-100 rounded-lg p-4 shadow">
        <div class="text-2xl font-bold text-green-800">
          {{ statistics.onlineCount }}
        </div>
        <div class="text-gray-600">在线设备</div>
      </div>
      <div class="bg-red-100 rounded-lg p-4 shadow">
        <div class="text-2xl font-bold text-red-800">
          {{ statistics.offlineCount }}
        </div>
        <div class="text-gray-600">离线设备</div>
      </div>
    </div>
    <div
      class="w-full bg-white rounded-lg shadow p-[12px]"
      style="height: calc(100% - 79px)"
    >
      <div class="device-list size-full">
        <div class="size-full">
          <a-row :gutter="16">
            <a-col
              v-for="device in devices"
              :key="device.mac_address"
              :span="4"
              style="margin-bottom: 16px"
            >
              <a-card hoverable>
                <div class="device-card">
                  <h3 class="layout-side">
                    {{ device.hostname || '未知设备' }}
                    <a-tag
                      :color="device.online ? 'green' : 'red'"
                      style="margin-right: 0"
                    >
                      {{ device.online ? '在线' : '离线' }}
                    </a-tag>
                  </h3>
                  <p>
                    <strong>IP地址:</strong>
                    {{ device.ip_address || 'N/A' }}
                  </p>
                </div>
              </a-card>
            </a-col>
            <a-col
              v-for="switchItem in switches"
              :key="switchItem.id"
              :span="4"
              style="margin-bottom: 16px"
            >
              <a-card hoverable>
                <div class="switch-card">
                  <h3 class="layout-side">
                    {{ switchItem.device_name || '未知设备' }}
                    <a-tag
                      :color="switchItem.online ? 'green' : 'red'"
                      style="margin-right: 0"
                    >
                      {{ switchItem.online ? '在线' : '离线' }}
                    </a-tag>
                  </h3>
                  <p><strong>IP地址:</strong> {{ switchItem.ip }}</p>
                </div>
              </a-card>
            </a-col>
          </a-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import DeviceApi from '@/common/api/device'
import SwitchApi from '@/common/api/switch'
import { formatOSInfo } from '@/common/utils/Utils.js'

export default {
  name: 'Home',
  setup() {
    const statistics = ref({
      deviceCount: 0,
      onlineCount: 0,
      offlineCount: 0,
      switchCount: 0
    })

    const devices = ref([])
    const switches = ref([])

    const formatOSInfo = (osInfo) => {
      if (!osInfo) return '未知'
      return `${osInfo.os_name || '未知'} ${osInfo.os_version || ''}`
    }

    const formatTimestamp = (timestamp) => {
      if (!timestamp) return '未知'
      return new Date(timestamp).toLocaleString('zh-CN')
    }

    const fetchDeviceStatistics = async () => {
      try {
        const response = await DeviceApi.getDevicesList()
        devices.value = response.data || []
        const deviceList = response.data || []

        statistics.value.deviceCount = deviceList.length
        statistics.value.onlineCount = deviceList.filter(
          (device) => device.online
        ).length
        statistics.value.offlineCount = deviceList.filter(
          (device) => !device.online
        ).length
      } catch (error) {
        console.error('获取设备统计信息失败:', error)
      }
    }

    const fetchSwitchStatistics = async () => {
      try {
        const response = await SwitchApi.getSwitchesList()
        const switchList = response.data || []
        switches.value = response.data || []
        statistics.value.switchCount = switchList.length
      } catch (error) {
        console.error('获取交换机统计信息失败:', error)
      }
    }

    const fetchData = async () => {
      await Promise.all([fetchDeviceStatistics(), fetchSwitchStatistics()])
    }

    onMounted(() => {
      fetchData()
    })

    return {
      statistics,
      devices,
      switches,
      formatOSInfo,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #1890ff;
  font-size: 2em;
}

.statistics {
  margin-bottom: 30px;
}

.statistic-card {
  text-align: center;
}

.statistic-card h3 {
  margin-bottom: 10px;
  color: #666;
}

.statistic-value {
  font-size: 2em;
  font-weight: bold;
  color: #1890ff;
  margin: 0;
}

.device-list h2 {
  margin-bottom: 20px;
  color: #333;
}

.device-card h3,
.switch-card h3 {
  margin-top: 0;
  color: #1890ff;
}

.device-card p,
.switch-card p {
  margin: 8px 0;
}
</style>
