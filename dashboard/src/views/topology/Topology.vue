<template>
  <div class="p-[12px] size-full topology-area">
    <div class="size-full bg-white rounded-lg shadow p-[6px] relative">
      <!-- 测试数据生成面板 -->
      <div v-show="showTestPanel" class="test-data-panel">
        <a-space direction="vertical" size="small">
          <a-button type="primary" size="small" @click="handleGenerateTestData">
            🎨 生成测试数据
          </a-button>
          <a-button size="small" @click="handleGenerateSimpleData">
            📊 简化版(8交换机+50设备)
          </a-button>
          <a-button size="small" @click="handleGenerateLargeData" danger>
            🚀 大规模(30交换机+1000设备)
          </a-button>
          <a-button size="small" @click="handleExportData">
            💾 导出JSON
          </a-button>
          <a-button size="small" @click="handleClearData" danger>
            🗑️ 清空
          </a-button>
        </a-space>
      </div>

      <!-- D3 拓扑图组件 -->
      <D3Topology
        ref="topologyRef"
        :devices="devices"
        :switches="switches"
        :initial-data="data"
        :show-device-panel="true"
        @save="handleSave"
        @node-click="handleNodeClick"
        @node-delete="handleNodeDelete"
        @data-change="handleDataChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, shallowRef } from 'vue'
import { message, Modal } from 'ant-design-vue'
import D3Topology from '@/components/topology/D3Topology.vue'
import DeviceApi from '@/common/api/device'
import SwitchApi from '@/common/api/switch'
import TopologyApi from '@/common/api/topology'
import {
  generateThreeTierTopology,
  generateSimpleTestData,
  generateLargeScaleTestData,
  exportToJSON
} from '@/utils/topologyTestDataGenerator'

// Refs
const topologyRef = ref(null)
const devices = shallowRef([])
const switches = shallowRef([])
const data = shallowRef({ nodes: [], links: [] })
const currentTopologyId = ref(null)
const isSaving = ref(false)
const showTestPanel = ref(false) // 测试面板显示状态

// 加载最新的拓扑图
const loadLatestTopology = async () => {
  try {
    const response = await TopologyApi.getLatestTopology()
    if (response?.data?.content) {
      currentTopologyId.value = response.data.id
      // 直接使用 D3 数据格式
      data.value = response.data.content
    }
  } catch (error) {
    if (error?.response?.status !== 404) {
      console.error('加载拓扑图失败:', error)
      message.error('加载拓扑图失败')
    }
  }
}

// 保存拓扑图
const handleSave = async (topologyData) => {
  if (isSaving.value) return

  try {
    isSaving.value = true

    // 直接保存 D3 数据格式
    const response = await TopologyApi.createTopology(topologyData)
    if (response?.data?.id) {
      currentTopologyId.value = response.data.id
    }
    message.success('拓扑图保存成功')
  } catch (error) {
    console.error('保存拓扑图失败:', error)
    message.error(error?.response?.data?.message || '保存拓扑图失败')
  } finally {
    isSaving.value = false
  }
}

// 节点点击事件
const handleNodeClick = (node) => {
  console.log('节点点击:', node)
}

// 节点删除事件
const handleNodeDelete = (nodeId) => {
  console.log('节点删除:', nodeId)
}

// 数据变化事件
const handleDataChange = (newData) => {
  data.value = newData
}

// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await DeviceApi.getDevicesList()
    devices.value = response?.data || []
  } catch (error) {
    console.error('获取设备列表失败:', error)
    message.error('获取设备列表失败')
  }
}

// 获取交换机列表
const fetchSwitches = async () => {
  try {
    const response = await SwitchApi.getSwitchesList()
    switches.value = response?.data || []
  } catch (error) {
    console.error('获取交换机列表失败:', error)
    message.error('获取交换机列表失败')
  }
}

// 生成标准测试数据（20个交换机，500个设备）
const handleGenerateTestData = () => {
  Modal.confirm({
    title: '生成测试数据',
    content:
      '将生成三层网络架构：2个核心交换机 + 6个汇聚交换机 + 12个接入交换机 + 500个终端设备',
    okText: '确认生成',
    cancelText: '取消',
    onOk() {
      try {
        const hideLoading = message.loading('正在生成测试数据...', 0)

        const testData = generateThreeTierTopology({
          switchCount: 20,
          deviceCount: 500
        })

        data.value = testData

        setTimeout(() => {
          hideLoading()
          topologyRef.value?.fitView()

          message.success(
            `测试数据生成完成！\n` +
              `节点: ${testData.nodes.length} | ` +
              `连线: ${testData.links.length}`,
            5
          )
        }, 300)
      } catch (error) {
        console.error('生成测试数据失败:', error)
        message.error('生成测试数据失败: ' + error.message)
      }
    }
  })
}

// 生成简化版测试数据
const handleGenerateSimpleData = () => {
  try {
    const hideLoading = message.loading('正在生成简化测试数据...', 0)

    const testData = generateSimpleTestData()
    data.value = testData

    setTimeout(() => {
      hideLoading()
      topologyRef.value?.fitView()
      message.success(
        `简化版数据生成完成！\n` +
          `节点: ${testData.nodes.length} | ` +
          `连线: ${testData.links.length}`,
        3
      )
    }, 200)
  } catch (error) {
    console.error('生成简化数据失败:', error)
    message.error('生成数据失败: ' + error.message)
  }
}

// 生成大规模测试数据
const handleGenerateLargeData = () => {
  Modal.confirm({
    title: '⚠️ 生成大规模测试数据',
    content: '将生成30个交换机和1000个设备，可能会影响性能，确认继续？',
    okText: '确认生成',
    cancelText: '取消',
    okType: 'danger',
    onOk() {
      try {
        const hideLoading = message.loading(
          '正在生成大规模测试数据，请稍候...',
          0
        )

        // 使用 setTimeout 避免阻塞 UI
        setTimeout(() => {
          try {
            const testData = generateLargeScaleTestData()
            data.value = testData

            hideLoading()

            setTimeout(() => {
              topologyRef.value?.fitView()
              message.success(
                `大规模数据生成完成！\n` +
                  `节点: ${testData.nodes.length} | ` +
                  `连线: ${testData.links.length}`,
                5
              )
            }, 500)
          } catch (error) {
            hideLoading()
            console.error('生成大规模数据失败:', error)
            message.error('生成数据失败: ' + error.message)
          }
        }, 100)
      } catch (error) {
        console.error('生成大规模数据失败:', error)
        message.error('生成数据失败: ' + error.message)
      }
    }
  })
}

// 导出数据为JSON
const handleExportData = () => {
  if (!data.value || data.value.nodes.length === 0) {
    message.warning('当前没有数据可导出')
    return
  }

  try {
    const filename = `topology-${new Date().getTime()}.json`
    exportToJSON(data.value, filename)
    message.success('数据导出成功')
  } catch (error) {
    console.error('导出数据失败:', error)
    message.error('导出数据失败')
  }
}

// 清空数据
const handleClearData = () => {
  Modal.confirm({
    title: '清空拓扑图',
    content: '确认要清空当前拓扑图的所有数据吗？',
    okText: '确认清空',
    cancelText: '取消',
    okType: 'danger',
    onOk() {
      data.value = { nodes: [], links: [] }
      message.success('拓扑图已清空')
    }
  })
}

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([loadLatestTopology(), fetchDevices(), fetchSwitches()])

  // 添加快捷键监听
  window.addEventListener('keydown', handleKeyDown)
})

// 组件卸载时移除监听
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// 快捷键处理
const handleKeyDown = (event) => {
  // Ctrl+Shift+K
  if (event.ctrlKey && event.shiftKey && event.key === 'K') {
    event.preventDefault() // 阻止默认行为
    showTestPanel.value = !showTestPanel.value

    if (showTestPanel.value) {
      message.success('测试面板已展开', 1)
    } else {
      message.info('测试面板已隐藏', 1)
    }
  }
}
</script>

<style lang="less" scoped>
.topology-area {
  // 确保容器填充父元素
  :deep(.d3-topology-container) {
    width: 100%;
    height: 100%;
  }
}

// 测试数据面板
.test-data-panel {
  position: absolute;
  bottom: 73px;
  right: 12px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease-in-out;

  :deep(.ant-btn) {
    width: 100%;
    font-size: 12px;
    height: 28px;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
  }
}
</style>
