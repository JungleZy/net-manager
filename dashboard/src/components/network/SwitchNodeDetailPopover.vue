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
    <div class="node-detail-popover">
      <!-- 头部 -->
      <div class="popover-header">
        <div class="header-top">
          <h4
            style="width: calc(100% - 50px)"
            class="popover-title truncate"
            :title="
              (device.device_name || '未命名设备') +
              (device.alias ? ' - ' + device.alias : '')
            "
          >
            {{ device.device_name || '未命名设备' }}
            <span style="font-size: 14px">{{
              device.alias ? ' - ' + device.alias : ''
            }}</span>
          </h4>
          <span
            style="width: 50px"
            :class="[
              'status-badge',
              device.isVirtual
                ? 'virtual'
                : device.status === 'online'
                ? 'online'
                : 'offline'
            ]"
          >
            {{
              device.isVirtual
                ? '虚拟'
                : device.status === 'online'
                ? '在线'
                : '离线'
            }}
          </span>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="popover-body" v-if="!device.isVirtual">
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="section-title">基本信息</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">IP地址</span>
              <span class="value">{{ device.ip || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">设备类型</span>
              <span class="value">{{ device.device_type || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">SNMP版本</span>
              <span class="value">{{ device.snmp_version || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后更新</span>
              <span class="value">{{ formatTime(device.last_updated) }}</span>
            </div>
          </div>
        </div>

        <!-- 设备描述 -->
        <div class="info-section" v-if="device.description">
          <div class="section-title">
            <span>设备描述</span>
          </div>
          <div class="description-text">{{ device.description }}</div>
        </div>

        <!-- 运行状态 -->
        <div class="info-section" v-if="device.status === 'online'">
          <div class="section-title">运行状态</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">运行时间</span>
              <span class="value">{{
                formatUptime(device.device_info.uptime)
              }}</span>
            </div>
            <div class="info-item">
              <span class="label">接口数量</span>
              <span class="value">{{ device.device_info.if_count || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- 错误信息 -->
        <div class="info-section" v-if="device.error">
          <div class="section-title error-title">错误信息</div>
          <div class="error-message">{{ device.error }}</div>
        </div>

        <!-- 接口信息 -->
        <div class="info-section" v-if="interfaceList.length > 0">
          <div
            class="section-title"
            @click="interfaceExpanded = !interfaceExpanded"
          >
            <span>接口信息 ({{ interfaceList.length }})</span>
            <DownOutlined v-if="interfaceExpanded" class="toggle-icon" />
            <UpOutlined v-else class="toggle-icon" />
          </div>
          <div v-show="interfaceExpanded" class="section-content">
            <div class="interface-list">
              <div
                class="interface-item"
                v-for="(iface, idx) in interfaceList"
                :key="idx"
              >
                <div class="interface-header">
                  <span class="interface-name">{{
                    iface.description || `接口${idx + 1}`
                  }}</span>
                  <span class="interface-type">{{
                    iface.type_text || '-'
                  }}</span>
                </div>
                <div class="interface-details">
                  <div class="detail-grid">
                    <div class="detail-cell">
                      <span class="detail-label">MAC地址:</span>
                      <span class="detail-value">{{
                        iface.address || '-'
                      }}</span>
                    </div>
                    <div class="detail-cell">
                      <span class="detail-label">速率:</span>
                      <span class="detail-value">{{
                        iface.speed_text || '-'
                      }}</span>
                    </div>
                    <div class="detail-cell">
                      <span class="detail-label">管理状态:</span>
                      <span
                        :class="[
                          'status-tag',
                          getAdminStatusClass(iface.admin_status_text)
                        ]"
                      >
                        {{ iface.admin_status_text || '-' }}
                      </span>
                    </div>
                    <div class="detail-cell">
                      <span class="detail-label">工作状态:</span>
                      <span
                        :class="[
                          'status-tag',
                          getOperStatusClass(iface.oper_status_text)
                        ]"
                      >
                        {{ iface.oper_status_text || '-' }}
                      </span>
                    </div>
                  </div>
                  <div class="speed-row">
                    <div class="speed-item upload">
                      <span class="speed-icon">⬆</span>
                      <span class="speed-value">{{
                        iface.upload_readable || formatSpeed(iface.upload_bps)
                      }}</span>
                    </div>
                    <div class="speed-item download">
                      <span class="speed-icon">⬇</span>
                      <span class="speed-value">{{
                        iface.download_readable ||
                        formatSpeed(iface.download_bps)
                      }}</span>
                    </div>
                  </div>
                </div>
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
  ref
} from 'vue'
import { DownOutlined, UpOutlined } from '@ant-design/icons-vue'

// 展开/收起状态
const interfaceExpanded = ref(true)

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
    console.log('switchData: ', list.value[index.value])
    return list.value[index.value]
  }
  return {}
})

// 接口列表
const interfaceList = computed(() => {
  if (!device.value.interface_info) return []
  if (Array.isArray(device.value.interface_info)) {
    return device.value.interface_info
  }
  return []
})

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return timestamp
}

// 格式化运行时间（毫秒转为可读格式）
const formatUptime = (milliseconds) => {
  if (!milliseconds) return '-'

  const seconds = Math.floor(milliseconds / 100) // 从timeticks转换
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  const parts = []
  if (days > 0) parts.push(`${days}天`)
  if (hours > 0) parts.push(`${hours}小时`)
  if (minutes > 0) parts.push(`${minutes}分钟`)

  return parts.length > 0 ? parts.join('') : '不到1分钟'
}

const formatSpeed = (bps) => {
  if (bps === null || bps === undefined) return '-'
  const val = Number(bps)
  if (Number.isNaN(val)) return String(bps)
  if (val === 0) return '-'
  if (val >= 1_000_000_000) return `${(val / 1_000_000_000).toFixed(1)} Gbps`
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(0)} Mbps`
  if (val >= 1_000) return `${(val / 1_000).toFixed(0)} Kbps`
  return `${val} bps`
}

// 获取管理状态样式类
const getAdminStatusClass = (status) => {
  if (!status) return ''
  if (status.includes('已启用')) return 'enabled'
  if (status.includes('已禁用')) return 'disabled'
  if (status.includes('测试')) return 'testing'
  return ''
}

// 获取工作状态样式类
const getOperStatusClass = (status) => {
  if (!status) return ''
  if (status.includes('运行中')) return 'running'
  if (status.includes('未运行')) return 'down'
  if (status.includes('测试')) return 'testing'
  return ''
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
      nextTick(() => {
        // 移除旧的监听器
        document.removeEventListener('click', handleClickOutside)
        // 延迟添加新的监听器，防止当前点击立即触发关闭
        setTimeout(() => {
          document.addEventListener('click', handleClickOutside)
        }, 100)
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
@import './stytle.less';

// 接口信息特定样式
.interface-list {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .interface-item {
    padding: 8px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 6px;

    .interface-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      padding-bottom: 4px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.08);

      .interface-name {
        font-size: 13px;
        font-weight: 600;
        color: #262626;
      }

      .interface-type {
        font-size: 12px;
        color: #1890ff;
        font-weight: 500;
        padding: 2px 8px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 4px;
      }
    }

    .interface-details {
      display: flex;
      flex-direction: column;
      gap: 6px;

      .detail-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 12px;
      }

      .detail-cell {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
      }

      .detail-label {
        color: #8c8c8c;
        font-weight: 500;
      }

      .detail-value {
        color: #262626;
        font-weight: 500;
        font-family: monospace;
      }

      .status-tag {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;

        &.enabled,
        &.running {
          background-color: #f6ffed;
          color: #52c41a;
          border: 1px solid #b7eb8f;
        }

        &.disabled,
        &.down {
          background-color: #fff2f0;
          color: #ff4d4f;
          border: 1px solid #ffccc7;
        }

        &.testing {
          background-color: #fff7e6;
          color: #fa8c16;
          border: 1px solid #ffd591;
        }
      }

      .speed-row {
        display: flex;
        gap: 12px;
        align-items: center;
        margin-top: 2px;
      }

      .speed-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 2px 6px;
        border-radius: 4px;
        background: #f0f5ff;
        font-size: 12px;
      }

      .speed-item.upload .speed-icon {
        color: #1890ff;
      }
      .speed-item.download .speed-icon {
        color: #52c41a;
      }

      .speed-value {
        font-family: monospace;
        color: #262626;
        font-weight: 500;
      }
    }
  }
}

// 设备描述样式
.description-text {
  padding: 8px;
  background: #fafafa;
  border-radius: 4px;
  font-size: 12px;
  color: #595959;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

// 错误信息样式
.error-title {
  color: #ff4d4f !important;
  border-bottom-color: #ff4d4f !important;
}

.error-message {
  padding: 8px 12px;
  background: #fff2f0;
  border-left: 3px solid #ff4d4f;
  border-radius: 4px;
  font-size: 12px;
  color: #ff4d4f;
  font-weight: 500;
}
</style>
