<template>
  <div class="p-[12px] size-full overflow-auto">
    <ServerPerformance />

    <div class="w-full bg-white rounded-lg shadow p-[12px]">
      <h2 class="text-lg font-semibold mb-[12px]">设备统计</h2>
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-[12px]">
        <div class="bg-blue-100 rounded-lg p-4 shadow">
          <div class="text-2xl font-bold text-blue-800">
            {{ totalCount }}
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
                  <div class="layout-side">
                    <h3
                      class="truncate"
                      style="width: calc(100% - 42px); margin: 0"
                    >
                      {{ device.hostname || '未知设备' }}
                    </h3>
                    <a-tag
                      :color="device.online ? 'green' : 'red'"
                      style="margin-right: 0"
                    >
                      {{ device.online ? '在线' : '离线' }}
                    </a-tag>
                  </div>
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
                  <div class="layout-side">
                    <h3
                      class="truncate"
                      style="width: calc(100% - 42px); margin: 0"
                    >
                      {{ switchItem.device_name || '未知设备' }}
                    </h3>
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
                      v-else
                      color="error"
                      style="margin-right: 0"
                      :title="switchItem.errorMsg || '设备离线'"
                    >
                      离线
                    </a-tag>
                  </div>
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
  shallowRef,
  watch
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

    // 使用 shallowRef 承载大数组，减少深层响应式追踪开销
    const devices = shallowRef([])
    const switches = shallowRef([])

    // 基于列表的设备/交换机数量计算，减少手动赋值风险
    const deviceCount = computed(() =>
      Array.isArray(devices.value) ? devices.value.length : 0
    )
    const switchCount = computed(() =>
      Array.isArray(switches.value) ? switches.value.length : 0
    )
    const totalCount = computed(() => deviceCount.value + switchCount.value)

    // 设备与交换机在线/离线计数（用于聚合统计）
    const deviceOnlineCount = ref(0)
    const deviceOfflineCount = ref(0)
    const switchOnlineCount = ref(0)
    const switchOfflineCount = ref(0)

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
        const deviceList = response.data || []
        devices.value = deviceList

        // deviceCount 由计算属性基于 devices 列表自动得到
        // 单次遍历计算在线/离线，减少两次过滤开销
        const counts = deviceList.reduce(
          (acc, d) => {
            if (d && d.online) acc.online += 1
            else acc.offline += 1
            return acc
          },
          { online: 0, offline: 0 }
        )
        deviceOnlineCount.value = counts.online
        deviceOfflineCount.value = counts.offline
      } catch (error) {
        console.error('获取设备统计信息失败:', error)
      }
    }

    const fetchSwitchStatistics = async () => {
      try {
        const response = await SwitchApi.getSwitchesList()
        const switchList = response.data || []
        switches.value = switchList
        // switchCount 由计算属性基于 switches 列表自动得到
        // 单次遍历计算在线/离线
        const counts = switchList.reduce(
          (acc, d) => {
            if (d && d.online) acc.online += 1
            else acc.offline += 1
            return acc
          },
          { online: 0, offline: 0 }
        )
        switchOnlineCount.value = counts.online
        switchOfflineCount.value = counts.offline
      } catch (error) {
        console.error('获取交换机统计信息失败:', error)
      }
    }

    // 计算 SNMP 设备在线/离线数量（基于 snmpDevicesStatus.type）
    const getSnmpOnlineCount = () => {
      const statusData = snmpDevicesStatus.value || {}
      return Object.values(statusData).filter((d) => d?.type === 'success')
        .length
    }
    const getSnmpOfflineCount = () => {
      const statusData = snmpDevicesStatus.value || {}
      return Object.values(statusData).filter((d) => d?.type !== 'success')
        .length
    }

    // 聚合计算：设备 + SNMP 交换机
    const recomputeStatistics = () => {
      statistics.value.onlineCount =
        deviceOnlineCount.value + getSnmpOnlineCount()
      statistics.value.offlineCount =
        deviceOfflineCount.value + getSnmpOfflineCount()
    }

    // 轻量去抖：在高频 SNMP 推送时合并计算，避免重复渲染
    let _recomputeTimer = null
    const scheduleRecompute = () => {
      if (_recomputeTimer) return
      _recomputeTimer = setTimeout(() => {
        try {
          recomputeStatistics()
        } finally {
          _recomputeTimer = null
        }
      }, 100)
    }

    const fetchData = async () => {
      await Promise.all([fetchDeviceStatistics(), fetchSwitchStatistics()])
      // 首页在线/离线统计 = devices + SNMP 交换机
      recomputeStatistics()
    }

    // 加载SNMP设备状态 - 使用新的buildStatusMap方法
    const loadSNMPDevicesStatus = async () => {
      try {
        const statusMap = await SNMPStorage.buildStatusMap()
        if (statusMap && typeof statusMap === 'object') {
          snmpDevicesStatus.value = statusMap
          const count = Object.keys(statusMap).length
          // SNMP 状态更新后重算统计（去抖）
          scheduleRecompute()
          if (count > 0) {
            console.log(`Home: 加载SNMP设备状态: ${count}个设备`)
          }
        }
      } catch (error) {
        console.error('Home: 加载SNMP设备状态失败:', error)
        // 失败时保持原有数据，不清空
      }
    }

    // 当 SNMP 状态映射变化时，自动重算统计（包括 WebSocket 推送）
    watch(
      () => snmpDevicesStatus.value,
      () => {
        scheduleRecompute()
      },
      { flush: 'post' }
    )

    // WebSocket消息处理器 - 处理单设备实时更新
    const handleDeviceUpdate = async (deviceData) => {
      try {
        const switchId = deviceData.switch_id
        if (!switchId) {
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
        scheduleRecompute()

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
        scheduleRecompute()

        console.debug(
          `Home: 接口状态更新: switch_id=${switchId}, 接口数=${
            interfaceData.interface_info?.length || 0
          }`
        )
      } catch (error) {
        console.error('Home: 处理接口更新失败:', error)
      }
    }

    let deviceUpdateSubToken = null
    let interfaceUpdateSubToken = null

    onMounted(() => {
      fetchData()

      // 异步加载SNMP状态，不阻塞组件渲染
      loadSNMPDevicesStatus().catch((err) => {
        console.error('Home: 初始化SNMP状态失败:', err)
      })

      // 订阅SNMP设备/接口实时更新（保存订阅ID以便精确退订）
      deviceUpdateSubToken = PubSub.subscribe(
        wsCode.SNMP_DEVICE_UPDATE,
        handleDeviceUpdate
      )
      interfaceUpdateSubToken = PubSub.subscribe(
        wsCode.SNMP_INTERFACE_UPDATE,
        handleInterfaceUpdate
      )
      console.log('Home: SNMP实时状态订阅已启动')
    })

    // 组件卸载 - 清理资源
    onUnmounted(() => {
      if (deviceUpdateSubToken) {
        PubSub.unsubscribe(deviceUpdateSubToken)
        deviceUpdateSubToken = null
      }
      if (interfaceUpdateSubToken) {
        PubSub.unsubscribe(interfaceUpdateSubToken)
        interfaceUpdateSubToken = null
      }
      // 清空状态，释放内存
      snmpDevicesStatus.value = {}
      if (_recomputeTimer) {
        clearTimeout(_recomputeTimer)
        _recomputeTimer = null
      }
      console.log('Home: SNMP实时状态订阅已取消')
    })

    return {
      statistics,
      devices,
      switches,
      switchesWithStatus,
      formatOSInfo,
      formatTimestamp,
      deviceCount,
      switchCount,
      totalCount
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
  color: #456a63;
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
  color: #456a63;
  margin: 0;
}

.device-list h2 {
  margin-bottom: 20px;
  color: #333;
}

.device-card h3,
.switch-card h3 {
  margin-top: 0;
  color: #456a63;
}

.device-card p,
.switch-card p {
  margin: 8px 0;
}
</style>
