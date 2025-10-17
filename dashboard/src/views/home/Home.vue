<template>
  <div class="p-[12px] size-full overflow-auto">
    <ServerPerformance />

    <div class="w-full bg-white rounded-lg shadow p-[12px]">
      <h2 class="text-lg font-semibold mb-[12px]">设备统计</h2>
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
      <a-empty v-if="devices.length === 0 && switchesWithStatus.length === 0">
        <template #description>
          <div class="text-center">暂无设备</div>
        </template>
      </a-empty>
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
                    <strong>IP地址:</strong> <IPDisplay :ips="device.ips" />
                  </p>
                </div>
              </a-card>
            </a-col>
            <a-col
              v-for="switchItem in switchesWithStatus"
              :key="switchItem.id"
              :span="4"
              style="margin-bottom: 16px"
            >
              <a-card hoverable>
                <div class="switch-card">
                  <h3 class="layout-side">
                    {{ switchItem.device_name || '未知设备' }}
                    <a-tag
                      v-if="switchItem.status === 'success'"
                      color="success"
                      style="margin-right: 0"
                      :title="
                        switchItem.lastUpdate
                          ? `最后更新: ${new Date(
                              switchItem.lastUpdate
                            ).toLocaleString('zh-CN')}`
                          : ''
                      "
                    >
                      在线
                    </a-tag>
                    <a-tag
                      v-else-if="switchItem.status === 'error'"
                      color="error"
                      style="margin-right: 0"
                      :title="switchItem.errorMsg || '设备离线'"
                    >
                      离线
                    </a-tag>
                    <a-tag v-else color="default" style="margin-right: 0">
                      未知
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
import {
  ref,
  onMounted,
  onUnmounted,
  h,
  defineComponent,
  computed,
  shallowRef
} from 'vue'
import { Tooltip } from 'ant-design-vue'
import DeviceApi from '@/common/api/device'
import SwitchApi from '@/common/api/switch'
import { formatOSInfo } from '@/common/utils/Utils.js'
import SNMPStorage from '@/common/utils/SNMPStorage.js'
import { PubSub } from '@/common/utils/PubSub'
import { wsCode } from '@/common/ws/Ws'
import ServerPerformance from './ServerPerformance.vue'

// IP地址显示组件
const IPDisplay = defineComponent({
  name: 'IPDisplay',
  props: {
    ips: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    /**
     * 格式化IP地址数组
     * @param {Array} ips - IP地址数组，格式: ["接口名: IP地址", ...]
     * @returns {Array} - 解析后的IP地址数组
     */
    const formatIPs = (ips) => {
      if (!ips || !Array.isArray(ips)) return []

      return ips
        .map((ipStr) => {
          // 解析 "接口名: IP地址" 格式
          if (typeof ipStr === 'string' && ipStr.includes(':')) {
            const parts = ipStr.split(':')
            // 返回IP地址部分（去除空格）
            return parts.length > 1 ? parts[1].trim() : ipStr.trim()
          }
          return ipStr
        })
        .filter((ip) => ip) // 过滤空值
    }

    return () => {
      if (!props.ips || !Array.isArray(props.ips) || props.ips.length === 0) {
        return h('span', 'N/A')
      }

      // 解析所有IP地址
      const parsedIPs = formatIPs(props.ips)

      if (parsedIPs.length === 0) {
        return h('span', 'N/A')
      }

      // 如果只有一个IP地址，直接显示
      if (parsedIPs.length === 1) {
        return h('span', parsedIPs[0])
      }

      // 如果有多个IP地址，显示第一个并提示还有更多，Tooltip中一行显示一个IP
      return h('span', { style: { display: 'inline' } }, [
        h('span', parsedIPs[0]),
        h(
          Tooltip,
          {
            title: h(
              'div',
              {
                style: {
                  textAlign: 'left'
                }
              },
              parsedIPs.map((ip) => h('div', ip))
            )
          },
          {
            default: () =>
              h(
                'span',
                {
                  style: {
                    color: '#1890ff',
                    marginLeft: '5px',
                    cursor: 'pointer'
                  }
                },
                `(+${parsedIPs.length - 1})`
              )
          }
        )
      ])
    }
  }
})

export default {
  name: 'Home',
  components: {
    IPDisplay,
    ServerPerformance
  },
  setup() {
    const statistics = ref({
      deviceCount: 0,
      onlineCount: 0,
      offlineCount: 0,
      switchCount: 0
    })

    const devices = ref([])
    const switches = ref([])

    // SNMP设备状态数据 - 使用 shallowRef 优化大对象性能（以switch_id为key）
    const snmpDevicesStatus = shallowRef({})

    // 状态文本映射
    const STATUS_TEXT_MAP = {
      success: '在线',
      error: '离线',
      unknown: '未知'
    }

    // 交换机列表增强状态 - 根据switch_id匹配状态
    const switchesWithStatus = computed(() => {
      const statusData = snmpDevicesStatus.value
      return switches.value.map((sw) => {
        // 使用switch_id（数据库主键）匹配状态
        const snmpData = statusData[sw.id]
        return {
          ...sw,
          status: snmpData?.type || 'unknown',
          statusText:
            STATUS_TEXT_MAP[snmpData?.type] || STATUS_TEXT_MAP.unknown,
          lastUpdate: snmpData?.updateTime || null,
          errorMsg: snmpData?.error || null
        }
      })
    })

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

    // 加载SNMP设备状态 - 使用新的buildStatusMap方法
    const loadSNMPDevicesStatus = async () => {
      try {
        const statusMap = await SNMPStorage.buildStatusMap()
        if (statusMap && typeof statusMap === 'object') {
          snmpDevicesStatus.value = statusMap
          const count = Object.keys(statusMap).length
          if (count > 0) {
            console.log(`Home: 加载SNMP设备状态: ${count}个设备`)
          }
        }
      } catch (error) {
        console.error('Home: 加载SNMP设备状态失败:', error)
        // 失败时保持原有数据，不清空
      }
    }

    // WebSocket消息处理器 - 处理单设备实时更新
    const handleDeviceUpdate = async (deviceData) => {
      try {
        const switchId = deviceData.switch_id
        if (!switchId) {
          console.warn('Home: 设备数据缺少switch_id:', deviceData)
          return
        }

        // 获取当前状态映射
        const currentStatus = { ...snmpDevicesStatus.value }

        // 如果该switch_id不存在，初始化结构
        if (!currentStatus[switchId]) {
          currentStatus[switchId] = {
            type: 'unknown',
            updateTime: null,
            error: null,
            device_info: {},
            interface_info: []
          }
        }

        // 更新设备信息状态
        currentStatus[switchId].type = deviceData.type
        currentStatus[switchId].updateTime = new Date().toISOString()
        currentStatus[switchId].error = deviceData.error || null
        currentStatus[switchId].device_info = deviceData.device_info || {}

        // 更新状态
        snmpDevicesStatus.value = currentStatus

        console.debug(
          `Home: 设备状态更新: switch_id=${switchId}, status=${deviceData.type}`
        )
      } catch (error) {
        console.error('Home: 处理设备更新失败:', error)
      }
    }

    // WebSocket消息处理器 - 处理单接口实时更新
    const handleInterfaceUpdate = async (interfaceData) => {
      try {
        const switchId = interfaceData.switch_id
        if (!switchId) {
          console.warn('Home: 接口数据缺少switch_id:', interfaceData)
          return
        }

        // 获取当前状态映射
        const currentStatus = { ...snmpDevicesStatus.value }

        // 如果该switch_id不存在，初始化结构
        if (!currentStatus[switchId]) {
          currentStatus[switchId] = {
            type: 'unknown',
            updateTime: null,
            error: null,
            device_info: {},
            interface_info: []
          }
        }

        // 更新接口信息状态（仅当设备信息不存在时更新type）
        if (
          !currentStatus[switchId].device_info ||
          Object.keys(currentStatus[switchId].device_info).length === 0
        ) {
          currentStatus[switchId].type = interfaceData.type
        }
        currentStatus[switchId].updateTime = new Date().toISOString()
        currentStatus[switchId].interface_info =
          interfaceData.interface_info || []

        // 更新状态
        snmpDevicesStatus.value = currentStatus

        console.debug(
          `Home: 接口状态更新: switch_id=${switchId}, 接口数=${
            interfaceData.interface_info?.length || 0
          }`
        )
      } catch (error) {
        console.error('Home: 处理接口更新失败:', error)
      }
    }

    onMounted(() => {
      fetchData()

      // 异步加载SNMP状态，不阻塞组件渲染
      loadSNMPDevicesStatus().catch((err) => {
        console.error('Home: 初始化SNMP状态失败:', err)
      })

      // 订阅SNMP设备实时更新
      PubSub.subscribe(wsCode.SNMP_DEVICE_UPDATE, handleDeviceUpdate)
      // 订阅SNMP接口实时更新
      PubSub.subscribe(wsCode.SNMP_INTERFACE_UPDATE, handleInterfaceUpdate)
      console.log('Home: SNMP实时状态订阅已启动')
    })

    // 组件卸载 - 清理资源
    onUnmounted(() => {
      PubSub.unsubscribe(wsCode.SNMP_DEVICE_UPDATE)
      PubSub.unsubscribe(wsCode.SNMP_INTERFACE_UPDATE)
      // 清空状态，释放内存
      snmpDevicesStatus.value = {}
      console.log('Home: SNMP实时状态订阅已取消')
    })

    return {
      statistics,
      devices,
      switches,
      switchesWithStatus,
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
