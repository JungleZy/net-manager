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
          <div class="section-title">性能监控</div>

          <!-- CPU -->
          <div class="metric-item">
            <div class="metric-header">
              <span class="metric-label">CPU 使用率</span>
              <span class="metric-value"
                >{{ device.cpu_info?.usage_percent }}%</span
              >
            </div>
            <a-progress
              :percent="device.cpu_info?.usage_percent"
              :show-info="false"
              :stroke-color="getProgressColor(device.cpu_info?.usage_percent)"
            />
            <div class="metric-detail">
              {{ device.cpu_info?.physical_cores }} 核心 ({{
                device.cpu_info?.cores
              }}
              逻辑处理器) @ {{ device.cpu_info?.current_frequency }} MHz
            </div>
          </div>

          <!-- 内存 -->
          <div class="metric-item">
            <div class="metric-header">
              <span class="metric-label">内存使用率</span>
              <span class="metric-value"
                >{{ device.memory_info?.percentage }}%</span
              >
            </div>
            <a-progress
              :percent="device.memory_info?.percentage"
              :show-info="false"
              :stroke-color="getProgressColor(device.memory_info?.percentage)"
            />
            <div class="metric-detail">
              {{ formatBytes(device.memory_info?.used) }} /
              {{ formatBytes(device.memory_info?.total) }}
            </div>
          </div>

          <!-- 磁盘 -->
          <div class="metric-item">
            <div class="metric-header">
              <span class="metric-label">磁盘使用率</span>
              <span class="metric-value"
                >{{ device.disk_info?.percentage?.toFixed(1) }}%</span
              >
            </div>
            <a-progress
              :percent="device.disk_info?.percentage"
              :show-info="false"
              :stroke-color="getProgressColor(device.disk_info?.percentage)"
            />
            <div class="metric-detail">
              {{ formatBytes(device.disk_info?.used) }} /
              {{ formatBytes(device.disk_info?.total) }}
            </div>
          </div>
        </div>

        <!-- 网络接口 -->
        <div class="info-section">
          <div class="section-title">
            网络接口 ({{ networkInterfaces.length }})
          </div>
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
                  <span class="speed-label">上传:</span>
                  <span class="speed-value">{{
                    formatSpeed(network.upload_rate)
                  }}</span>
                </div>
                <div class="speed-item download">
                  <span class="speed-icon">⬇</span>
                  <span class="speed-label">下载:</span>
                  <span class="speed-value">{{
                    formatSpeed(network.download_rate)
                  }}</span>
                </div>
              </div>
              <div
                class="network-detail layout-left-center"
                v-if="network.mac_address"
              >
                <span class="detail-label">MAC:{{ network.mac_address }}</span>
              </div>
              <div class="network-detail" v-if="network.gateway">
                <span class="detail-label">网关:</span>
                <span class="detail-value">{{ network.gateway }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 磁盘分区 -->
        <div class="info-section" v-if="device.disk_info?.partitions?.length">
          <div class="section-title">
            磁盘分区 ({{ device.disk_info.partitions.length }})
          </div>
          <div class="partition-list">
            <div
              class="partition-item"
              v-for="(partition, idx) in device.disk_info.partitions"
              :key="idx"
            >
              <div class="partition-header">
                <span class="partition-name">{{ partition.device }}</span>
                <span class="partition-usage">{{ partition.percentage }}%</span>
              </div>
              <a-progress
                :percent="partition.percentage"
                :show-info="false"
                :stroke-color="getProgressColor(partition.percentage)"
                size="small"
              />
              <div class="partition-detail">
                {{ formatBytes(partition.used) }} /
                {{ formatBytes(partition.total) }} ({{ partition.file_system }})
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
import { watch, nextTick, onUnmounted, useTemplateRef, computed } from 'vue'
import simplebar from 'simplebar-vue'
import 'simplebar-vue/dist/simplebar.min.css'
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
    return list.value[index.value]
  }
  return {}
})

// 网络接口数据
const networkInterfaces = computed(() => {
  if (!device.value.networks) return []

  // 如果是字符串，解析为JSON
  if (typeof device.value.networks === 'string') {
    try {
      return JSON.parse(device.value.networks)
    } catch (e) {
      console.warn('解析网络接口数据失败:', e)
      return []
    }
  }

  // 如果已经是数组，直接返回
  if (Array.isArray(device.value.networks)) {
    return device.value.networks
  }

  return []
})

// 格式化网络速率
const formatSpeed = (bytesPerSecond) => {
  if (!bytesPerSecond || bytesPerSecond === 0) return '0 B/s'

  const k = 1024
  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
  const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k))

  return (bytesPerSecond / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 格式化字节大小
const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return timestamp
}

// 根据使用率获取进度条颜色
const getProgressColor = (percent) => {
  if (percent < 60) return '#52c41a'
  if (percent < 80) return '#faad14'
  return '#ff4d4f'
}

// Refs
const popoverRef = useTemplateRef('popoverRef')

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

// 监听visible变化，动态添加/移除全局点击监听
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      // 使用 nextTick 确保 Popover 渲染完成后再添加全局监听
      // 避免当前点击事件立即触发关闭
      nextTick(() => {
        // 移除旧的监听器
        document.removeEventListener('click', handleClickOutside)
        // 延迟添加新的监听器
        setTimeout(() => {
          document.addEventListener('click', handleClickOutside)
        }, 0)
      })
    } else {
      // Popover关闭时移除监听器
      document.removeEventListener('click', handleClickOutside)
    }
  }
)

// 组件卸载时清理
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="less" scoped>
// 自定义 Popover 样式
.custom-popover {
  position: absolute;
  z-index: 1000;

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
          background-color: rgba(82, 196, 26, 0.2);
          color: #52c41a;
          border: 1px solid rgba(82, 196, 26, 0.4);
        }

        &.offline {
          background-color: rgba(255, 77, 79, 0.2);
          color: #ff4d4f;
          border: 1px solid rgba(255, 77, 79, 0.4);
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
        gap: 12px;

        .network-item {
          padding: 12px;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          border-radius: 8px;
          border-left: 4px solid #1890ff;

          .network-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;

            .network-name {
              font-size: 14px;
              font-weight: 600;
              color: #262626;
            }

            .network-ip {
              font-size: 13px;
              color: #1890ff;
              font-weight: 500;
            }
          }

          .network-speeds {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 8px;

            .speed-item {
              display: flex;
              align-items: center;
              gap: 4px;
              padding: 6px 10px;
              background: rgba(255, 255, 255, 0.8);
              border-radius: 6px;

              &.upload {
                border-left: 3px solid #52c41a;
              }

              &.download {
                border-left: 3px solid #1890ff;
              }

              .speed-icon {
                font-size: 14px;
              }

              .speed-label {
                font-size: 12px;
                color: #8c8c8c;
                font-weight: 500;
              }

              .speed-value {
                font-size: 13px;
                font-weight: 600;
                color: #262626;
                margin-left: auto;
              }
            }
          }

          .network-detail {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 4px;
            font-size: 12px;

            .detail-label {
              color: #8c8c8c;
              font-weight: 500;
            }

            .detail-value {
              color: #595959;
              font-family: monospace;
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
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;

            .partition-name {
              font-size: 13px;
              font-weight: 600;
              color: #262626;
            }

            .partition-usage {
              font-size: 13px;
              font-weight: 600;
              color: #595959;
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
          padding: 12px;
          background: linear-gradient(135deg, #667eea 0%, #1677ff 100%);
          border-radius: 8px;
          color: white;

          .stat-value {
            font-size: 24px;
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
</style>
