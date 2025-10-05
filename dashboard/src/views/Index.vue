<template>
  <div class="size-full">
    <div class="h-[52px] bg-blue-600 px-[20px] w-full shadow-md layout-left-center title">
      <!-- Logo部分 -->
      <div class="text-[16px] font-bold h-full layout-left-center text-white mr-8">
        网络管理中心
      </div>
      
      <!-- 菜单部分 -->
      <div class="flex h-full ml-[24px]">
        <div 
          class="h-full layout-left-center px-[12px] cursor-pointer menu-item"
          :class="$route.path === '/home' || $route.path === '/' ? 'text-white border-b-2 menu-item-active' : ''"
          @click="switchTo('/home')"
        >
          首页
        </div>
        <div 
          class="h-full layout-left-center px-[12px] cursor-pointer menu-item"
          :class="$route.path === '/devices' ? 'text-white border-b-2 menu-item-active' : ''"
          @click="switchTo('/devices')"
        >
          设备
        </div>
        <div 
          class="h-full layout-left-center px-[12px] cursor-pointer menu-item"
          :class="$route.path === '/topology' ? 'text-white border-b-2 menu-item-active' : ''"
          @click="switchTo('/topology')"
        >
          拓扑图
        </div>
      </div>
    </div>
    <div class="h-[calc(100vh-52px)] bg-[#fff]">
      <!-- 路由出口 -->
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SystemApi from '@/common/api/system.js'

// 获取路由信息
const route = useRoute()
const router = useRouter()

// 页面切换方法
const switchTo = (path) => {
  router.push(path)
}

// 页面挂载时获取系统列表
onMounted(() => {
  SystemApi.getSystemsList().then((res) => {
    console.log(res)
  })
})
</script>

<style lang="less" scoped>
.layout-left-center {
  display: flex;
  align-items: center;
}
.title{
  background-color: #1677ff;
  color: #fff;
  
  .menu-item{
    color: #fff;
    &-active{
      border-color: #1677ff;
    }
  }
}
</style>
