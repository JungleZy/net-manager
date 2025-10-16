<template>
  <div class="h-full w-full">
    <div class="w-full h-full project-grid" ref="container"></div>
  </div>
</template>

<script setup>
import {
  onMounted,
  onUnmounted,
  nextTick,
  ref,
  useTemplateRef,
  shallowRef,
  computed
} from 'vue'
import { LogicFlow } from '@logicflow/core'
import {
  Control,
  DndPanel,
  SelectionSelect,
  Group,
  GroupNode,
  GroupNodeModel
} from '@logicflow/extension'
import { Dagre } from '@logicflow/layout'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'
import CustomHtml from '@/common/node/HtmlNode'
import { default as customNodes } from '@/common/node/index'
import DeviceApi from '@/common/api/device'
import SwitchApi from '@/common/api/switch'
import TopologyApi from '@/common/api/topology'
import { message } from 'ant-design-vue'
import Firewall from '@/assets/firewall.png'
import Laptop from '@/assets/laptop.png'
import Pc from '@/assets/pc.png'
import Router from '@/assets/router.png'
import Server from '@/assets/server.png'
import Switches from '@/assets/switches.png'
import Printer from '@/assets/printer.png'

// 设备类型映射 - 移到外部作为常量,避免重复创建
const DEVICE_TYPE_MAP = Object.freeze({
  台式机: { icon: Pc, type: 'pc' },
  笔记本: { icon: Laptop, type: 'laptop' },
  服务器: { icon: Server, type: 'server' },
  路由器: { icon: Router, type: 'router' },
  交换机: { icon: Switches, type: 'switch' },
  防火墙: { icon: Firewall, type: 'firewall' },
  打印机: { icon: Printer, type: 'printer' }
})
let lf = null

let data = {
  nodes: [
    {
      id: '3',
      type: 'firewall',
      x: 200,
      y: 300,
      properties: { width: 60, height: 60, status: 'online' },
      text: { x: 200, y: 300, value: '防火墙防火墙防火墙' }
    },
    {
      id: '31',
      type: 'firewall',
      x: 652,
      y: 658,
      properties: { width: 60, height: 60, status: 'offline' },
      text: { x: 652, y: 658, value: '防火墙防火墙防火墙' }
    },
    {
      id: 'group_1',
      type: 'custom-group',
      x: 300,
      y: 120,
      // children: ["rect_3"],
      text: 'sub-process-1',
      properties: {
        isFolded: false
      }
    }
  ]
}
class CustomGroup extends GroupNode {}

class CustomGroupModel extends GroupNodeModel {
  foldedText

  initNodeData(data) {
    super.initNodeData(data)

    // 如果传入了 width 和 height，在 super 之后重新应用
    if (data.width !== undefined) {
      this.width = data.width
    }
    if (data.height !== undefined) {
      this.height = data.height
    }

    this.isRestrict =
      data.properties?.isRestrict !== undefined
        ? data.properties.isRestrict
        : true
    this.resizable = true
  }

  setAttributes() {
    super.setAttributes()
  }

  getNodeStyle() {
    const style = super.getNodeStyle()
    style.stroke = '#AEAFAE'
    style.strokeWidth = 1
    return style
  }

  foldGroup(folded) {
    super.foldGroup(folded)
    // this.isFolded = folded

    if (folded) {
      if (this.foldedText) {
        this.text = { ...this.foldedText }
      }
      if (!this.text.value) {
        this.text.value = '已折叠分组'
      }
      this.text.x = this.x + 10
      this.text.y = this.y
    } else {
      this.foldedText = { ...this.text }
      this.text.value = ''
    }
  }

  // isAllowAppendIn(nodeData) {
  //   if (nodeData.type === 'rect') {
  //     return false
  //   }
  //   return true
  // }
}
const customGroup = {
  type: 'custom-group',
  view: CustomGroup,
  model: CustomGroupModel
}

const containerRef = useTemplateRef('container')
onMounted(() => {
  nextTick(() => {
    initTopology()
  })
})

const initTopology = () => {
  console.log(lf)
  // 清理旧实例
  if (lf) {
    try {
      lf.destroy()
    } catch (error) {
      console.warn('清理旧 LogicFlow 实例失败:', error)
    }
    lf = null
  }

  // 确保container已正确挂载并获取其尺寸
  const container = containerRef.value
  if (!container) {
    console.error('容器元素未找到')
    return
  }

  const width = container.offsetWidth || 800
  const height = container.offsetHeight || 600

  try {
    lf = new LogicFlow({
      container: container,
      width: width,
      height: height,
      grid: true,
      multipleSelectKey: 'alt',
      autoExpand: false,
      keyboard: {
        enabled: true
      },
      plugins: [Group, Control, DndPanel, SelectionSelect]
    })

    lf.register(CustomHtml)
    // 注册所有自定义节点
    customNodes.forEach((node) => {
      lf.register(node)
    })

    lf.register(customGroup)
  } catch (error) {
    console.error('LogicFlow 初始化失败:', error)
    message.error('拓扑图初始化失败')
    return
  }

  lf.extension.dndPanel.setPatternItems([])

  // 添加创建分组按钮
  lf.extension.control.addItem({
    key: 'createGroup',
    iconClass: 'lf-control-create-group',
    title: '创建分组',
    text: '分组',
    onClick: (lf) => {
      handleCreateGroup(lf)
    }
  })
  console.log(data)

  lf.render(data)
}

// 创建分组功能
const handleCreateGroup = (lfInstance) => {
  if (!lfInstance) {
    console.warn('创建分组: LogicFlow 实例不存在')
    return
  }

  try {
    // 获取选中的节点
    const selectElements = lfInstance.getSelectElements(true)

    if (!selectElements?.nodes || selectElements.nodes.length < 2) {
      message.warning('请至少选择2个节点来创建分组')
      return
    }

    // 过滤掉group类型的节点，避免嵌套分组
    const normalNodes = selectElements.nodes.filter(
      (node) => node.type !== 'group'
    )

    if (normalNodes.length < 2) {
      message.warning('请选择至少两个非分组节点')
      return
    }

    // 计算选中节点的边界
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity

    for (const node of normalNodes) {
      const nodeWidth = node.properties?.width || 60
      const nodeHeight = node.properties?.height || 60

      minX = Math.min(minX, node.x - nodeWidth / 2)
      minY = Math.min(minY, node.y - nodeHeight / 2)
      maxX = Math.max(maxX, node.x + nodeWidth / 2)
      maxY = Math.max(maxY, node.y + nodeHeight / 2)
    }

    // 计算分组中心点和尺寸，留出一些边距
    const padding = 30
    const groupX = (minX + maxX) / 2
    const groupY = (minY + maxY) / 2
    const groupWidth = maxX - minX + padding * 2
    const groupHeight = maxY - minY + padding * 2

    // 创建分组节点
    lfInstance.addNode({
      type: 'customGroup',
      x: groupX,
      y: groupY,
      // 将 width 和 height 放在顶层，不放在 properties 中

      width: groupWidth,
      height: groupHeight,
      properties: {
        fillColor: '#cccccc', // 浅蓝色
        fillOpacity: 0.3, // 50% 透明度
        strokeColor: '#2196F3', // 蓝色边框
        strokeWidth: 2,
        isRestrict: false // 默认不限制子节点移动
      },
      text: {
        x: groupX,
        y: minY - 20, // 将文本放在分组顶部
        value: '新建分组',
        editable: true
      },
      children: normalNodes.map((node) => node.id)
    })

    // 清除选中状态
    lfInstance.clearSelectElements()

    message.success('分组创建成功')
  } catch (error) {
    console.error('创建分组失败:', error)
    message.error('创建分组失败')
  }
}
</script>
