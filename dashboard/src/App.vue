<script setup>
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
dayjs.locale('zh-cn')

const locale = zhCN
</script>

<template>
  <a-config-provider :locale="locale">
    <router-view />
  </a-config-provider>
</template>

<style lang="less"></style>
