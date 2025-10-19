<template>
  <div
    v-if="visible && index > -1"
    ref="popoverRef"
    class="custom-popover"
    :class="`popover-${placement}`"
    :style="{
      left: position.x + 'px',
      top: position.y + 'px',
      '--max-height': maxHeight + 'px',
      '--arrow-offset': arrowOffset + 'px'
    }"
    @click.stop
  >
    <div class="popover-arrow"></div>
    <div class="node-detail-popover">
      <!-- 头部 -->
      <div class="popover-header">
        <div class="header-top">
          <h4 class="popover-title">
            {{ device.hostname || '未命名设备' }}
            <span style="font-size: 14px">{{
              device.alias ? ' - ' + device.alias : ''
            }}</span>
          </h4>
          <span :class="['status-badge', device.online ? 'online' : 'offline']">
            {{ device.online ? '在线' : '离线' }}
          </span>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="popover-body">
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="section-title">基本信息</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">操作系统</span>
              <span class="value"
                >{{ device.os_name }} {{ device.os_version }}</span
              >
            </div>
            <div class="info-item">
              <span class="label">架构</span>
              <span class="value">{{ device.os_architecture }}</span>
            </div>
            <div class="info-item">
              <span class="label">机器类型</span>
              <span class="value">{{ device.machine_type }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后更新</span>
              <span class="value">{{ formatTime(device.timestamp) }}</span>
            </div>
          </div>
        </div>

        <!-- 性能监控 -->
        <div class="info-section">
          <div
            class="section-title"
            @click="performanceExpanded = !performanceExpanded"
          >
            <span>性能监控</span>
            <DownOutlined v-if="performanceExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>

          <div v-show="performanceExpanded" class="section-content">
            <!-- CPU -->
            <div class="metric-item">
              <div class="metric-row">
                <span class="metric-label">CPU</span>
                <a-progress
                  :percent="device.cpu_info?.usage_percent"
                  :show-info="false"
                  :stroke-color="
                    getProgressColor(device.cpu_info?.usage_percent)
                  "
                  class="metric-progress"
                />
                <span class="metric-value"
                  >{{ device.cpu_info?.usage_percent }}%</span
                >
              </div>
              <div class="metric-detail">
                {{ device.cpu_info?.physical_cores }} 核心 ({{
                  device.cpu_info?.cores
                }}
                逻辑处理器) @ {{ device.cpu_info?.current_frequency }} MHz
              </div>
            </div>

            <!-- 内存 -->
            <div class="metric-item">
              <div class="metric-row">
                <span class="metric-label">内存</span>
                <a-progress
                  :percent="device.memory_info?.percentage"
                  :show-info="false"
                  :stroke-color="
                    getProgressColor(device.memory_info?.percentage)
                  "
                  class="metric-progress"
                />
                <span class="metric-value"
                  >{{ device.memory_info?.percentage }}%</span
                >
              </div>
              <div class="metric-detail">
                {{ formatBytes(device.memory_info?.used) }} /
                {{ formatBytes(device.memory_info?.total) }}
              </div>
            </div>

            <!-- 磁盘 -->
            <div class="metric-item">
              <div class="metric-row">
                <span class="metric-label">磁盘</span>
                <a-progress
                  :percent="device.disk_info?.percentage"
                  :show-info="false"
                  :stroke-color="getProgressColor(device.disk_info?.percentage)"
                  class="metric-progress"
                />
                <span class="metric-value"
                  >{{ device.disk_info?.percentage?.toFixed(1) }}%</span
                >
              </div>
              <div class="metric-detail">
                {{ formatBytes(device.disk_info?.used) }} /
                {{ formatBytes(device.disk_info?.total) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 网络接口 -->
        <div class="info-section">
          <div
            class="section-title"
            @click="networkExpanded = !networkExpanded"
          >
            <span>网络接口 ({{ networkInterfaces.length }})</span>
            <DownOutlined v-if="networkExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>
          <div v-show="networkExpanded" class="section-content">
            <div class="network-list">
              <div
                class="network-item"
                v-for="(network, idx) in networkInterfaces"
                :key="idx"
              >
                <div class="network-header">
                  <span class="network-name">{{ network.name }}</span>
                  <span class="network-ip">{{ network.ip_address }}</span>
                </div>
                <div class="network-speeds">
                  <div class="speed-item upload">
                    <span class="speed-icon">⬆</span>
                    <span class="speed-value">{{
                      formatSpeed(network.upload_rate)
                    }}</span>
                  </div>
                  <div class="speed-item download">
                    <span class="speed-icon">⬇</span>
                    <span class="speed-value">{{
                      formatSpeed(network.download_rate)
                    }}</span>
                  </div>
                  <div
                    class="network-extra"
                    v-if="network.mac_address || network.gateway"
                  >
                    <span v-if="network.mac_address" class="extra-info"
                      >MAC: {{ network.mac_address }}</span
                    >
                    <span v-if="network.gateway" class="extra-info"
                      >网关: {{ network.gateway }}</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 磁盘分区 -->
        <div class="info-section" v-if="device.disk_info?.partitions?.length">
          <div
            class="section-title"
            @click="partitionExpanded = !partitionExpanded"
          >
            <span>磁盘分区 ({{ device.disk_info.partitions.length }})</span>
            <DownOutlined v-if="partitionExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>
          <div v-show="partitionExpanded" class="section-content">
            <div class="partition-list">
              <div
                class="partition-item"
                v-for="(partition, idx) in device.disk_info.partitions"
                :key="idx"
              >
                <div class="partition-header">
                  <span class="partition-name">{{ partition.device }}</span>
                  <a-progress
                    :percent="partition.percentage"
                    :show-info="false"
                    :stroke-color="getProgressColor(partition.percentage)"
                    size="small"
                    class="partition-progress"
                  />
                  <span class="partition-usage"
                    >{{ partition.percentage }}%</span
                  >
                </div>
                <div class="partition-detail">
                  {{ formatBytes(partition.used) }} /
                  {{ formatBytes(partition.total) }} ({{
                    partition.file_system
                  }})
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="info-section">
          <div class="section-title">统计信息</div>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-value">{{ device.services_count }}</div>
              <div class="stat-label">服务数</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ device.processes_count }}</div>
              <div class="stat-label">进程数</div>
            </div>
          </div>
        </div>

        <!-- 服务列表（前5个） -->
        <div class="info-section" v-if="device.services?.length">
          <div class="section-title">
            运行中的服务 (显示前5个，共{{ device.services.length }}个)
          </div>
          <div class="service-list">
            <div
              class="service-item"
              v-for="(service, idx) in device.services.slice(0, 5)"
              :key="idx"
            >
              <div class="service-header">
                <span class="service-protocol">{{ service.protocol }}</span>
                <span class="service-address">{{ service.local_address }}</span>
              </div>
              <div class="service-detail">
                <span class="service-process">{{ service.process_name }}</span>
                <span class="service-pid">PID: {{ service.pid }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  watch,
  nextTick,
  onUnmounted,
  useTemplateRef,
  computed,
  ref,
  shallowRef
} from 'vue'
import { DownOutlined, UpOutlined } from '@ant-design/icons-vue'
import localforage from 'localforage'
import simplebar from 'simplebar-vue'
import 'simplebar-vue/dist/simplebar.min.css'

// 展开/收起状态
const performanceExpanded = ref(true)
const networkExpanded = ref(true)
const partitionExpanded = ref(true)

// 优化：使用常量存储固定值，避免重复创建
const BYTES_UNITS = Object.freeze(['B/s', 'KB/s', 'MB/s', 'GB/s'])
const SIZE_UNITS = Object.freeze(['B', 'KB', 'MB', 'GB', 'TB'])
const BYTES_K = 1024
const LOG_K = Math.log(BYTES_K)

// Props定义
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  placement: {
    type: String,
    default: 'right',
    validator: (value) => ['right', 'left', 'top', 'bottom'].includes(value)
  },
  maxHeight: {
    type: Number,
    default: 600
  },
  arrowOffset: {
    type: Number,
    default: 0
  }
})
const list = defineModel()
const index = defineModel('index')

// Emits定义
const emit = defineEmits(['close'])

// 当前设备数据
const device = computed(() => {
  if (list.value && index.value > -1 && index.value < list.value.length) {
    console.log(list.value[index.value])
    return list.value[index.value]
  }
  return {}
})

// 设备ID（用于存储key）
const deviceId = computed(() => {
  return device.value.client_id || device.value.id || 'unknown'
})

// LocalForage 存储key
const STORAGE_KEY_PREFIX = 'device-popover-state-'

// 优化：存储防抖定时器
let saveStateDebounceTimer = null

// 加载设备的展开/收起状态
const loadDeviceState = async () => {
  if (!deviceId.value || deviceId.value === 'unknown') return

  try {
    const storageKey = STORAGE_KEY_PREFIX + deviceId.value
    const savedState = await localforage.getItem(storageKey)

    if (savedState) {
      performanceExpanded.value = savedState.performance ?? true
      networkExpanded.value = savedState.network ?? true
      partitionExpanded.value = savedState.partition ?? true
    }
  } catch (error) {
    console.warn('加载设备状态失败:', error)
  }
}

// 保存设备的展开/收起状态（优化：添加防抖）
const saveDeviceState = async () => {
  if (!deviceId.value || deviceId.value === 'unknown') return

  try {
    const storageKey = STORAGE_KEY_PREFIX + deviceId.value
    const state = {
      performance: performanceExpanded.value,
      network: networkExpanded.value,
      partition: partitionExpanded.value
    }

    await localforage.setItem(storageKey, state)
  } catch (error) {
    console.warn('保存设备状态失败:', error)
  }
}

// 防抖保存函数
const debouncedSaveDeviceState = () => {
  if (saveStateDebounceTimer) {
    clearTimeout(saveStateDebounceTimer)
  }
  saveStateDebounceTimer = setTimeout(() => {
    saveDeviceState()
  }, 300)
}

// 网络接口数据（按总速率降序排列）
const networkInterfaces = computed(() => {
  if (!device.value.networks) return []

  let interfaces = []

  // 如果是字符串，解析为JSON
  if (typeof device.value.networks === 'string') {
    try {
      interfaces = JSON.parse(device.value.networks)
    } catch (e) {
      console.warn('解析网络接口数据失败:', e)
      return []
    }
  } else if (Array.isArray(device.value.networks)) {
    // 如果已经是数组，直接使用
    interfaces = device.value.networks
  } else {
    return []
  }

  // 优化：按照上传+下载的总速率降序排列，使用一次遍历
  return interfaces.sort((a, b) => {
    const totalA = (a.upload_rate || 0) + (a.download_rate || 0)
    const totalB = (b.upload_rate || 0) + (b.download_rate || 0)
    return totalB - totalA
  })
})

// 格式化网络速率（优化：使用常量数组和数学计算）
const formatSpeed = (bytesPerSecond) => {
  if (!bytesPerSecond || bytesPerSecond === 0) return '0 B/s'

  const i = Math.floor(Math.log(bytesPerSecond) / LOG_K)
  return (
    (bytesPerSecond / Math.pow(BYTES_K, i)).toFixed(2) + ' ' + BYTES_UNITS[i]
  )
}

// 格式化字节大小（优化：使用常量数组和数学计算）
const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / LOG_K)
  return (bytes / Math.pow(BYTES_K, i)).toFixed(2) + ' ' + SIZE_UNITS[i]
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return timestamp
}

// 根据使用率获取进度条颜色（优化：直接返回，减少条件判断）
const getProgressColor = (percent) => {
  return percent < 60 ? '#52c41a' : percent < 80 ? '#faad14' : '#ff4d4f'
}

// Refs
const popoverRef = useTemplateRef('popoverRef')

// 优化：使用事件委托和防抖处理点击事件
let clickDebounceTimer = null

// 处理全局点击事件，点击外部关闭 Popover
const handleClickOutside = (event) => {
  // 如果 Popover 未显示，直接返回
  if (!props.visible) return

  // 检查点击是否在 Popover 内部
  const popoverElement = popoverRef.value
  if (popoverElement && popoverElement.contains(event.target)) {
    return
  }

  // 点击在 Popover 外部，关闭 Popover
  emit('close')
}

// 监听visible变化，动态添加/移除全局点击监听（优化：添加防抖）
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      // 加载设备状态
      loadDeviceState()

      // 使用 nextTick 确保 Popover 渲染完成后再添加全局监听
      nextTick(() => {
        // 移除旧的监听器
        document.removeEventListener('click', handleClickOutside)
        // 延迟添加新的监听器，防止当前点击立即触发关闭
        if (clickDebounceTimer) clearTimeout(clickDebounceTimer)
        clickDebounceTimer = setTimeout(() => {
          document.addEventListener('click', handleClickOutside)
        }, 100)
      })
    } else {
      // Popover关闭时移除监听器
      document.removeEventListener('click', handleClickOutside)
      if (clickDebounceTimer) {
        clearTimeout(clickDebounceTimer)
        clickDebounceTimer = null
      }
    }
  }
)

// 监听展开/收起状态变化，保存到 LocalForage（优化：使用防抖）
watch([performanceExpanded, networkExpanded, partitionExpanded], () => {
  if (props.visible) {
    debouncedSaveDeviceState()
  }
})

// 组件卸载时清理（优化：清理定时器）
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)

  // 清理防抖定时器
  if (saveStateDebounceTimer) {
    clearTimeout(saveStateDebounceTimer)
    saveStateDebounceTimer = null
  }
})
</script>

<style lang="less" scoped>
// 自定义 Popover 样式
.custom-popover {
  position: absolute;
  z-index: 10000; // 确保在页内全屏时也能显示

  .popover-arrow {
    position: absolute;
    width: 0;
    height: 0;
  }
}

// 右侧弹出（默认）
.popover-right {
  transform: translate(20px, -50%);
  animation: popoverFadeInRight 0.2s ease-out;

  .popover-arrow {
    left: -8px;
    top: 50%;
    transform: translateY(-50%);
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
    border-right: 8px solid #fff;
    filter: drop-shadow(-2px 0 4px rgba(0, 0, 0, 0.08));
  }
}

// 左侧弹出
.popover-left {
  transform: translate(calc(-100% - 20px), -50%);
  animation: popoverFadeInLeft 0.2s ease-out;

  .popover-arrow {
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
    border-left: 8px solid #fff;
    filter: drop-shadow(2px 0 4px rgba(0, 0, 0, 0.08));
  }
}

@keyframes popoverFadeInRight {
  from {
    opacity: 0;
    transform: translate(10px, -50%);
  }
  to {
    opacity: 1;
    transform: translate(20px, -50%);
  }
}

@keyframes popoverFadeInLeft {
  from {
    opacity: 0;
    transform: translate(calc(-100% - 10px), -50%);
  }
  to {
    opacity: 1;
    transform: translate(calc(-100% - 20px), -50%);
  }
}

// 下方弹出
.popover-bottom {
  transform: translate(-50%, 70px);
  animation: popoverFadeInBottom 0.2s ease-out;

  .popover-arrow {
    position: absolute;
    left: 50%;
    top: var(--arrow-offset, 0px);
    transform: translate(-50%, -8px);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 8px solid #fff;
    filter: drop-shadow(0 -2px 4px rgba(0, 0, 0, 0.08));
  }
}

@keyframes popoverFadeInBottom {
  from {
    opacity: 0;
    transform: translate(-50%, 60px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 70px);
  }
}

// 上方弹出
.popover-top {
  transform: translate(-50%, calc(-100% - 70px));
  animation: popoverFadeInTop 0.2s ease-out;

  .popover-arrow {
    position: absolute;
    left: 50%;
    bottom: calc(var(--arrow-offset, 0px) * -1);
    transform: translate(-50%, 8px);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid #fff;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.08));
  }
}

@keyframes popoverFadeInTop {
  from {
    opacity: 0;
    transform: translate(-50%, calc(-100% - 60px));
  }
  to {
    opacity: 1;
    transform: translate(-50%, calc(-100% - 70px));
  }
}

// 节点详情 Popover 样式
.node-detail-popover {
  width: 450px;
  max-height: var(--max-height, 600px);
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .popover-header {
    padding: 6px 12px;
    background: linear-gradient(135deg, #667eea 0%, #1677ff 100%);
    color: white;
    flex-shrink: 0;

    .header-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 4px;

      .popover-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: white;
      }

      .status-badge {
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;

        &.online {
          background-color: rgba(0, 255, 0, 0.8);
          color: #ffffff;
          border: 1px solid rgb(0, 255, 0);
        }

        &.offline {
          background-color: rgba(255, 0, 0, 0.8);
          color: #ffffff;
          border: 1px solid rgb(255, 0, 0);
        }
      }
    }

    .header-subtitle {
      font-size: 13px;
      opacity: 0.9;
      color: rgba(255, 255, 255, 0.85);
    }
  }

  .popover-body {
    padding: 6px 12px;
    overflow-y: auto;
    overflow-x: hidden;
    flex: 1;
    .ant-progress-line {
      margin: 0;
    }

    .info-section {
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #262626;
        margin-bottom: 6px;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        user-select: none;
        transition: all 0.2s ease;

        &:hover {
          color: #1890ff;
          border-bottom-color: #1890ff;
        }

        .toggle-icon {
          font-size: 12px;
          color: #8c8c8c;
          transition: transform 0.2s ease, color 0.2s ease;
        }

        &:hover .toggle-icon {
          color: #1890ff;
        }
      }

      .section-content {
        animation: slideDown 0.2s ease-out;
      }

      .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;

          .label {
            font-size: 12px;
            color: #8c8c8c;
            font-weight: 500;
          }

          .value {
            font-size: 13px;
            color: #262626;
            word-break: break-word;
          }
        }
      }

      .metric-item {
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }

        .metric-row {
          display: flex;
          align-items: center;
          gap: 12px;

          .metric-label {
            font-size: 13px;
            color: #595959;
            font-weight: 500;
            min-width: 30px;
            max-width: 80px;
            flex-shrink: 0;
          }

          .metric-progress {
            flex: 1;
          }

          .metric-value {
            font-size: 14px;
            color: #262626;
            font-weight: 600;
            min-width: 50px;
            text-align: right;
            flex-shrink: 0;
          }
        }

        .metric-header {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .metric-label {
            font-size: 13px;
            color: #595959;
            font-weight: 500;
          }

          .metric-value {
            font-size: 14px;
            color: #262626;
            font-weight: 600;
          }
        }

        .metric-detail {
          font-size: 12px;
          color: #8c8c8c;
          margin-top: 4px;
        }
      }

      .network-list {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .network-item {
          padding: 6px 8px;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          border-radius: 6px;

          .network-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;

            .network-name {
              font-size: 13px;
              font-weight: 600;
              color: #262626;
            }

            .network-ip {
              font-size: 12px;
              color: #1890ff;
              font-weight: 500;
            }
          }

          .network-speeds {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;

            .speed-item {
              display: flex;
              align-items: center;
              gap: 6px;
              padding: 4px 8px;
              background: rgba(255, 255, 255, 0.8);
              border-radius: 4px;
              font-size: 12px;

              &.upload {
                border-left: 2px solid #52c41a;
              }

              &.download {
                border-left: 2px solid #1890ff;
              }

              .speed-icon {
                font-size: 12px;
              }

              .speed-value {
                font-size: 12px;
                font-weight: 600;
                color: #262626;
                margin-left: auto;
              }
            }

            .network-extra {
              grid-column: 1 / -1;
              display: flex;
              gap: 12px;
              font-size: 11px;
              color: #8c8c8c;
              padding: 2px 8px;

              .extra-info {
                font-family: monospace;
              }
            }
          }
        }
      }

      .partition-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .partition-item {
          padding: 10px;
          background: #fafafa;
          border-radius: 6px;

          .partition-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 6px;

            .partition-name {
              font-size: 13px;
              font-weight: 600;
              color: #262626;
              min-width: 30px;
              max-width: 80px;
              flex-shrink: 0;
            }

            .partition-progress {
              flex: 1;
            }

            .partition-usage {
              font-size: 13px;
              font-weight: 600;
              color: #595959;
              min-width: 50px;
              text-align: right;
              flex-shrink: 0;
            }
          }

          .partition-detail {
            font-size: 12px;
            color: #8c8c8c;
            margin-top: 4px;
          }
        }
      }

      .stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;

        .stat-card {
          text-align: center;
          padding: 6px;
          background: linear-gradient(135deg, #667eea 0%, #1677ff 100%);
          border-radius: 8px;
          color: white;

          .stat-value {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 4px;
          }

          .stat-label {
            font-size: 12px;
            opacity: 0.9;
          }
        }
      }

      .service-list {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .service-item {
          padding: 10px;
          background: #fafafa;
          border-radius: 6px;
          border-left: 3px solid #1890ff;

          .service-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;

            .service-protocol {
              padding: 2px 6px;
              background: #e6f7ff;
              color: #1890ff;
              border-radius: 4px;
              font-size: 11px;
              font-weight: 600;
            }

            .service-address {
              font-size: 12px;
              font-weight: 500;
              color: #262626;
            }
          }

          .service-detail {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 11px;
            color: #8c8c8c;

            .service-process {
              font-weight: 500;
            }

            .service-pid {
              color: #1890ff;
            }
          }
        }
      }
    }
  }
}

// 展开/收起动画
@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    overflow: hidden;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}
</style>
