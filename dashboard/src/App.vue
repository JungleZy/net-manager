<script setup>
import { legacyLogicalPropertiesTransformer } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { Ws } from './common/ws/Ws'

Ws.getInstance().run().then()
dayjs.locale('zh-cn')

const locale = zhCN
</script>

<template>
  <a-config-provider
    :locale="locale"
    :transformers="[legacyLogicalPropertiesTransformer]"
    :theme="{
      token: {
        colorPrimary: '#456a63'
      }
    }"
  >
    <a-style-provider hash-priority="high">
      <router-view />
    </a-style-provider>
  </a-config-provider>
</template>

<style lang="less"></style>
