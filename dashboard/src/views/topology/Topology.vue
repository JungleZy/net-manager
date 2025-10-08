<template>
  <div class="p-[12px] size-full">
    <div class="size-full bg-white rounded-lg shadow p-[12px]">
      <div class="w-full h-full project-grid" ref="container"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, nextTick, ref, useTemplateRef } from 'vue'
import { LogicFlow } from '@logicflow/core'
import {
  Control,
  DndPanel,
  SelectionSelect,
  Menu,
  MiniMap,
  Highlight,
  CurvedEdge,
  CurvedEdgeModel,
  Label
} from '@logicflow/extension'
import '@logicflow/core/lib/style/index.css'
import '@logicflow/extension/lib/style/index.css'

const containerRef = useTemplateRef('container')
let lf = null

onMounted(() => {
  nextTick(() => {
    initTopology()
  })
})

const pluginsOptions = () => {
  return {
    miniMap: {
      width: 137,
      height: 121,
      rightPosition: 8,
      bottomPosition: 8
    },
    lable: {
      isMultiple: true,
      textOverflowMode: 'ellipsis'
    }
  }
}

const initTopology = () => {
  lf = new LogicFlow({
    grid: true,
    container: containerRef.value,
    keyboard: {
      enabled: true
    },
    plugins: [DndPanel, SelectionSelect, Menu, MiniMap, Highlight],
    pluginsOptions: pluginsOptions(),
    adjustEdgeStartAndEnd: true,
    allowResize: true,
    allowRotate: true
  })
  lf.render(null)
}
</script>

<style lang="less" scoped></style>
