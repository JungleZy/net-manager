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
      <div class="popover-header">
        <h4 class="popover-title">
          {{ list[index].name || '未命名设备' }}
        </h4>
      </div>
      <div class="popover-body">
        {{ list[index] }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch, nextTick, onUnmounted, useTemplateRef } from 'vue'

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
  min-width: 280px;
  max-width: 400px;
  max-height: var(--max-height, 600px);
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  overflow-y: auto;

  .popover-header {
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;

    .popover-title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #262626;
    }
  }

  .popover-body {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .detail-item {
      display: flex;
      align-items: center;
      font-size: 14px;

      .detail-label {
        min-width: 80px;
        color: #8c8c8c;
        font-weight: 500;
      }

      .detail-value {
        color: #262626;
        word-break: break-all;
      }

      .status-tag {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;

        &.online {
          background-color: #f6ffed;
          color: #52c41a;
          border: 1px solid #b7eb8f;
        }

        &.offline {
          background-color: #fff2f0;
          color: #ff4d4f;
          border: 1px solid #ffccc7;
        }
      }
    }
  }
}
</style>
