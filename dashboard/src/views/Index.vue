<template>
  <div class="size-full main">
    <div
      class="h-[52px] bg-blue-600 px-[20px] w-full shadow-md layout-side title"
    >
      <!-- Logo部分 -->
      <div class="h-full layout-left-center">
        <div class="text-2xl font-bold h-full layout-left-center text-white">
          网络监控中心
        </div>

        <!-- 菜单部分 -->
        <div class="flex h-full ml-[24px]">
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/home' || $route.path === '/'
                ? 'text-white menu-item-active'
                : ''
            "
            @click="switchTo('/home')"
          >
            监控面板
          </div>
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/network' ? 'text-white menu-item-active' : ''
            "
            @click="switchTo('/network')"
          >
            网络拓扑
          </div>
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/devices' ? 'text-white menu-item-active' : ''
            "
            @click="switchTo('/devices')"
          >
            设备管理
          </div>
          <div
            class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-3"
            :class="
              $route.path === '/topology' ? 'text-white menu-item-active' : ''
            "
            @click="switchTo('/topology')"
          >
            拓扑管理
          </div>
        </div>
      </div>

      <div class="h-full layout-right-center">
        <div
          class="h-full layout-center cursor-pointer text-sm"
          @click="openAgentModal"
        >
          <DownloadOutlined class="mr-[2px]" />下载探针
        </div>
      </div>
    </div>
    <div class="h-[calc(100vh-52px)]">
      <!-- 路由出口 -->
      <router-view></router-view>
    </div>
    <a-modal
      v-model:open="agentVisible"
      width="724px"
      centered
      title="下载探针"
      :footer="null"
    >
      <AgentDownload />
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DownloadOutlined } from '@ant-design/icons-vue'
import AgentDownload from '@/components/agent/AgentDownload.vue'

// 获取路由信息
const route = useRoute()
const router = useRouter()
const agentVisible = ref(false)

// 页面切换方法
const switchTo = (path) => {
  router.push(path)
}
const openAgentModal = () => {
  agentVisible.value = true
}
</script>

<style lang="less" scoped>
@import '../styles/color.less';
.main {
  background-color: #f5f7fa;
}
.title {
  background-color: @firstColor;
  color: #fff;

  .menu-item {
    color: #fff;
    border-color: transparent;

    &-active {
      border-color: #ffffff;
    }
  }
}
</style>
