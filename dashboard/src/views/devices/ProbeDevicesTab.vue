<template>
  <div class="size-full" ref="el">
    <div class="mb-[12px] layout-side">
      <div>
        <span class="mr-2 font-medium">IP地址:</span>
        <a-input
          v-model:value="filterIP"
          placeholder="请输入IP地址"
          style="width: 200px; margin-right: 12px"
        />
        <span class="mr-2 font-medium">设备类型:</span>
        <a-select
          v-model:value="filterType"
          style="width: 100px; margin-right: 12px"
        >
          <a-select-option value="">全部类型</a-select-option>
          <a-select-option value="台式机">台式机</a-select-option>
          <a-select-option value="笔记本">笔记本</a-select-option>
          <a-select-option value="服务器">服务器</a-select-option>
          <a-select-option value="__unset__">未知</a-select-option>
          <a-select-option value="其他">其他</a-select-option>
        </a-select>

        <span class="mr-2 font-medium">操作系统:</span>
        <a-select
          v-model:value="filterOS"
          style="width: 100px; margin-right: 12px"
        >
          <a-select-option value="">全部系统</a-select-option>
          <a-select-option value="Windows">Windows</a-select-option>
          <a-select-option value="Linux">Linux</a-select-option>
        </a-select>

        <span class="mr-2 font-medium">状态:</span>
        <a-select
          v-model:value="filterStatus"
          style="width: 80px; margin-right: 12px"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="online">在线</a-select-option>
          <a-select-option value="offline">离线</a-select-option>
        </a-select>
        <a-button @click="clearFilter">重置</a-button>
      </div>
      <a-button class="layout-center" type="primary" @click="openProcessModal">
        <template #icon>
          <AlertOutlined />
        </template>
        进程管理
      </a-button>
    </div>
    <!-- 设备列表 -->
    <div class="w-full h-[calc(100%-44px)] overflow-auto">
      <a-table
        :columns="columns"
        :data-source="filteredDevices"
        :pagination="tablePagination"
        :loading="tableLoading"
        size="small"
        row-key="id"
        bordered
        :scroll="{ y: height - 180 + 'px' }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record, index }">
          <template v-if="column.dataIndex === 'hostname'">
            {{ record.hostname || '未知设备' }}
          </template>
          <template v-else-if="column.dataIndex === 'ip_address'">
            {{ record.ip_address || '未知' }}
          </template>
          <template v-else-if="column.dataIndex === 'id'">
            {{ record.id || '未知' }}
          </template>
          <template v-else-if="column.dataIndex === 'machine_type'">
            {{ formatMachineType(record.machine_type) }}
          </template>
          <template v-else-if="column.dataIndex === 'type'">
            <div class="flex items-center justify-center">
              <a-tooltip
                v-if="record.type && getDeviceIcon(record.type)"
                :title="record.type"
              >
                <div
                  v-html="getDeviceIcon(record.type)"
                  class="device-icon"
                  style="width: 28px; height: 28px; cursor: help"
                ></div>
              </a-tooltip>
              <span style="height: 28px" class="layout-center" v-else>{{
                record.type || '未设置'
              }}</span>
            </div>
          </template>
          <template v-else-if="column.dataIndex === 'online'">
            <a-tag :color="record.online ? 'green' : 'red'" style="margin: 0">
              {{ record.online ? '在线' : '离线' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'os_name'">
            <div class="layout-center" v-if="record.os_name === 'Linux'">
              <a-tooltip title="Linux">
                <svg
                  t="1761046997370"
                  class="icon"
                  viewBox="0 0 1024 1024"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  p-id="1829"
                  width="24"
                  height="24"
                >
                  <path
                    d="M525.2 198.3c-8.6 5.6-15.2 13.8-18.9 23.4-3.8 12.4-3.2 25.6 1.5 37.7 3.9 12.7 11.7 23.8 22.2 31.8 5.4 3.8 11.6 6.2 18.2 7 6.6 0.8 13.2-0.3 19.1-3.3 7-3.9 12.6-10 15.9-17.3 3.2-7.4 5-15.3 5.2-23.3 0.7-10.2-0.6-20.4-3.8-30.1-3.5-10.6-10.3-19.7-19.5-25.9-4.7-3-9.9-5-15.4-5.8-5.5-0.8-11.1-0.2-16.3 1.8-2.9 1.2-5.7 2.7-8.3 4.5"
                    fill="#FFFFFF"
                    p-id="1830"
                  ></path>
                  <path
                    d="M810.2 606.5c-5.1-28.3-13.1-56-23.8-82.6-7.3-19.8-17.2-38.6-29.5-55.8-12.4-16.5-28.1-30.4-40.2-47.1-6.4-8.7-11.8-18.4-18.5-26.9-2.7-5.6-5.3-11.2-7.9-16.8-8-17.5-15.3-35.4-24.8-52-1.5-2.6-3.1-5.2-4.6-7.7-1.2-16-2.9-32-3.8-48 0.7-32.1-2-64.3-8.1-95.9-4.2-15.1-10.6-29.6-19-42.8-9.8-15.6-22.4-29.2-37.2-40.1-24.1-17.1-52.9-26.3-82.4-26.4-21.7-0.5-43.2 4.4-62.5 14.4-20.3 11.1-36.7 28.2-47 48.9-9.6 20.9-14.7 43.5-15 66.5-0.8 22.6 1.3 45 2.2 67.6 0.9 23.4 0.4 46.9 2.3 70.3 0.6 7.5 1.5 15 1.5 22.6 0 3.8-0.2 7.6-0.3 11.3l-0.3 0.8c-10.2 17.3-21.5 34-33.8 49.9-8.6 10.9-17.2 21.7-25.9 32.4-11.3 12.7-20.9 26.8-28.5 42-5.1 13.2-9.2 26.8-12.4 40.6l-0.3 1.1c-4.8 15.9-10.8 31.3-18 46.2-0.7 1.4-1.4 2.9-2 4.2-4.3 8.9-8.8 17.8-13.5 26.5l-5.4 10.1c-3.4 6.1-6.4 12.4-9 18.8-1.5 3.9-2.7 7.9-3.4 12-1.3 8.7-0.7 17.5 1.6 25.9 0.5 2.1 1.2 4.2 1.9 6.3 2.2 6.2 4.8 12.3 7.9 18.1 1.4 2.7 2.9 5.3 4.3 8l1.3 1.9c1.4 2.5 2.9 5 4.4 7.4l0.2 0.3c1.7 2.8 3.6 5.5 5.4 8.2l0.3 0.4c1.9 2.6 3.8 5.3 5.8 7.9 7.4 28.9 21 55.8 39.7 79-2.9 5.1-5.5 10.1-8.4 15.1-10.2 14.8-18.6 30.7-25.1 47.4-2.7 8.6-3.4 17.7-1.9 26.6 1.4 9 6 17.1 13 23 4.7 3.6 10.1 6.1 15.8 7.3 5.7 1.2 11.6 1.8 17.5 1.5 22.2-1.7 44.2-6.1 65.4-12.9 12.8-3.4 25.6-6.4 38.6-9 13.5-3.1 27.2-5 41-5.6 3.4 0.1 6.8-0.1 10.1-0.3 9.4 1 18.8 1.4 28.3 1l3.5-0.2c2.4 0.3 4.9 0.4 7.4 0.6 16.6 0.9 33.1 2.6 49.5 5.1 14.4 2.2 28.8 5 43 8.5 21.9 6.6 44.4 11 67.3 12.9 6 0.3 12-0.2 18-1.4 5.9-1.2 11.5-3.8 16.3-7.4 7-5.8 11.6-13.9 13.1-22.9 1.5-8.9 0.8-18-1.9-26.6-6.6-16.7-15.1-32.6-25.5-47.3-3.6-6.1-7-12.4-10.6-18.5 15.5-17.3 29.2-36.3 40.7-56.5 7 0.4 13.9-0.4 20.6-2.6 17.5-5.9 32.7-17.3 43.3-32.5 3.2-4.5 5.7-9.5 7.2-14.8 6.9-10.7 11.6-22.7 13.8-35.3 3.2-20.8 2.7-42.1-1.5-62.7h-0.2z m0 0"
                    fill="#020204"
                    p-id="1831"
                  ></path>
                  <path
                    d="M425.6 323.2c-3.1 4-5.3 8.7-6.4 13.6-1.1 4.9-1.8 10-1.9 15 0.3 10.1-0.5 20.2-2.5 30.1-3.5 10.3-8.8 19.8-15.6 28.3-11.7 14.7-20.9 31.2-27.2 48.8-3.2 10.9-4.3 22.3-3.1 33.7-12.1 17.9-22.6 36.9-31.3 56.7-13.4 29.9-22 61.8-25.5 94.4-4.3 40.1 1.6 80.6 17 117.8 11.3 26.8 28.5 50.8 50.3 70.1 11.2 9.7 23.5 17.9 36.7 24.4 46.7 22.8 101.4 22.3 147.6-1.4 23.1-13.5 44.2-30.2 62.6-49.5 11.9-10.8 22.5-22.9 31.8-36.1 15.5-26.9 24.6-57.1 26.5-88.1 9.6-53.6 3.7-108.8-16.9-159.2-8.1-16.8-18.8-32.2-31.8-45.6a252.5 252.5 0 0 0-20.2-68c-7.2-15.5-15.9-30.3-22.6-46.2-2.7-6.5-5.1-13.1-8.1-19.4-2.9-6.4-6.9-12.3-11.8-17.3-5.3-4.9-11.6-8.6-18.5-10.7-6.9-2.2-14-3.4-21.2-3.6-14.4-0.7-28.9 1.1-43.1 0.6-11.5-0.5-22.8-2.5-34.3-1.8-5.7 0.3-11.4 1.4-16.7 3.5-5.4 2.1-10.1 5.5-13.8 10m4.6-125.1c-5.4 0.4-10.5 2.7-14.4 6.4-3.9 3.7-6.8 8.4-8.4 13.5-2.7 10.4-3.4 21.3-1.9 32 0.2 9.7 1.9 19.4 5.1 28.6 1.8 4.5 4.4 8.7 7.8 12.2 3.4 3.5 7.7 6.1 12.4 7.3 4.5 1.1 9.2 0.9 13.5-0.5 4.3-1.4 8.3-3.8 11.5-7 4.7-4.8 8.1-10.7 9.8-17.1 1.7-6.4 2.5-13.1 2.3-19.8 0-8.3-1.3-16.6-3.8-24.6s-6.8-15.3-12.6-21.4c-2.8-2.9-6-5.4-9.6-7.2-3.7-1.7-7.7-2.6-11.7-2.4m95 0c-8.6 5.6-15.2 13.8-18.9 23.4-3.8 12.4-3.2 25.6 1.5 37.7 3.9 12.7 11.7 23.8 22.2 31.8 5.4 3.8 11.6 6.2 18.2 7 6.6 0.8 13.2-0.3 19.1-3.3 7-3.9 12.6-10 15.9-17.3 3.2-7.4 5-15.3 5.2-23.3 0.7-10.2-0.6-20.4-3.8-30.1-3.5-10.6-10.3-19.7-19.5-25.9-4.7-3-9.9-5-15.4-5.8-5.5-0.8-11.1-0.2-16.3 1.8-2.9 1.2-5.7 2.7-8.3 4.5"
                    fill="#FFFFFF"
                    p-id="1832"
                  ></path>
                  <path
                    d="M544.5 223.6c-3.2 0.2-6.2 1.2-8.9 2.9s-5 4-6.8 6.6c-3.4 5.3-5.3 11.5-5.4 17.9-0.3 4.7 0.4 9.5 1.9 14s4.3 8.5 7.9 11.5c3.8 3.1 8.4 4.9 13.3 5.2 4.9 0.2 9.7-1.1 13.7-3.9 3.2-2.3 5.8-5.2 7.6-8.7 1.8-3.4 2.9-7.2 3.4-11 1-6.8-0.2-13.8-3.2-19.9-3.1-6.2-8.4-10.9-14.8-13.4-2.8-1.1-5.7-1.5-8.7-1.4"
                    fill="#020204"
                    p-id="1833"
                  ></path>
                  <path
                    d="M430.2 198.3c-5.4 0.4-10.5 2.7-14.4 6.4-3.9 3.7-6.8 8.4-8.4 13.5-2.7 10.4-3.4 21.3-1.9 32 0.2 9.7 1.9 19.4 5.1 28.6 1.8 4.6 4.4 8.7 7.8 12.2 3.4 3.5 7.7 6.1 12.4 7.3 4.5 1.1 9.2 0.9 13.5-0.5 4.3-1.4 8.3-3.8 11.5-7 4.7-4.8 8.1-10.7 9.8-17.1 1.7-6.4 2.5-13.1 2.3-19.8 0-8.3-1.3-16.6-3.8-24.6s-6.8-15.3-12.6-21.4c-2.8-2.9-6-5.4-9.6-7.2-3.7-1.7-7.7-2.6-11.7-2.4"
                    fill="#FFFFFF"
                    p-id="1834"
                  ></path>
                  <path
                    d="M417.3 242.8c-1.3 6.7-1 13.7 1.1 20.2 1.6 4.3 4 8.2 7.2 11.5 2 2.2 4.3 4.1 7 5.4 2.7 1.4 5.7 1.8 8.7 1.1 2.7-0.7 5-2.3 6.7-4.5 1.7-2.2 2.9-4.7 3.7-7.3 2.3-7.8 2.1-16.1-0.4-23.9-1.6-5.7-4.7-10.9-9.1-14.8-2.1-1.8-4.7-3.2-7.4-3.9-2.8-0.7-5.7-0.5-8.4 0.7-2.8 1.4-5.1 3.7-6.5 6.5-1.4 2.8-2.3 5.8-2.7 8.9"
                    fill="#020204"
                    p-id="1835"
                  ></path>
                  <path
                    d="M404.6 326.9c0.2 0.9 0.5 1.8 1 2.5 0.9 1.4 2 2.5 3.4 3.4 1.3 0.9 2.6 1.7 3.9 2.5 6.9 4.7 13 10.5 17.9 17.3 6 9.4 13.5 17.8 22 25 6.5 4.5 14.1 7.2 22 7.9 9.2 0.7 18.5-0.4 27.4-3.2 8.2-2.4 16.1-5.8 23.5-10.3 12.7-10.2 26.3-19.2 40.7-26.7 3.4-1.2 6.8-2.1 10-3.6 3.3-1.4 6.1-3.8 7.8-7 1.1-3.2 1.8-6.6 1.9-10 0.5-3.6 1.7-7.1 2.3-10.7 0.8-3.6 0.5-7.3-0.8-10.8-1.4-2.7-3.6-4.9-6.3-6.3-2.7-1.3-5.7-2.1-8.7-2.2-6.1 0.2-12.1 0.8-18 1.8-8 0.7-16-0.3-24 0-9.9 0.3-19.8 2.5-29.8 2.9-11.4 0.6-22.7-1.2-34.1-1.7-4.9-0.3-9.9-0.1-14.8 0.7-4.9 0.7-9.6 2.5-13.7 5.3-3.8 3-7.3 6.2-10.7 9.6-1.8 1.6-3.8 3-5.9 4.1-2.2 1.1-4.5 1.7-7 1.6-1.2-0.2-2.5-0.2-3.7 0-0.7 0.3-1.4 0.7-1.9 1.2l-1.5 1.8c-1 1.5-1.9 3.1-2.6 4.7"
                    fill="#D99A03"
                    p-id="1836"
                  ></path>
                  <path
                    d="M429.7 301.7c-4 2.4-7.9 5-11.8 7.7-2.1 1.3-3.8 3-5.1 5.1-0.7 1.6-1 3.3-0.9 5 0.1 1.7 0.1 3.4 0 5.1-0.1 1.1-0.5 2.3-0.5 3.5 0 0.6 0 1.2 0.2 1.7 0.2 0.6 0.4 1.1 0.8 1.5 0.5 0.5 1.2 0.9 2 1.1 0.7 0.2 1.5 0.3 2.3 0.5 3.5 1 6.7 2.9 9.3 5.4 2.7 2.4 5.1 5.2 8 7.5 8 6 17.7 9.1 27.6 9 9.9-0.2 19.7-1.6 29.2-4.1 7.5-1.6 14.9-3.6 22.1-6.1 11.2-4.2 21.5-10.3 30.4-18.2 3.9-3.8 8-7.2 12.4-10.3 4-2.5 8.7-4.2 12.7-6.6 0.4-0.2 0.7-0.5 1.1-0.7 0.3-0.3 0.6-0.6 0.8-1 0.3-0.7 0.3-1.5 0-2.2-0.2-0.7-0.5-1.3-0.9-1.8-0.5-0.6-1.1-1.2-1.7-1.7-4.6-3.4-10.1-5.3-15.8-5.5-5.8-0.4-11.3 0-16.9-1.1-5.2-1.1-10.3-2.6-15.3-4.4-5.3-1.7-10.7-3-16.3-3.9-13-2.1-26.2-1.8-39.1 1-12.1 2.7-23.8 7.3-34.6 13.5"
                    fill="#604405"
                    p-id="1837"
                  ></path>
                  <path
                    d="M428.4 288.1c-5.8 3.9-11 8.7-15.5 14.1-2.6 3-4.7 6.5-6.1 10.3-0.9 3-1.5 6.1-2 9.2-0.3 1.1-0.5 2.3-0.5 3.5 0 0.6 0.1 1.2 0.3 1.7 0.2 0.6 0.5 1.1 0.9 1.5 0.7 0.7 1.6 1.1 2.6 1.3 0.9 0.2 1.9 0.2 2.9 0.3 4.4 0.7 8.5 2.5 12.1 5.1 3.6 2.5 7 5.4 10.7 7.8 8.4 5 18 7.7 27.8 7.9 9.8 0.2 19.5-0.8 29-2.9 7.6-1.4 15.1-3.5 22.4-6.3 10.9-4.7 21.1-10.8 30.4-18.2 4.3-3.2 8.5-6.6 12.4-10.3 1.3-1.3 2.6-2.6 4-3.8 1.4-1.2 3-2.1 4.7-2.7 2.7-0.7 5.5-0.8 8.3-0.1 2 0.5 4.1 0.7 6.2 0.7 1.1 0 2.1-0.2 3.1-0.5 1-0.4 1.9-1 2.5-1.8 0.9-1.1 1.3-2.4 1.3-3.8s-0.4-2.7-1.1-3.9c-1.5-2.3-3.8-4.1-6.3-5.1-3.5-1.4-7.1-2.5-10.8-3.2-11.3-2.7-22.3-6.7-32.7-11.9-5.2-2.6-10.1-5.4-15.3-8.1-5.2-2.9-10.6-5.4-16.2-7.2-12.9-3.5-26.6-2.9-39.1 1.8-14 4.9-26.5 13.4-36.1 24.7"
                    fill="#F5BD0C"
                    p-id="1838"
                  ></path>
                  <path
                    d="M493.5 272.2c0.7 2.3 4.3 1.9 6.4 2.9 2.1 1 3.3 2.9 5.3 3.1 2.1 0.2 5-0.7 5.3-2.6 0.4-2.6-3.4-4.2-5.8-5.1-3.2-1.5-6.8-1.6-10-0.2-0.7 0.3-1.4 1.2-1.2 1.9z m-34.4-1.2c-2.7-0.9-7.1 3.8-5.8 6.3 0.4 0.7 1.6 1.5 2.4 1.1 0.8-0.4 2.3-3.1 3.6-4 1-0.8 0.8-3.1-0.2-3.4z m0 0"
                    fill="#CD8907"
                    p-id="1839"
                  ></path>
                  <path
                    d="M887.7 829.8c-2 5.2-4.9 10-8.5 14.3-8.4 9-18.6 16.2-29.8 21.2-19 8.8-37.5 18.6-55.5 29.3-11.7 7.8-22.6 16.6-32.7 26.4-8.3 8.7-17.2 16.7-26.6 24.2-9.8 7.2-21.1 12.1-33.1 14-14.7 1.9-29.6-0.4-43.1-6.5-9.7-3.7-18.1-10.2-24-18.8-5-9.2-7.3-19.5-6.8-29.9 0.6-18.3 2.8-36.5 6.6-54.5 2.6-15 5.2-30 6.8-45.1 2.8-27.6 3.1-55.3 1-82.9-0.5-4.6-0.5-9.3 0-13.9 0.6-9.4 8.5-16.6 18-16.5 4.3-0.1 8.6 0.3 12.8 1.1 10 1.2 20 2.9 29.8 5.2 6.1 1.6 12.2 3.8 18.3 5.5 10.2 3 21 3.9 31.6 2.9 11.1-2.6 22.4-4.3 33.8-5.3 4.7 0.2 9.4 1 13.8 2.4 4.6 1.3 8.9 3.6 12.4 6.9 2.5 2.7 4.5 5.8 5.8 9.2 1.9 5.1 3.1 10.4 3.5 15.8 0.2 4.8 0.6 9.6 1.2 14.4 1.7 7.7 5.4 14.9 10.6 20.9 5.3 5.8 11 11.2 17.2 16 5.9 5.2 12.1 10 18.6 14.4 3.1 2.1 6.2 4 9.1 6.3 3 2.2 5.5 5 7.4 8.2 2.4 4.4 3.2 9.5 2 14.4"
                    fill="#F5BD0C"
                    p-id="1840"
                  ></path>
                  <path
                    d="M887.7 829.8c-2 5.2-4.9 10-8.5 14.3-8.4 9-18.6 16.2-29.8 21.2-19 8.8-37.5 18.6-55.5 29.3-11.7 7.8-22.6 16.6-32.7 26.4-8.3 8.7-17.2 16.7-26.6 24.2-9.8 7.2-21.1 12.1-33.1 14-14.7 1.9-29.6-0.4-43.1-6.5-9.7-3.7-18.1-10.2-24-18.8-5-9.2-7.3-19.5-6.8-29.9 0.6-18.3 2.8-36.5 6.6-54.5 2.6-15 5.2-30 6.8-45.1 2.8-27.6 3.1-55.3 1-82.9-0.5-4.6-0.5-9.3 0-13.9 0.6-9.4 8.5-16.6 18-16.5 4.3-0.1 8.6 0.3 12.8 1.1 10 1.2 20 2.9 29.8 5.2 6.1 1.6 12.2 3.8 18.3 5.5 10.2 3 21 3.9 31.6 2.9 11.1-2.6 22.4-4.3 33.8-5.3 4.7 0.2 9.4 1 13.8 2.4 4.6 1.3 8.9 3.6 12.4 6.9 2.5 2.7 4.5 5.8 5.8 9.2 1.9 5.1 3.1 10.4 3.5 15.8 0.2 4.8 0.6 9.6 1.2 14.4 1.7 7.7 5.4 14.9 10.6 20.9 5.3 5.8 11 11.2 17.2 16 5.9 5.2 12.1 10 18.6 14.4 3.1 2.1 6.2 4 9.1 6.3 3 2.2 5.5 5 7.4 8.2 2.4 4.4 3.2 9.5 2 14.4M259.4 676.3c4.9-1.9 10.2-2.4 15.4-1.4 5.2 1 10.1 3.1 14.4 6.1 8.3 6.3 15.5 14.1 21.2 22.8 14.1 19.4 27.6 39.2 39.9 59.8 10 16.7 19.1 33.9 30.6 49.6 7.5 10.2 16 19.7 23.6 29.9 7.9 10 13.9 21.4 17.6 33.5 4.4 16.1 2.6 33.2-4.9 48.1-5.4 10.4-13.5 19.1-23.4 25.1-10 6-21.5 9-33.2 8.7-18.4-2.5-36.2-8.1-52.6-16.6-34.9-13.9-72.8-18.3-108.8-29.1-11.1-3.3-21.9-7.3-33.1-10.3-5-1.2-9.9-2.7-14.7-4.7-4.7-2-8.8-5.4-11.5-9.7-2-3.5-3-7.5-2.9-11.5 0.1-4 0.9-7.9 2.3-11.5 2.7-7.5 7.1-14.2 10-21.6 4.4-12.2 6.1-25.3 5-38.2-0.6-12.9-2.9-25.8-3.6-38.7-0.6-5.8-0.4-11.6 0.6-17.3 1.5-11.4 10.4-20.5 21.9-22.2 5.3-0.9 10.6-1.3 15.9-1 5.3 0.3 10.7 0.3 16 0 5.3-0.3 10.6-1.8 15.3-4.3 4.3-2.6 8.1-6.2 11-10.4 2.9-4.2 5.5-8.5 7.9-13 2.4-4.5 5.1-8.7 8.3-12.7 3-4.1 7.1-7.2 11.8-9.4"
                    fill="#F5BD0C"
                    p-id="1841"
                  ></path>
                  <path
                    d="M259.4 676.4c4.9-1.9 10.2-2.4 15.4-1.4 5.2 1 10.1 3.1 14.4 6.1 8.3 6.3 15.5 14.1 21.2 22.8 14.1 19.4 27.6 39.2 39.9 59.8 10 16.7 19.1 33.9 30.6 49.6 7.5 10.2 16 19.7 23.6 29.9 7.9 10 13.9 21.4 17.6 33.5 4.4 16.1 2.6 33.2-4.9 48.1-5.4 10.4-13.5 19.1-23.4 25.1-10 6-21.5 9-33.2 8.7-18.4-2.5-36.2-8.1-52.6-16.6-34.9-13.9-72.8-18.3-108.8-29.1-11.1-3.3-21.9-7.3-33.1-10.3-5-1.2-9.9-2.7-14.7-4.7-4.7-2-8.8-5.4-11.5-9.7-2-3.5-3-7.5-2.9-11.5 0.1-4 0.9-7.9 2.3-11.5 2.7-7.5 7.1-14.2 10-21.6 4.4-12.2 6.1-25.3 5-38.2-0.6-12.9-2.9-25.7-3.6-38.7-0.6-5.8-0.4-11.6 0.6-17.3 1.5-11.4 10.4-20.5 21.9-22.2 5.3-0.9 10.6-1.3 15.9-1 5.3 0.3 10.7 0.3 16 0 5.3-0.3 10.6-1.8 15.3-4.3 4.3-2.6 8.1-6.2 11-10.4 2.9-4.2 5.5-8.5 7.9-13 2.4-4.5 5.1-8.7 8.3-12.7 3-4.1 7.1-7.3 11.8-9.4"
                    fill="#F5BD0C"
                    p-id="1842"
                  ></path>
                  <path
                    d="M267.1 684.8c4.4-1.7 9.3-2 13.9-0.9s8.9 3.2 12.6 6.2c7.1 6.2 13.1 13.6 17.6 21.9 12 19.4 23.7 39 34.6 59 7.9 15.3 16.8 30.1 26.6 44.2 6.8 9.2 14.6 17.6 21.6 26.6 7.3 8.9 12.8 19 16.2 29.9 4 14.3 2.3 29.6-4.5 42.9-5 9.4-12.5 17.3-21.7 22.6-9.2 5.4-19.8 8-30.4 7.5-16.7-2.6-32.9-7.6-48.2-14.9-30.4-11.1-63.5-12.5-94.7-21.2-11.2-3-22.1-7.1-33.4-9.9-5-1.1-10-2.5-14.8-4.3-4.8-1.8-9-5.2-11.8-9.5-1.8-3.4-2.7-7.2-2.5-11 0.2-3.8 1-7.6 2.4-11.2 2.7-7.1 7-13.6 9.7-20.7 3.8-11 5.1-22.6 3.9-34.2-0.8-11.5-2.9-22.9-3.5-34.5-0.4-5.1-0.2-10.3 0.7-15.4 0.9-5.1 3.3-9.8 6.9-13.6 4.2-3.8 9.4-6.3 15-7 5.6-0.7 11.2-0.7 16.7 0 5.6 0.7 11.2 0.9 16.8 0.8 11 0 21-6.4 25.7-16.4 2.3-4.5 4.3-9.2 5.9-13.9 1.7-4.8 4-9.3 6.7-13.6 2.8-4.3 6.8-7.7 11.5-9.7"
                    fill="#F5BD0C"
                    p-id="1843"
                  ></path>
                </svg>
              </a-tooltip>
            </div>
            <div class="layout-center" v-else-if="record.os_name === 'Windows'">
              <a-tooltip title="Windows">
                <svg
                  t="1761047141548"
                  class="icon"
                  viewBox="0 0 1024 1024"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  p-id="2007"
                  width="24"
                  height="24"
                >
                  <path
                    d="M456 484V160.1l-335.9 72V484H456zM512 484h391.8V64.2l-391.8 84V484zM456 540H120.2v251.9l335.9 72V540zM512 540v335.9l391.8 84V540H512z"
                    fill="#00adef"
                    p-id="2008"
                  ></path>
                </svg>
              </a-tooltip>
            </div>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <EditOutlined
              @click="openEditModal(record)"
              style="font-size: 16px; color: #1677ff"
              class="cursor-pointer"
            />
            <a-popconfirm
              placement="topRight"
              title="确定要删除这个设备吗？"
              @confirm="deleteDevice(record.id)"
              ok-text="确定"
              cancel-text="取消"
            >
              <DeleteOutlined
                style="font-size: 16px; color: red"
                class="cursor-pointer ml-2"
              />
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 创建/编辑设备模态框 -->
    <DeviceAddModal
      v-model:visible="showModal"
      :is-editing="isEditing"
      :device-data="currentDevice"
      @ok="saveDevice"
      @cancel="closeModal"
    />

    <!-- 服务详情模态框 -->
    <ServiceDetailModal
      v-model:visible="showServicesModal"
      :services-list="servicesList"
      :device-name="currentDeviceName"
      @cancel="closeServicesModal"
    />

    <!-- 进程详情模态框 -->
    <ProcessDetailModal
      v-model:visible="showProcessesModal"
      :processes-list="processesList"
      :device-name="currentDeviceName"
      @cancel="closeProcessesModal"
    />

    <!-- 网口详情 Popover 气泡卡片：已在列渲染中实现 -->
    <ProcessModal v-model:open="processVisible" />
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  shallowRef,
  watch,
  h,
  useTemplateRef
} from 'vue'
import { useElementSize } from '@vueuse/core'
import {
  DeleteOutlined,
  EditOutlined,
  AlertOutlined
} from '@ant-design/icons-vue'
import { formatMachineType } from '@/common/utils/Utils.js'
import { message, Tooltip, Popover, Table, Empty, Spin } from 'ant-design-vue'
import DeviceAddModal from '@/components/devices/DeviceAddModal.vue'
import ServiceDetailModal from '@/components/devices/ServiceDetailModal.vue'
import ProcessDetailModal from '@/components/devices/ProcessDetailModal.vue'
import ProcessModal from '../../components/devices/ProcessModal.vue'
import DeviceApi from '@/common/api/device.js'
import { wsCode } from '@/common/ws/Ws.js'
import { PubSub } from '@/common/utils/PubSub.js'

// 导入设备类型SVG图标
import PCIcon from '@/assets/svg/TopologyPC.svg?raw'
import LaptopIcon from '@/assets/svg/TopologyLaptop.svg?raw'
import ServerIcon from '@/assets/svg/TopologyServer.svg?raw'
import PrinterIcon from '@/assets/svg/TopologyPrinter.svg?raw'
import FirewallIcon from '@/assets/svg/TopologyFireWall.svg?raw'
import RouterIcon from '@/assets/svg/TopologyRouter.svg?raw'
import SwitchIcon from '@/assets/svg/TopologySwitches.svg?raw'

// 常量定义
const ANIMATION_DURATION = 3000 // 动画持续时间
const CHANGE_KEYS = [
  'timestamp',
  'cpu_usage',
  'memory_usage',
  'disk_usage',
  'services_count',
  'processes_count'
] // 需要监听变化的字段

const DEVICE_ICON_MAP = {
  台式机: PCIcon,
  笔记本: LaptopIcon,
  服务器: ServerIcon,
  打印机: PrinterIcon,
  防火墙: FirewallIcon,
  路由器: RouterIcon,
  交换机: SwitchIcon
}
const el = useTemplateRef('el')
const { width, height } = useElementSize(el)

const sanitizeSvg = (raw) => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(raw, 'image/svg+xml')
  const el = doc.documentElement
  el.removeAttribute('width')
  el.removeAttribute('height')
  el.setAttribute('viewBox', el.getAttribute('viewBox') || '0 0 1024 1024')
  return new XMLSerializer().serializeToString(el)
}
const SANITIZED_ICON_MAP = {}
Object.keys(DEVICE_ICON_MAP).forEach((k) => {
  const raw = DEVICE_ICON_MAP[k]
  if (raw) {
    SANITIZED_ICON_MAP[k] = sanitizeSvg(raw)
  }
})
const getDeviceIcon = (type) => {
  const icon = SANITIZED_ICON_MAP[type]
  return icon || null
}

// 定义组件属性
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: () => ({})
  }
})

// 使用 defineModel 替代 changedTimestamps prop
const changedTimestamps = defineModel('changedTimestamps', {
  type: Object,
  default: () => ({})
})

// 定义组件事件
const emit = defineEmits([
  'update:loading',
  'handleTableChange',
  'handleShowServices',
  'handleShowProcesses',
  'handleShowNetworks',
  'clearFilter'
])
// 设备数据使用 shallowRef 优化大数组性能
const devices = shallowRef([])
const current = ref(1)
const pageSize = ref((props.pagination && props.pagination.pageSize) || 20)
const total = ref(0)
const innerLoading = ref(false)
const tableLoading = computed(() => props.loading || innerLoading.value)
const tablePagination = computed(() => ({
  current: current.value,
  pageSize: pageSize.value,
  total: total.value,
  showSizeChanger: true
}))

// 模态框相关
const showModal = ref(false)
const isEditing = ref(false)
const currentDevice = ref(null)

// 详情模态框相关
const showServicesModal = ref(false)
const showProcessesModal = ref(false)
const showNetworksModal = ref(false)
const servicesList = shallowRef([])
const processesList = shallowRef([])
const currentDeviceName = ref('')
const networksById = shallowRef({})
const networksPopoverOpen = shallowRef({})
const networksLoadingById = shallowRef({})

// 定时器管理 - 用于清理
const animationTimers = new Map()

// 网口表格列定义
const networkColumns = [
  {
    title: '接口名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: 'IP地址',
    dataIndex: 'ip_address',
    key: 'ip_address',
    width: 110
  },
  {
    title: 'MAC地址',
    dataIndex: 'mac_address',
    key: 'mac_address',
    customRender: ({ text }) => {
      return text || '无'
    }
  },
  {
    title: '网关',
    dataIndex: 'gateway',
    key: 'gateway',
    width: 110,
    customRender: ({ text }) => {
      return text || '无'
    }
  },
  {
    title: '子网掩码',
    dataIndex: 'netmask',
    key: 'netmask',
    width: 120,
    customRender: ({ text }) => {
      return text || '无'
    }
  },
  {
    title: '上传速率',
    dataIndex: 'upload_rate',
    key: 'upload_rate',
    width: 80,
    customRender: ({ text }) => formatNetworkRate(text)
  },
  {
    title: '下载速率',
    dataIndex: 'download_rate',
    key: 'download_rate',
    width: 80,
    customRender: ({ text }) => formatNetworkRate(text)
  }
]

// 表格列定义
const columns = [
  {
    title: '序号',
    dataIndex: 'index',
    align: 'center',
    key: 'index',
    width: 50,
    customRender: ({ text, index }) => {
      return index + 1
    }
  },
  {
    title: '基本信息',
    children: [
      {
        title: '类型',
        dataIndex: 'type',
        align: 'center',
        key: 'type',
        width: 60
      },
      {
        title: '设备名称',
        dataIndex: 'hostname',
        align: 'center',
        key: 'hostname'
      },
      {
        title: '设备别名',
        dataIndex: 'alias',
        align: 'center',
        key: 'alias',
        customRender: ({ text }) => {
          if (!text || text.length === 0) {
            return '无'
          }
          return text
        }
      },
      {
        title: '设备分组',
        dataIndex: 'grouping',
        align: 'center',
        key: 'grouping',
        customRender: ({ text }) => {
          if (!text || text.length === 0) {
            return '无'
          }
          return text
        }
      },
      {
        title: '设备地址',
        dataIndex: 'ips',
        align: 'center',
        key: 'ips',
        customRender: ({ text }) => {
          if (!text || !Array.isArray(text) || text.length === 0) {
            return '无'
          }
          // 如果只有一个IP地址，直接显示
          if (text.length === 1) {
            return text[0].split(':')[1]
          }
          // 如果有多个IP地址，显示第一个并提示还有更多，Tooltip中也一行显示一个IP
          return h('div', [
            h('span', text[0].split(':')[1]),
            h(
              Tooltip,
              {
                title: h(
                  'div',
                  {
                    style: {
                      textAlign: 'left'
                    }
                  },
                  text.map((ip) => h('div', ip))
                )
              },
              {
                default: () =>
                  h(
                    'span',
                    {
                      style: {
                        color: '#1890ff',
                        marginLeft: '5px',
                        cursor: 'pointer'
                      }
                    },
                    `(+${text.length - 1})`
                  )
              }
            )
          ])
        }
      }
    ]
  },
  {
    title: '系统信息',
    children: [
      {
        title: '系统',
        dataIndex: 'os_name',
        align: 'center',
        key: 'os_name',
        width: 70
      },
      {
        title: '版本',
        dataIndex: 'os_version',
        align: 'center',
        key: 'os_version'
      }
    ]
  },
  {
    title: '架构信息',
    children: [
      {
        title: '系统',
        dataIndex: 'os_architecture',
        align: 'center',
        key: 'os_architecture',
        width: 66,
        customRender: ({ text }) => {
          text = text.replace('bit', '位')
          return text || '-'
        }
      },
      {
        title: '硬件',
        dataIndex: 'machine_type',
        align: 'center',
        key: 'machine_type',
        width: 66
      }
    ]
  },
  {
    title: '使用率',
    children: [
      {
        title: 'CPU',
        dataIndex: 'cpu_usage',
        align: 'center',
        key: 'cpu_usage',
        width: 66,
        customRender: ({ record }) => {
          const displayValue = !record.online
            ? '0%'
            : record.cpu_info?.usage_percent != null
            ? `${record.cpu_info.usage_percent}%`
            : '未知'
          return createTextAnimationRenderer(
            displayValue,
            'cpu_usage',
            record.id
          )
        }
      },
      {
        title: '内存',
        dataIndex: 'memory_usage',
        align: 'center',
        key: 'memory_usage',
        width: 66,
        customRender: ({ record }) => {
          const displayValue = !record.online
            ? '0%'
            : record.memory_info?.percentage != null
            ? `${record.memory_info.percentage}%`
            : '未知'
          return createTextAnimationRenderer(
            displayValue,
            'memory_usage',
            record.id
          )
        }
      },
      {
        title: '磁盘',
        dataIndex: 'disk_usage',
        align: 'center',
        key: 'disk_usage',
        width: 66,
        customRender: ({ record }) => {
          const displayValue = !record.online
            ? '0%'
            : record.disk_info?.percentage != null
            ? `${record.disk_info.percentage}%`
            : '未知'
          return createTextAnimationRenderer(
            displayValue,
            'disk_usage',
            record.id
          )
        }
      }
    ]
  },
  {
    title: '数量信息',
    children: [
      {
        title: '服务',
        dataIndex: 'services_count',
        align: 'center',
        key: 'services_count',
        width: 70,
        customRender: ({ text, record }) => {
          return createClickableRenderer(
            record.services_count,
            record.online,
            () => handleShowServices(record),
            'services_count',
            record.id
          )
        }
      },
      {
        title: '进程',
        dataIndex: 'processes_count',
        align: 'center',
        key: 'processes_count',
        width: 70,
        customRender: ({ text, record }) => {
          return createClickableRenderer(
            record.processes_count,
            record.online,
            () => handleShowProcesses(record),
            'processes_count',
            record.id
          )
        }
      },
      {
        title: '网口',
        dataIndex: 'networks_count',
        align: 'center',
        key: 'networks_count',
        width: 70,
        customRender: ({ text, record }) => {
          const clickable = record.networks_count > 0 && record.online
          const link = h(
            'a',
            {
              style: {
                color: clickable ? '#1890ff' : '#00000040',
                cursor: clickable ? 'pointer' : 'not-allowed'
              }
            },
            clickable ? text : 0
          )
          return h(
            Popover,
            {
              open: !!networksPopoverOpen.value[record.id],
              placement: 'topRight',
              trigger: 'click',
              onOpenChange: async (open) => {
                if (!clickable) return
                networksPopoverOpen.value = {
                  ...networksPopoverOpen.value,
                  [record.id]: open
                }
                if (open) {
                  await handleShowNetworksPopover(record)
                }
              }
            },
            {
              default: () => link,
              content: () => {
                const rows = networksById.value[record.id] || []
                const loading = !!networksLoadingById.value[record.id]
                return h(
                  'div',
                  {
                    style: {
                      maxHeight: '360px',
                      overflow: 'auto',
                      width: '754px'
                    }
                  },
                  [
                    h(
                      'div',
                      { style: { fontWeight: 600, marginBottom: '8px' } },
                      `网口详情 - ${record.hostname || record.id}`
                    ),
                    h(
                      Spin,
                      { spinning: loading },
                      {
                        default: () =>
                          h(Table, {
                            dataSource: rows,
                            columns: networkColumns,
                            pagination: false,
                            bordered: true,
                            size: 'small',
                            rowKey: 'name',
                            scroll: { y: 320 },
                            locale: { emptyText: '暂无网口数据' }
                          })
                      }
                    )
                  ]
                )
              }
            }
          )
        }
      }
    ]
  },
  {
    title: '状态',
    dataIndex: 'online',
    align: 'center',
    key: 'online',
    width: 60
  },
  {
    title: '上报时间',
    dataIndex: 'timestamp',
    align: 'center',
    key: 'timestamp',
    width: 140,
    customRender: ({ text, record }) => {
      return createTextAnimationRenderer(text, 'timestamp', record.id)
    }
  },
  {
    title: '操作',
    dataIndex: 'action',
    align: 'center',
    key: 'action',
    width: 60
  }
]

// 格式化网络速率显示（优化性能）
const formatNetworkRate = (rate) => {
  if (rate == null) return '未知'
  if (rate < 1000) return `${rate} Kbps`
  if (rate < 1000000) return `${(rate / 1000).toFixed(2)} Mbps`
  return `${(rate / 1000000).toFixed(2)} Gbps`
}

// 创建动画处理器 - 提取公共逻辑
const createAnimationHandler = (key) => {
  return () => {
    if (changedTimestamps.value[key]) {
      changedTimestamps.value = { ...changedTimestamps.value, [key]: false }
    }
  }
}

// 创建可点击元素渲染器 - 复用逻辑
const createClickableRenderer = (
  count,
  online,
  handler,
  fieldKey,
  deviceId
) => {
  const displayValue = count > 0 && online ? count : 0
  const key = `${fieldKey}-${deviceId}`
  const isChanged = changedTimestamps.value[key] || false

  return h(
    'a',
    {
      onClick: () => count > 0 && online && handler(),
      class: isChanged ? 'timestamp-changed' : '',
      style: {
        color: count > 0 && online ? '#1890ff' : '#00000040',
        cursor: count > 0 && online ? 'pointer' : 'not-allowed'
      },
      onAnimationEnd: createAnimationHandler(key)
    },
    displayValue
  )
}

// 创建文本动画渲染器 - 复用逻辑
const createTextAnimationRenderer = (displayValue, fieldKey, deviceId) => {
  const key = `${fieldKey}-${deviceId}`
  const isChanged = changedTimestamps.value[key] || false

  return h(
    'span',
    {
      class: isChanged ? 'timestamp-changed' : '',
      onAnimationEnd: createAnimationHandler(key)
    },
    displayValue
  )
}

// 筛选状态
const filterType = ref('')
const filterIP = ref('')
const filterOS = ref('')
const filterStatus = ref('')

const debouncedFilterIP = ref('')
let ipDebounceTimer = null
watch(filterIP, (val) => {
  if (ipDebounceTimer) clearTimeout(ipDebounceTimer)
  ipDebounceTimer = setTimeout(() => {
    debouncedFilterIP.value = val
  }, 200)
})

const fetchDevices = async () => {
  try {
    innerLoading.value = true
    const response = await DeviceApi.getDevicesPage(
      pageSize.value,
      (current.value - 1) * pageSize.value
    )
    devices.value = response?.data || []
    total.value = response?.total || 0
  } catch (error) {
    console.error('获取设备列表失败:', error)
    message.error('获取设备列表失败')
  } finally {
    innerLoading.value = false
  }
}

const filteredDevices = computed(() => {
  const ft = filterType.value
  const fi = debouncedFilterIP.value
  const fo = filterOS.value
  const fs = filterStatus.value
  const out = []
  for (let i = 0; i < devices.value.length; i++) {
    const d = devices.value[i]
    if (ft) {
      if (ft === '__unset__') {
        if (d.type) continue
      } else {
        if (d.type !== ft) continue
      }
    }
    if (fi) {
      const ips = d.ips
      if (!ips || !Array.isArray(ips)) continue
      let matched = false
      for (let j = 0; j < ips.length; j++) {
        const ip = ips[j]
        const ipAddress = ip.split(': ')[1] || ip
        if (ipAddress && ipAddress.includes(fi)) {
          matched = true
          break
        }
      }
      if (!matched) continue
    }
    if (fo) {
      if (fo === '__unset__') {
        if (d.os_name && d.os_name !== 'N/A' && d.os_name !== '未知') continue
      } else {
        if (!d.os_name || !d.os_name.toLowerCase().includes(fo.toLowerCase()))
          continue
      }
    }
    if (fs) {
      if (fs === 'online') {
        if (d.online !== true) continue
      } else if (fs === 'offline') {
        if (d.online !== false) continue
      }
    }
    out.push(d)
  }
  return out
})

// 清除筛选
const clearFilter = () => {
  filterType.value = ''
  filterIP.value = ''
  filterOS.value = ''
  filterStatus.value = ''
  emit('clearFilter')
}

// 打开创建设备模态框
const openCreateModal = () => {
  isEditing.value = false
  currentDevice.value = null
  showModal.value = true
}

// 打开编辑设备模态框
const openEditModal = (device) => {
  isEditing.value = true
  currentDevice.value = { ...device }
  showModal.value = true
}
const processVisible = ref(false)
const openProcessModal = () => {
  processVisible.value = true
}

// 删除设备
const deleteDevice = async (id) => {
  try {
    const response = await DeviceApi.deleteDevice({ id })
    if (response.status === 'success') {
      message.success('设备删除成功')
      fetchDevices()
    } else {
      message.error('设备删除失败: ' + response.message)
    }
  } catch (error) {
    console.error('删除设备失败:', error)
    message.error('删除设备失败: ' + error.message)
  }
}

// 处理表格变化事件
const handleTableChange = (pag, filters, sorter) => {
  if (pag) {
    current.value = pag.current || 1
    pageSize.value = pag.pageSize || pageSize.value
    fetchDevices()
  }
  emit('handleTableChange', pag, filters, sorter)
}

// 通用排序函数 - 按PID排序
const sortByPid = (list) => {
  return [...list].sort((a, b) => {
    if (a.pid == null && b.pid == null) return 0
    if (a.pid == null) return 1
    if (b.pid == null) return -1
    return a.pid - b.pid
  })
}

// 显示服务详情
const handleShowServices = async (record) => {
  try {
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response?.data?.services) {
      servicesList.value = sortByPid(response.data.services)
      currentDeviceName.value = record.hostname || record.id
      showServicesModal.value = true
    }
  } catch (error) {
    console.error('获取服务详情失败:', error)
    message.error('获取服务详情失败')
  }
}

// 显示进程详情
const handleShowProcesses = async (record) => {
  try {
    const response = await DeviceApi.getDeviceInfo(record.id)
    if (response?.data?.processes) {
      processesList.value = sortByPid(response.data.processes)
      currentDeviceName.value = record.hostname || record.id
      showProcessesModal.value = true
    }
  } catch (error) {
    console.error('获取进程详情失败:', error)
    message.error('获取进程详情失败')
  }
}

// 关闭服务详情模态框
const closeServicesModal = () => {
  showServicesModal.value = false
}

// 关闭进程详情模态框
const closeProcessesModal = () => {
  showProcessesModal.value = false
}

// 显示网口详情
const handleShowNetworksPopover = async (record) => {
  try {
    networksLoadingById.value = {
      ...networksLoadingById.value,
      [record.id]: true
    }
    const response = await DeviceApi.getDeviceInfo(record.id)
    networksById.value = {
      ...networksById.value,
      [record.id]: response?.data?.networks || []
    }
    currentDeviceName.value = record.hostname || record.id
  } catch (error) {
    console.error('获取网口详情失败:', error)
    message.error('获取网口详情失败')
  } finally {
    networksLoadingById.value = {
      ...networksLoadingById.value,
      [record.id]: false
    }
  }
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
}

// 保存设备（创建或更新）
const saveDevice = async (deviceData) => {
  try {
    if (isEditing.value) {
      // 更新设备
      const response = await DeviceApi.updateDevice(deviceData)
      if (response.status === 'success') {
        message.success('设备更新成功')
        closeModal()
        fetchDevices()
      } else {
        message.error('设备更新失败: ' + response.message)
      }
    } else {
      // 创建设备
      const response = await DeviceApi.createDevice(deviceData)
      if (response.status === 'success') {
        message.success('设备创建成功')
        closeModal()
        fetchDevices()
      } else {
        message.error('设备创建失败: ' + response.message)
      }
    }
  } catch (error) {
    console.error('保存设备失败:', error)
    message.error('保存设备失败: ' + error.message)
  }
}

// 清理所有动画定时器
const clearAllAnimationTimers = () => {
  animationTimers.forEach((timerId) => clearTimeout(timerId))
  animationTimers.clear()
}

// 设置动画定时器
const setAnimationTimer = (changeKey) => {
  // 清除旧的定时器
  if (animationTimers.has(changeKey)) {
    clearTimeout(animationTimers.get(changeKey))
  }

  // 设置新的定时器
  const timerId = setTimeout(() => {
    changedTimestamps.value = { ...changedTimestamps.value, [changeKey]: false }
    animationTimers.delete(changeKey)
  }, ANIMATION_DURATION)

  animationTimers.set(changeKey, timerId)
}

// 获取字段值的辅助函数
const getFieldValue = (device, key) => {
  switch (key) {
    case 'timestamp':
      return device.timestamp
    case 'cpu_usage':
      return device.cpu_info?.usage_percent
    case 'memory_usage':
      return device.memory_info?.percentage
    case 'disk_usage':
      return device.disk_info?.percentage
    case 'services_count':
      return device.services_count
    case 'processes_count':
      return device.processes_count
    default:
      return undefined
  }
}

// 处理设备信息更新
const handleDeviceInfoUpdate = async (deviceInfo) => {
  const index = devices.value.findIndex((dev) => dev.id === deviceInfo.id)
  if (index === -1) return

  const oldDevice = devices.value[index]
  const newChangedTimestamps = { ...changedTimestamps.value }

  // 检查字段变化
  CHANGE_KEYS.forEach((key) => {
    const oldValue = getFieldValue(oldDevice, key)
    const newValue = getFieldValue(deviceInfo, key)

    // 严格检查值的变化
    if (oldValue !== newValue && newValue != null) {
      const changeKey = `${key}-${deviceInfo.id}`

      // 避免重复触发动画
      if (!newChangedTimestamps[changeKey]) {
        newChangedTimestamps[changeKey] = true
        setAnimationTimer(changeKey)
      }
    }
  })

  // 更新设备信息（使用浅拷贝优化性能）
  const updatedDevices = [...devices.value]
  updatedDevices[index] = { ...oldDevice, ...deviceInfo }
  devices.value = updatedDevices
  changedTimestamps.value = newChangedTimestamps

  // 若该设备的网口 Popover 处于打开状态，则同步更新其内容
  if (networksPopoverOpen.value[deviceInfo.id]) {
    try {
      networksLoadingById.value = {
        ...networksLoadingById.value,
        [deviceInfo.id]: true
      }
      const response = await DeviceApi.getDeviceInfo(deviceInfo.id)
      const rows = response?.data?.networks
      if (Array.isArray(rows)) {
        const prev = networksById.value[deviceInfo.id] || []
        const sameLen = prev.length === rows.length
        const same =
          sameLen &&
          prev.every((p, i) => {
            const r = rows[i]
            return (
              p.name === r.name &&
              p.ip_address === r.ip_address &&
              p.mac_address === r.mac_address &&
              p.gateway === r.gateway &&
              p.netmask === r.netmask &&
              p.upload_rate === r.upload_rate &&
              p.download_rate === r.download_rate
            )
          })
        if (!same) {
          networksById.value = {
            ...networksById.value,
            [deviceInfo.id]: rows
          }
        }
      }
    } catch (error) {
    } finally {
      networksLoadingById.value = {
        ...networksLoadingById.value,
        [deviceInfo.id]: false
      }
    }
  }
}

// 处理设备状态更新
const handleDeviceStatusUpdate = (data) => {
  const index = devices.value.findIndex(
    (dev) => dev.client_id === data.client_id
  )
  if (index === -1) return

  const updatedDevices = [...devices.value]
  updatedDevices[index] = {
    ...updatedDevices[index],
    online: data.status === 'online'
  }
  devices.value = updatedDevices
}

// 页面挂载时订阅设备信息和状态更新
onMounted(() => {
  fetchDevices()
  PubSub.subscribe(wsCode.DEVICE_INFO, handleDeviceInfoUpdate)
  PubSub.subscribe(wsCode.DEVICE_STATUS, handleDeviceStatusUpdate)
})

// 页面卸载时取消订阅并清理资源
onUnmounted(() => {
  PubSub.unsubscribe(wsCode.DEVICE_INFO)
  PubSub.unsubscribe(wsCode.DEVICE_STATUS)
  clearAllAnimationTimers() // 清理所有定时器
  changedTimestamps.value = {} // 清空变化标记
})
</script>

<style lang="less">
// 时间戳变更时的过渡色提示样式
.timestamp-changed {
  animation: highlightChange 3s ease-in-out;
}

@keyframes highlightChange {
  0% {
    background-color: rgba(255, 193, 7, 0.5); // 淡黄色背景
    color: #212529;
  }
  50% {
    background-color: rgba(40, 167, 69, 0.3); // 淡绿色背景
    color: #212529;
  }
  100% {
    background-color: transparent;
    color: inherit;
  }
}

// 设备图标样式
.device-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;

  :deep(svg) {
    width: 100%;
    height: 100%;
    display: block;
  }
}
</style>
