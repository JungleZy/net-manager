<template>
  <div class="size-full">ddddd</div>
</template>

<script setup>
import { onMounted } from 'vue'
import SystemApi from '@/common/api/system.js'

onMounted(() => {
  SystemApi.getSystemsList().then((res) => {
    console.log(res)
  })
})
</script>

<style lang="less" scoped></style>
