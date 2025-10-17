<template>
  <div class="server-performance-test">
    <!-- 骨架屏加载状态 -->
    <div v-if="isLoading">
      <!-- 概览卡片骨架屏 -->
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-[12px]"
      >
        <div
          v-for="i in 4"
          :key="i"
          class="bg-white p-[12px] rounded-lg shadow"
        >
          <a-skeleton active :paragraph="{ rows: 2 }" />
        </div>
      </div>

      <!-- 仪表盘骨架屏 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-[12px] mb-[12px]">
        <div
          v-for="i in 2"
          :key="i"
          class="bg-white p-[12px] rounded-lg shadow"
        >
          <a-skeleton
            active
            :title="{ width: '50%' }"
            :paragraph="{ rows: 1 }"
          />
          <div class="mt-4">
            <a-skeleton-button
              active
              :style="{ width: '100%', height: '240px' }"
            />
          </div>
        </div>
      </div>

      <!-- CPU核心使用率骨架屏 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <a-skeleton active :title="{ width: '30%' }" :paragraph="{ rows: 1 }" />
        <div class="mt-4">
          <a-skeleton-button
            active
            :style="{ width: '100%', height: '300px' }"
          />
        </div>
      </div>

      <!-- 表格骨架屏 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <a-skeleton active :title="{ width: '30%' }" :paragraph="{ rows: 6 }" />
      </div>

      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <a-skeleton active :title="{ width: '30%' }" :paragraph="{ rows: 6 }" />
      </div>

      <!-- 趋势图骨架屏 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-[12px] mb-[12px]">
        <div
          v-for="i in 2"
          :key="i"
          class="bg-white p-[12px] rounded-lg shadow"
        >
          <a-skeleton
            active
            :title="{ width: '40%' }"
            :paragraph="{ rows: 1 }"
          />
          <div class="mt-4">
            <a-skeleton-button
              active
              :style="{ width: '100%', height: '300px' }"
            />
          </div>
        </div>
      </div>

      <!-- 网络速率趋势图骨架屏 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <a-skeleton active :title="{ width: '30%' }" :paragraph="{ rows: 1 }" />
        <div class="mt-4">
          <a-skeleton-button
            active
            :style="{ width: '100%', height: '300px' }"
          />
        </div>
      </div>
    </div>

    <!-- 实际数据 -->
    <div v-else-if="performanceData">
      <!-- 概览卡片 -->
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-[12px]"
      >
        <!-- CPU概览 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">CPU使用率</div>
              <div
                class="text-2xl font-bold"
                :class="getCpuColor(performanceData.cpu.usage_percent)"
              >
                {{ performanceData.cpu.usage_percent }}%
              </div>
              <div class="text-xs text-gray-500 mt-1">
                <template
                  v-if="performanceData.cpu.estimated_physical_cpus > 1"
                >
                  {{ performanceData.cpu.estimated_physical_cpus }}路CPU |
                  {{ performanceData.cpu.physical_cores }}核{{
                    performanceData.cpu.cores
                  }}线程
                </template>
                <template v-else>
                  {{ performanceData.cpu.physical_cores }}核{{
                    performanceData.cpu.cores
                  }}线程
                </template>
              </div>
            </div>
            <div class="text-3xl">💻</div>
          </div>
        </div>

        <!-- 内存概览 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">内存使用率</div>
              <div
                class="text-2xl font-bold"
                :class="getMemoryColor(performanceData.memory.usage_percent)"
              >
                {{ performanceData.memory.usage_percent }}%
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ formatBytes(performanceData.memory.used) }} /
                {{ formatBytes(performanceData.memory.total) }}
              </div>
            </div>
            <div class="text-3xl">🧠</div>
          </div>
        </div>

        <!-- 磁盘概览 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">磁盘使用率</div>
              <div
                class="text-2xl font-bold"
                :class="getDiskColor(performanceData.disk.usage_percent)"
              >
                {{ performanceData.disk.usage_percent }}%
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ formatBytes(performanceData.disk.used) }} /
                {{ formatBytes(performanceData.disk.total) }}
              </div>
            </div>
            <div class="text-3xl">💾</div>
          </div>
        </div>

        <!-- 网络概览 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">网络活跃接口</div>
              <div class="text-2xl font-bold text-blue-600">
                {{ activeNetworkCount }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                总计 {{ performanceData.network.length }} 个接口
              </div>
            </div>
            <div class="text-3xl">🌐</div>
          </div>
        </div>
      </div>

      <!-- 仪表盘和图表 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-[12px] mb-[12px]">
        <!-- CPU使用率仪表盘 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <div class="w-full layout-left-center">
            <h2 class="text-lg font-semibold mb-0" style="margin: 0">
              CPU使用率
            </h2>
            <span class="mx-[6px]">-</span>
            <div class="text-sm text-gray-600 layout-left-center">
              <div>
                当前频率:
                {{ performanceData.cpu.current_frequency || 'N/A' }} MHz
              </div>
              <a-divider type="vertical" />
              <div>
                最大频率: {{ performanceData.cpu.max_frequency || 'N/A' }} MHz
              </div>
              <template v-if="performanceData.cpu.estimated_physical_cpus > 1">
                <a-divider type="vertical" />
                <div>
                  物理CPU: {{ performanceData.cpu.estimated_physical_cpus }}路
                </div>
              </template>
            </div>
          </div>

          <v-chart
            class="chart"
            :option="cpuGaugeOption"
            autoresize
            style="height: 260px"
          />
        </div>

        <!-- 内存使用率仪表盘 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <div class="w-full layout-left-center">
            <h2 class="text-lg font-semibold mb-0" style="margin: 0">
              内存使用率
            </h2>
            <span class="mx-[6px]">-</span>
            <div class="text-sm text-gray-600 layout-left-center">
              <div>
                可用: {{ formatBytes(performanceData.memory.available) }}
              </div>
              <a-divider type="vertical" />
              <div>
                Swap使用: {{ performanceData.memory.swap_percent }}% ({{
                  formatBytes(performanceData.memory.swap_used)
                }}
                / {{ formatBytes(performanceData.memory.swap_total) }})
              </div>
            </div>
          </div>

          <v-chart
            class="chart"
            :option="memoryGaugeOption"
            autoresize
            style="height: 260px"
          />
        </div>
      </div>

      <!-- CPU核心使用率 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <div class="w-full layout-left-center mb-3">
          <h2 class="text-lg font-semibold mb-0" style="margin: 0">
            CPU核心使用率
          </h2>
          <template v-if="performanceData.cpu.estimated_physical_cpus > 1">
            <span class="mx-[6px]">-</span>
            <div class="text-sm text-gray-600">
              {{ performanceData.cpu.estimated_physical_cpus }}路CPU， 共{{
                performanceData.cpu.physical_cores
              }}个物理核心， {{ performanceData.cpu.cores }}个逻辑线程
            </div>
          </template>
        </div>
        <v-chart
          class="chart"
          :option="perCpuOption"
          autoresize
          style="height: 300px"
        />
      </div>

      <!-- 磁盘分区详情 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <div class="w-full layout-left-center">
          <h2 class="text-lg font-semibold mb-[12px]">磁盘分区详情</h2>
          <span class="mx-[6px]">-</span>
          <div class="text-sm text-gray-600 layout-left-center">
            <div>
              磁盘IO - 读取:
              {{ formatBytes(performanceData.disk.io.read_bytes) }} ({{
                performanceData.disk.io.read_count
              }}
              次)
            </div>
            <a-divider type="vertical" />
            <div>
              磁盘IO - 写入:
              {{ formatBytes(performanceData.disk.io.write_bytes) }} ({{
                performanceData.disk.io.write_count
              }}
              次)
            </div>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  挂载点
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  文件系统
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  总容量
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  已用
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  可用
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  使用率
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="(partition, index) in performanceData.disk.partitions"
                :key="index"
              >
                <td
                  class="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  {{ partition.mountpoint }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                  {{ partition.fstype }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                  {{ formatBytes(partition.total) }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                  {{ formatBytes(partition.used) }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                  {{ formatBytes(partition.free) }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm">
                  <span
                    class="px-2 py-1 rounded"
                    :class="getDiskColorBg(partition.usage_percent)"
                  >
                    {{ partition.usage_percent }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 网络接口详情 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <h2 class="text-lg font-semibold mb-3">网络接口详情</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  接口名称
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  IP地址
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  MAC地址
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  上传速率
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  下载速率
                </th>
                <th
                  class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                >
                  发送/接收
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="(iface, index) in performanceData.network"
                :key="index"
                :class="
                  iface.upload_rate > 0 || iface.download_rate > 0
                    ? 'bg-blue-50'
                    : ''
                "
              >
                <td
                  class="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900"
                >
                  {{ iface.name }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                  {{ iface.ip_address }}
                </td>
                <td
                  class="px-4 py-2 whitespace-nowrap text-sm text-gray-500 font-mono"
                >
                  {{ iface.mac_address }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-green-600">
                  {{ formatSpeed(iface.upload_rate) }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-blue-600">
                  {{ formatSpeed(iface.download_rate) }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                  {{ formatBytes(iface.bytes_sent) }} /
                  {{ formatBytes(iface.bytes_recv) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-[12px] mb-[12px]">
        <!-- CPU趋势图 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <h2 class="text-lg font-semibold" style="margin: 0">CPU使用率趋势</h2>
          <v-chart
            class="chart"
            :option="cpuTrendOption"
            autoresize
            style="height: 300px"
          />
        </div>

        <!-- 内存趋势图 -->
        <div class="bg-white p-[12px] rounded-lg shadow">
          <h2 class="text-lg font-semibold" style="margin: 0">
            内存使用率趋势
          </h2>
          <v-chart
            class="chart"
            :option="memoryTrendOption"
            autoresize
            style="height: 300px"
          />
        </div>
      </div>

      <!-- 网络速率趋势图 -->
      <div class="bg-white p-[12px] rounded-lg shadow mb-[12px]">
        <h2 class="text-lg font-semibold mb-3">网络速率趋势</h2>
        <v-chart
          class="chart"
          :option="networkLineOption"
          autoresize
          style="height: 300px"
        />
      </div>
    </div>

    <!-- 无数据提示（加载完成但无数据） -->
    <div v-else class="text-center text-gray-500 py-8">
      <div class="text-4xl mb-4">🔌</div>
      <div>服务器连接断开，等待性能数据...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onUnmounted, computed } from 'vue'
import { PubSub } from '@/common/utils/PubSub'
import PerformanceApi from '@/common/api/performance'
import localforage from 'localforage'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { GaugeChart, LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册ECharts组件
use([
  GaugeChart,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer
])

// ==================== 响应式数据 ====================
const isLoading = ref(true) // 加载状态
const isConnected = ref(false)
const performanceData = shallowRef(null) // 使用 shallowRef 减少响应式开销
const lastUpdateTime = ref('')

// 历史数据存储

// ==================== 常量配置 ====================
const MAX_DATA_POINTS = 20 // 最大数据点数
const DATA_INTERVAL = 10000 // 数据采集间隔（10秒）
const STORAGE_KEY = 'performanceHistory' // LocalForage 存储键
const DEBOUNCE_DELAY = 1000 // 保存防抖延迟

// 颜色阈值配置
const THRESHOLDS = Object.freeze({
  cpu: { warning: 60, danger: 80 },
  memory: { warning: 70, danger: 90 },
  disk: { warning: 80, danger: 90 }
})

// ECharts 颜色配置
const CHART_COLORS = Object.freeze({
  green: '#67C23A',
  orange: '#E6A23C',
  red: '#F56C6C',
  blue: '#409EFF',
  greenAlpha: 'rgba(103, 194, 58, 0.2)',
  blueAlpha: 'rgba(64, 158, 255, 0.2)'
})

// ==================== 注册ECharts组件 ====================
const cpuHistory = ref([])
const memoryHistory = ref([])
const networkUploadHistory = ref([])
const networkDownloadHistory = ref([])
const timeHistory = ref([])

// ==================== 工具函数 ====================

/**
 * B/s 转换为 Mbps
 * @param {number} bytes - 字节/秒
 * @returns {number} Mbps值
 */
const bytesToMbps = (bytes) => Number(((bytes * 8) / 1024 / 1024).toFixed(2))

/**
 * 格式化字节数
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的字符串
 */
const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`
}

/**
 * 格式化速率
 * @param {number} bytesPerSecond - 字节/秒
 * @returns {string} 格式化后的速率字符串
 */
const formatSpeed = (bytesPerSecond) => {
  if (bytesPerSecond === 0) return '0 B/s'
  const mbps = bytesToMbps(bytesPerSecond)
  return mbps >= 1
    ? `${mbps.toFixed(2)} Mbps`
    : `${((bytesPerSecond * 8) / 1024).toFixed(2)} Kbps`
}

/**
 * 格式化时间字符串
 * @param {Date} date - 日期对象
 * @returns {string} HH:MM:SS格式的时间字符串
 */
const formatTime = (date) => {
  return `${date.getHours().toString().padStart(2, '0')}:${date
    .getMinutes()
    .toString()
    .padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

/**
 * 根据使用率获取颜色类名
 * @param {number} percent - 使用率百分比
 * @param {string} type - 类型: 'cpu', 'memory', 'disk'
 * @returns {string} Tailwind颜色类名
 */
const getUsageColor = (percent, type = 'cpu') => {
  const thresholds = THRESHOLDS[type] || THRESHOLDS.cpu
  if (percent >= thresholds.danger) return 'text-red-600'
  if (percent >= thresholds.warning) return 'text-orange-600'
  return 'text-green-600'
}

/**
 * 根据磁盘使用率返回背景颜色类名
 * @param {number} percent - 使用率百分比
 * @returns {string} Tailwind背景颜色类名
 */
const getDiskColorBg = (percent) => {
  if (percent >= THRESHOLDS.disk.danger) return 'bg-red-100 text-red-800'
  if (percent >= THRESHOLDS.disk.warning) return 'bg-orange-100 text-orange-800'
  return 'bg-green-100 text-green-800'
}

// 兼容旧函数名
const getCpuColor = (percent) => getUsageColor(percent, 'cpu')
const getMemoryColor = (percent) => getUsageColor(percent, 'memory')
const getDiskColor = (percent) => getUsageColor(percent, 'disk')

// 计算活跃网络接口数量
const activeNetworkCount = computed(() => {
  if (!performanceData.value?.network) return 0
  return performanceData.value.network.filter(
    (iface) => iface.upload_rate > 0 || iface.download_rate > 0
  ).length
})

// ==================== 图表配置 ====================

/**
 * 创建仪表盘配置
 * @param {number} value - 当前值
 * @param {string} name - 名称
 * @returns {Object} ECharts仪表盘配置
 */
const createGaugeConfig = (value, name) => ({
  series: [
    {
      type: 'gauge',
      center: ['50%', '70%'], // 上移中心位置，增大上方图像区域
      radius: '140%', // 增大半径至95%
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 10,
      axisLine: {
        lineStyle: {
          width: 6,
          color: [
            [0.3, CHART_COLORS.green],
            [0.7, CHART_COLORS.orange],
            [1, CHART_COLORS.red]
          ]
        }
      },
      pointer: { itemStyle: { color: 'inherit' } },
      axisTick: {
        distance: -30,
        length: 8,
        lineStyle: { color: '#fff', width: 2 }
      },
      splitLine: {
        distance: -30,
        length: 30,
        lineStyle: { color: '#fff', width: 4 }
      },
      axisLabel: {
        color: 'inherit',
        distance: 30,
        fontSize: 16 // 减小刻度文字大小
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}%',
        color: 'inherit',
        fontSize: 18, // 减小数值文字大小（从24改为20）
        offsetCenter: [0, '40%'] // 下移文字位置，给上方图像更多空间
      },
      data: [{ value, name }]
    }
  ]
})

/**
 * 创建趋势图配置
 * @param {string} name - 图表名称
 * @param {Array} data - 数据数组
 * @param {string} color - 线条颜色
 * @param {string} alphaColor - 区域填充颜色
 * @returns {Object} ECharts折线图配置
 */
const createTrendConfig = (name, data, color, alphaColor) => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  grid: {
    left: 0,
    right: 0,
    bottom: 0,
    top: 24,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: timeHistory.value
  },
  yAxis: {
    type: 'value',
    name: name.includes('速率') ? 'Mbps' : '使用率(%)',
    min: 0,
    max: name.includes('速率') ? undefined : 100,
    axisLabel: {
      formatter: name.includes('速率') ? '{value}' : '{value}%'
    }
  },
  series: [
    {
      name,
      type: 'line',
      smooth: true,
      data,
      areaStyle: { color: alphaColor },
      itemStyle: { color },
      lineStyle: { width: 2 }
    }
  ]
})

// CPU仪表盘配置
const cpuGaugeOption = computed(() =>
  createGaugeConfig(performanceData.value?.cpu?.usage_percent || 0, 'CPU')
)

// 内存仪表盘配置
const memoryGaugeOption = computed(() =>
  createGaugeConfig(performanceData.value?.memory?.usage_percent || 0, '内存')
)

// CPU核心使用率图表配置
const perCpuOption = computed(() => {
  const perCpuData = performanceData.value?.cpu?.per_cpu_percent || []
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const item = params[0]
        return `CPU ${item.name}: ${item.value}%`
      }
    },
    grid: {
      left: 0,
      right: 0,
      bottom: 0,
      top: 24,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: perCpuData.map((_, index) => `核心${index}`),
      axisLabel: { interval: 0, rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '使用率(%)',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'bar',
        data: perCpuData,
        itemStyle: {
          color: (params) => {
            if (params.value >= THRESHOLDS.cpu.danger) return CHART_COLORS.red
            if (params.value >= THRESHOLDS.cpu.warning)
              return CHART_COLORS.orange
            return CHART_COLORS.green
          }
        }
      }
    ]
  }
})

// 网络速率趋势图配置（双折线）
const networkLineOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    formatter: (params) => {
      let result = `${params[0].axisValue}<br/>`
      params.forEach((item) => {
        result += `${item.seriesName}: ${item.value} Mbps<br/>`
      })
      return result
    }
  },
  legend: {
    data: ['上传速率', '下载速率'],
    bottom: 0
  },
  grid: {
    left: 0,
    right: 0,
    bottom: '6%',
    top: 24,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: timeHistory.value
  },
  yAxis: {
    type: 'value',
    name: 'Mbps',
    min: 0,
    axisLabel: { formatter: '{value}' }
  },
  series: [
    {
      name: '上传速率',
      type: 'line',
      smooth: true,
      data: networkUploadHistory.value,
      itemStyle: { color: CHART_COLORS.green },
      lineStyle: { width: 2 },
      areaStyle: { color: CHART_COLORS.greenAlpha }
    },
    {
      name: '下载速率',
      type: 'line',
      smooth: true,
      data: networkDownloadHistory.value,
      itemStyle: { color: CHART_COLORS.blue },
      lineStyle: { width: 2 },
      areaStyle: { color: CHART_COLORS.blueAlpha }
    }
  ]
}))

// CPU趋势图配置
const cpuTrendOption = computed(() =>
  createTrendConfig(
    'CPU使用率',
    cpuHistory.value,
    CHART_COLORS.blue,
    CHART_COLORS.blueAlpha
  )
)

// 内存趋势图配置
const memoryTrendOption = computed(() =>
  createTrendConfig(
    '内存使用率',
    memoryHistory.value,
    CHART_COLORS.green,
    CHART_COLORS.greenAlpha
  )
)

/**
 * 计算网络总速率
 * @param {Array} interfaces - 网络接口数组
 * @returns {Object} {upload, download} Mbps值
 */
const calculateNetworkSpeed = (interfaces = []) => {
  const totalUpload = interfaces.reduce(
    (sum, iface) => sum + (iface.upload_rate || 0),
    0
  )
  const totalDownload = interfaces.reduce(
    (sum, iface) => sum + (iface.download_rate || 0),
    0
  )
  return {
    upload: bytesToMbps(totalUpload),
    download: bytesToMbps(totalDownload)
  }
}

/**
 * 更新历史数据
 * @param {Object} data - 性能数据
 */
const updateHistory = (data) => {
  const timeStr = formatTime(new Date())
  const { upload, download } = calculateNetworkSpeed(data.network)

  // 添加新数据点
  cpuHistory.value.push(data.cpu.usage_percent)
  memoryHistory.value.push(data.memory.usage_percent)
  networkUploadHistory.value.push(upload)
  networkDownloadHistory.value.push(download)
  timeHistory.value.push(timeStr)

  // 保持最多20个数据点
  if (cpuHistory.value.length > MAX_DATA_POINTS) {
    cpuHistory.value.shift()
    memoryHistory.value.shift()
    networkUploadHistory.value.shift()
    networkDownloadHistory.value.shift()
    timeHistory.value.shift()
  }

  // 防抖保存到localforage
  debouncedSave()
}

/**
 * 保存历史数据到localforage
 */
const saveHistoryToStorage = async () => {
  try {
    const dataLength = cpuHistory.value.length
    if (dataLength < 19) return

    const dataToSave = {
      cpu: cpuHistory.value.slice(0, 19),
      memory: memoryHistory.value.slice(0, 19),
      networkUpload: networkUploadHistory.value.slice(0, 19),
      networkDownload: networkDownloadHistory.value.slice(0, 19),
      time: timeHistory.value.slice(0, 19),
      savedAt: new Date().toISOString()
    }

    await localforage.setItem(STORAGE_KEY, dataToSave)
  } catch (error) {
    console.error('保存历史数据失败:', error)
  }
}

// 防抖保存
let saveTimer = null
const debouncedSave = () => {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(saveHistoryToStorage, DEBOUNCE_DELAY)
}

/**
 * 从 localforage 加载历史数据
 * @returns {Object|null} 历史数据或null
 */
const loadHistoryFromStorage = async () => {
  try {
    const savedData = await localforage.getItem(STORAGE_KEY)
    if (savedData?.cpu) {
      return {
        cpu: savedData.cpu || [],
        memory: savedData.memory || [],
        networkUpload: savedData.networkUpload || [],
        networkDownload: savedData.networkDownload || [],
        time: savedData.time || []
      }
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
  }
  return null
}

// WebSocket消息订阅token
let subscriptionToken = null

/**
 * 预估历史数据点
 * @param {Object} currentData - 当前性能数据
 * @param {number} count - 需要预估的点数
 * @param {number} existingCount - 已有数据点数
 */
const estimateHistoryPoints = (currentData, count, existingCount) => {
  if (count <= 0) return

  const now = new Date()
  const baseTime = new Date(
    now.getTime() - (19 - existingCount) * DATA_INTERVAL
  )
  const { upload, download } = calculateNetworkSpeed(currentData.network)

  for (let i = count; i > 0; i--) {
    const estimatedTime = new Date(
      baseTime.getTime() + (count - i) * DATA_INTERVAL
    )

    cpuHistory.value.push(currentData.cpu.usage_percent)
    memoryHistory.value.push(currentData.memory.usage_percent)
    networkUploadHistory.value.push(upload)
    networkDownloadHistory.value.push(download)
    timeHistory.value.push(formatTime(estimatedTime))
  }

  console.log(`预估补齐 ${count} 个数据点`)
}

/**
 * 初始加载性能数据
 */
const loadInitialPerformanceData = async () => {
  try {
    isLoading.value = true // 开始加载

    // 1. 从 localforage 加载历史数据
    const savedHistory = await loadHistoryFromStorage()

    // 2. 获取当前性能数据
    const response = await PerformanceApi.getCurrentPerformance()
    if (response.code !== 0 || !response.data) {
      isLoading.value = false
      return
    }

    console.log('初始加载性能数据:', response.data)
    performanceData.value = response.data
    lastUpdateTime.value = new Date().toLocaleString()
    isConnected.value = true

    const currentData = response.data
    let needEstimate = 19

    // 3. 处理历史数据
    if (savedHistory?.cpu?.length > 0) {
      cpuHistory.value = [...savedHistory.cpu]
      memoryHistory.value = [...savedHistory.memory]
      networkUploadHistory.value = [...savedHistory.networkUpload]
      networkDownloadHistory.value = [...savedHistory.networkDownload]
      timeHistory.value = [...savedHistory.time]

      needEstimate = Math.max(0, 19 - savedHistory.cpu.length)
      console.log(`从缓存加载了 ${savedHistory.cpu.length} 个历史数据点`)
    }

    // 4. 预估补齐数据点
    const existingCount = savedHistory?.cpu?.length || 0
    estimateHistoryPoints(currentData, needEstimate, existingCount)

    // 5. 添加当前实际数据点
    updateHistory(currentData)

    // 加载完成，延迟隐藏骨架屏以保证流畅过渡
    setTimeout(() => {
      isLoading.value = false
    }, 300)
  } catch (error) {
    console.error('加载初始性能数据失败:', error)
    isLoading.value = false
  }
}

/**
 * 处理性能数据更新
 * @param {Object} data - 性能数据
 */
const handlePerformanceUpdate = (data) => {
  console.log('收到服务器性能数据:', data)
  performanceData.value = data
  lastUpdateTime.value = new Date().toLocaleString()
  isConnected.value = true
  updateHistory(data)
}

/**
 * 检查WebSocket连接状态
 */
const checkWebSocketStatus = async () => {
  try {
    const { Ws } = await import('@/common/ws/Ws')
    const ws = Ws.getInstance()
    if (ws.socket?.readyState === WebSocket.OPEN) {
      isConnected.value = true
    }
  } catch (error) {
    console.error('检查WebSocket状态失败:', error)
  }
}

onMounted(() => {
  // 首次加载性能数据
  loadInitialPerformanceData()

  // 订阅服务器性能数据
  subscriptionToken = PubSub.subscribe(
    'server_performance',
    handlePerformanceUpdate
  )

  // 检查WebSocket连接状态
  checkWebSocketStatus()
})

onUnmounted(() => {
  // 清理防抖定时器
  if (saveTimer) {
    clearTimeout(saveTimer)
    saveTimer = null
  }

  // 取消订阅
  if (subscriptionToken) {
    PubSub.unsubscribe(subscriptionToken)
    subscriptionToken = null
  }
})
</script>

<style scoped>
.server-performance-test {
  width: 100%;
}

/* 骨架屏动画优化 */
:deep(.ant-skeleton) {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 数据加载完成后的淡入动画 */
.server-performance-test > div:not(:first-child) {
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
