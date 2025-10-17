<template>
  <div class="size-full main">
    <div
      class="h-[52px] bg-blue-600 px-[20px] w-full shadow-md layout-left-center title"
    >
      <!-- Logo部分 -->
      <div class="text-2xl font-bold h-full layout-left-center text-white">
        局域网网络监控中心
      </div>

      <!-- 菜单部分 -->
      <div class="flex h-full ml-[24px]">
        <div
          class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-2"
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
          class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-2"
          :class="
            $route.path === '/devices' ? 'text-white menu-item-active' : ''
          "
          @click="switchTo('/devices')"
        >
          设备管理
        </div>
        <div
          class="h-full layout-left-center px-[12px] cursor-pointer menu-item border-b-2"
          :class="
            $route.path === '/topology' ? 'text-white menu-item-active' : ''
          "
          @click="switchTo('/topology')"
        >
          拓扑管理
        </div>
      </div>
    </div>
    <div class="h-[calc(100vh-52px)]">
      <!-- 路由出口 -->
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 获取路由信息
const route = useRoute()
const router = useRouter()

// 页面切换方法
const switchTo = (path) => {
  router.push(path)
}
</script>

<style lang="less" scoped>
.main {
  background-color: #f5f7fa;
}
.title {
  background-color: #1677ff;
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
