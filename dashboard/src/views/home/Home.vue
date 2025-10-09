<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[12px]">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-[12px]">
        <div class="bg-blue-100 rounded-lg p-4 shadow">
          <div class="text-2xl font-bold text-blue-800">
            {{ statistics.totalDevices }}
          </div>
          <div class="text-gray-600">总设备数</div>
        </div>
        <div class="bg-green-100 rounded-lg p-4 shadow">
          <div class="text-2xl font-bold text-green-800">
            {{ statistics.onlineDevices }}
          </div>
          <div class="text-gray-600">在线设备</div>
        </div>
        <div class="bg-red-100 rounded-lg p-4 shadow">
          <div class="text-2xl font-bold text-red-800">
            {{ statistics.offlineDevices }}
          </div>
          <div class="text-gray-600">离线设备</div>
        </div>
      </div>
      <!-- 设备列表 -->
      <div class="bg-white rounded-lg" style="height: calc(100% - 78px)">
        <div class="px-4 pb-[4px] border-b border-gray-200 layout-left-center">
          <div class="text-lg font-medium layout-left-center h-[40px]">
            设备列表
          </div>
        </div>
        <div class="overflow-auto" style="height: calc(100% - 45px)">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  设备名称
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  IP地址
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  MAC地址
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  操作系统
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  状态
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  最后更新
                </th>
                <th
                  scope="col"
                  class="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider"
                >
                  设备类型
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="device in devices" :key="device.mac_address">
                <td
                  class="px-6 py-4 whitespace-nowrap font-medium text-gray-900"
                >
                  {{ device.hostname || '未知设备' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                  {{ device.ip_address || '未知' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                  {{ device.mac_address || '未知' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                  {{ formatOSInfo(device) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="
                      device.online
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    "
                    class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                  >
                    {{ device.online ? '在线' : '离线' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                  {{ formatTimestamp(device.timestamp) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                  {{ device.type || '未设置' }}
                </td>
              </tr>
              <tr v-if="devices.length === 0">
                <td colspan="8" class="px-6 py-4 text-center text-gray-500">
                  暂无设备数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DeviceApi from '@/common/api/device.js'

// 设备统计数据
const statistics = ref({
  totalDevices: 0,
  onlineDevices: 0,
  offlineDevices: 0
})

// 设备列表
const devices = ref([])

// 格式化操作系统信息
const formatOSInfo = (device) => {
  if (!device.os_name) return '未知'

  let osInfo = device.os_name
  if (device.os_version) {
    osInfo += ' ' + device.os_version
  }
  if (device.os_architecture) {
    osInfo += ' (' + device.os_architecture + ')'
  }

  return osInfo
}

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '未知'

  // 如果是完整的日期时间字符串，则格式化为更友好的显示
  if (timestamp.includes(' ')) {
    return timestamp.replace(' ', '\n')
  }

  return timestamp
}

// 获取设备统计数据
const fetchDeviceStatistics = async () => {
  try {
    const response = await DeviceApi.getDevicesList()

    // 处理API返回的数据结构
    devices.value = response.data || []

    // 计算统计信息
    statistics.value.totalDevices = devices.value.length
    statistics.value.onlineDevices = devices.value.filter(
      (device) => device.online
    ).length
    statistics.value.offlineDevices =
      statistics.value.totalDevices - statistics.value.onlineDevices
  } catch (error) {
    console.error('获取设备统计信息失败:', error)
    // 出错时使用模拟数据
    devices.value = []

    statistics.value.totalDevices = devices.value.length
    statistics.value.onlineDevices = devices.value.filter(
      (device) => device.online
    ).length
    statistics.value.offlineDevices =
      statistics.value.totalDevices - statistics.value.onlineDevices
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchDeviceStatistics()
})
</script>

<style lang="less" scoped></style>
