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
            <div class="text-3xl">
              <svg
                t="1761545146202"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="2818"
                width="33"
                height="33"
              >
                <path
                  d="M76.8 358.4h76.8v307.2H76.8zM870.4 358.4h76.8v307.2h-76.8z"
                  fill="#101010"
                  p-id="2819"
                ></path>
                <path
                  d="M102.4 384v256h51.2V384zM870.4 384v256h51.2V384z"
                  fill="#00FFFF"
                  p-id="2820"
                ></path>
                <path
                  d="M153.6 153.6h716.8v716.8H153.6z"
                  fill="#101010"
                  p-id="2821"
                ></path>
                <path
                  d="M179.2 179.2v665.6h665.6V179.2z"
                  fill="#304FFE"
                  p-id="2822"
                ></path>
                <path
                  d="M281.6 307.2h512v486.4H281.6z"
                  fill="#101010"
                  p-id="2823"
                ></path>
                <path
                  d="M256 281.6h512v486.4H256z"
                  fill="#101010"
                  p-id="2824"
                ></path>
                <path
                  d="M281.6 307.2h460.8v435.2H281.6z"
                  fill="#00FFFF"
                  p-id="2825"
                ></path>
                <path
                  d="M453.12 549.0176c-1.0752 6.3744-3.008 12.032-5.7728 16.9728a43.2 43.2 0 0 1-10.304 12.4672c-4.096 3.3536-8.8064 5.9264-14.1056 7.68A53.9776 53.9776 0 0 1 405.76 588.8c-13.7344 0-25.3056-4.608-34.7008-13.7856a35.9424 35.9424 0 0 1-10.496-18.9184C359.1168 549.0176 358.4 538.5856 358.4 524.8c0-13.7856 0.7168-24.2176 2.176-31.296a35.9424 35.9424 0 0 1 10.4832-18.9184C380.4544 465.408 392.0256 460.8 405.76 460.8c12.416 0 22.8736 3.4176 31.36 10.2528 8.512 6.8352 13.8368 16.6784 16 29.5296h-25.472c-1.3312-5.4272-3.7504-9.7536-7.2448-12.992-3.4944-3.2512-8.32-4.864-14.464-4.864-6.9888 0-12.352 2.176-16.0768 6.528-1.3312 1.4208-2.4192 2.9312-3.264 4.5184a20.5056 20.5056 0 0 0-1.8944 6.1824 84.8 84.8 0 0 0-0.896 9.728A342.528 342.528 0 0 0 383.5136 524.8c0 6.1312 0.0896 11.1616 0.2688 15.104 0.1792 3.968 0.4864 7.2064 0.9088 9.728 0.4224 2.5472 1.0496 4.608 1.8944 6.1952 0.8448 1.5872 1.92 3.0976 3.264 4.5056 3.7248 4.352 9.088 6.5408 16.0896 6.5408 6.144 0 10.9568-1.6128 14.464-4.864 3.4816-3.2384 5.888-7.5648 7.2192-12.992h25.4976z m106.3296-47.9104c0 5.312-0.96 10.3424-2.8928 15.1168-1.92 4.7744-4.736 8.96-8.3968 12.544-3.6736 3.6096-8.1408 6.4384-13.376 8.4992-5.248 2.048-11.1872 3.0848-17.8176 3.0848h-24.768v47.3856H467.072v-125.8752h49.8944c6.6304 0 12.5696 1.024 17.8176 3.0976 5.248 2.048 9.7024 4.8896 13.376 8.4864 3.6736 3.584 6.4768 7.7696 8.3968 12.544 1.9328 4.7744 2.8928 9.8176 2.8928 15.1168z m-25.1264 0c0-5.184-1.664-9.3696-4.9664-12.544-3.328-3.2-7.872-4.7744-13.6448-4.7744h-23.5136v34.4704h23.5136c5.7728 0 10.3296-1.5616 13.6448-4.6848s4.9664-7.2832 4.9664-12.4672zM665.6 544.6016c0 6.72-1.2416 12.7872-3.712 18.2144a41.472 41.472 0 0 1-10.112 13.8752c-4.288 3.84-9.28 6.8096-15.0144 8.9216-5.7216 2.1248-11.904 3.1872-18.5216 3.1872-6.6304 0-12.8-1.0624-18.5344-3.1872a46.4256 46.4256 0 0 1-15.0016-8.9216 41.472 41.472 0 0 1-10.1248-13.8752 43.4176 43.4176 0 0 1-3.712-18.2144v-82.7392h25.1264v81.856c0 7.296 1.9968 12.992 5.9648 17.0624 3.9808 4.0576 9.408 6.0928 16.2816 6.0928 6.8608 0 12.3136-2.0352 16.3584-6.0928 4.032-4.0704 6.0544-9.7536 6.0544-17.0624v-81.856H665.6v82.7392z"
                  fill="#101010"
                  p-id="2826"
                ></path>
                <path
                  d="M486.4 102.4h-25.6V51.2h25.6v51.2z m76.8 0h-25.6V51.2h25.6v51.2z m76.8 0h-25.6V51.2h25.6v51.2zM409.6 102.4h-25.6V51.2h25.6v51.2z m76.8 870.4h-25.6v-51.2h25.6v51.2z m76.8 0h-25.6v-51.2h25.6v51.2z m76.8 0h-25.6v-51.2h25.6v51.2z m-230.4 0h-25.6v-51.2h25.6v51.2z"
                  fill="#101010"
                  p-id="2827"
                ></path>
                <path
                  d="M256 230.4h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m153.6 0h102.4v25.6h-102.4v-25.6z"
                  fill="#00FFFF"
                  p-id="2828"
                ></path>
                <path
                  d="M768 537.6v-25.6h51.2v25.6h-51.2z m0 76.8v-25.6h51.2v25.6h-51.2z m0-153.6v-25.6h51.2v25.6h-51.2zM204.8 537.6v-25.6h51.2v25.6h-51.2z m0 76.8v-25.6h51.2v25.6h-51.2z m0-153.6v-25.6h51.2v25.6h-51.2z"
                  fill="#101010"
                  p-id="2829"
                ></path>
                <path
                  d="M947.2 102.4m-51.2 0a51.2 51.2 0 1 0 102.4 0 51.2 51.2 0 1 0-102.4 0Z"
                  fill="#101010"
                  p-id="2830"
                ></path>
                <path
                  d="M947.2 102.4m-25.6 0a25.6 25.6 0 1 0 51.2 0 25.6 25.6 0 1 0-51.2 0Z"
                  fill="#FFDD00"
                  p-id="2831"
                ></path>
                <path
                  d="M92.16 934.4L115.2 957.44 99.84 972.8 76.8 949.76 53.76 972.8 38.4 957.44 61.44 934.4 38.4 911.36 53.76 896 76.8 919.04 99.84 896 115.2 911.36zM588.8 665.6h102.4v76.8h-102.4z"
                  fill="#101010"
                  p-id="2832"
                ></path>
                <path
                  d="M614.4 691.2h51.2v51.2h-51.2z"
                  fill="#FFDD00"
                  p-id="2833"
                ></path>
                <path
                  d="M332.8 307.2h102.4v76.8h-102.4z"
                  fill="#101010"
                  p-id="2834"
                ></path>
                <path
                  d="M358.4 307.2h51.2v51.2h-51.2z"
                  fill="#FFDD00"
                  p-id="2835"
                ></path>
                <path
                  d="M89.6 89.6V51.2h25.6v38.4h38.4v25.6H115.2v38.4H89.6V115.2H51.2V89.6h38.4zM908.8 908.8v-38.4h25.6v38.4h38.4v25.6h-38.4v38.4h-25.6v-38.4h-38.4v-25.6h38.4z"
                  fill="#304FFE"
                  p-id="2836"
                ></path>
              </svg>
            </div>
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
            <div class="text-3xl">
              <svg
                t="1761545343524"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="7272"
                width="33"
                height="33"
              >
                <path
                  d="M179.2 153.6h665.6v76.8H179.2z"
                  fill="#101010"
                  p-id="7273"
                ></path>
                <path
                  d="M204.8 179.2h614.4v51.2H204.8z"
                  fill="#304FFE"
                  p-id="7274"
                ></path>
                <path
                  d="M128 460.8h25.6v-25.6h-25.6V230.4h768v204.8h-25.6v25.6h25.6v76.8H128v-76.8z"
                  fill="#101010"
                  p-id="7275"
                ></path>
                <path
                  d="M870.4 409.6h-25.6v76.8h25.6v25.6H153.6v-25.6h25.6v-76.8h-25.6V256h716.8v153.6z"
                  fill="#00FFFF"
                  p-id="7276"
                ></path>
                <path
                  d="M896 256h25.6v25.6h-25.6v-25.6z m0 51.2h25.6v25.6h-25.6v-25.6zM102.4 256h25.6v25.6H102.4v-25.6z m0 51.2h25.6v25.6H102.4v-25.6zM179.2 307.2h665.6v76.8H179.2z"
                  fill="#101010"
                  p-id="7277"
                ></path>
                <path
                  d="M204.8 332.8h614.4v51.2H204.8z"
                  fill="#FFDD00"
                  p-id="7278"
                ></path>
                <path
                  d="M128 614.4h25.6v-25.6h-25.6V384h768v204.8h-25.6v25.6h25.6v76.8H128v-76.8z"
                  fill="#101010"
                  p-id="7279"
                ></path>
                <path
                  d="M870.4 563.2h-25.6v76.8h25.6v25.6H153.6v-25.6h25.6v-76.8h-25.6V409.6h716.8v153.6z"
                  fill="#00FFFF"
                  p-id="7280"
                ></path>
                <path
                  d="M896 409.6h25.6v25.6h-25.6v-25.6z m0 51.2h25.6v25.6h-25.6v-25.6zM102.4 409.6h25.6v25.6H102.4v-25.6z m0 51.2h25.6v25.6H102.4v-25.6z"
                  fill="#101010"
                  p-id="7281"
                ></path>
                <path
                  d="M179.2 460.8h665.6v76.8H179.2z"
                  fill="#101010"
                  p-id="7282"
                ></path>
                <path
                  d="M204.8 486.4h614.4v51.2H204.8z"
                  fill="#304FFE"
                  p-id="7283"
                ></path>
                <path
                  d="M128 768h25.6v-25.6h-25.6V537.6h768v204.8h-25.6v25.6h25.6v76.8H128v-76.8z"
                  fill="#101010"
                  p-id="7284"
                ></path>
                <path
                  d="M870.4 716.8h-25.6v76.8h25.6v25.6H153.6v-25.6h25.6v-76.8h-25.6V563.2h716.8v153.6z"
                  fill="#00FFFF"
                  p-id="7285"
                ></path>
                <path
                  d="M896 563.2h25.6v25.6h-25.6v-25.6z m0 51.2h25.6v25.6h-25.6v-25.6zM102.4 563.2h25.6v25.6H102.4v-25.6z m0 51.2h25.6v25.6H102.4v-25.6zM192 844.8h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m51.2 0h25.6v25.6h-25.6v-25.6z m102.4 0h25.6v25.6h-25.6v-25.6z m-51.2 0h25.6v25.6h-25.6v-25.6z m102.4 0h25.6v25.6h-25.6v-25.6zM332.8 614.4h51.2v51.2h-51.2v-51.2z m-102.4 0h51.2v51.2h-51.2v-51.2z m-102.4 0h51.2v51.2h-51.2v-51.2z m307.2 0h51.2v51.2h-51.2v-51.2z m102.4 0h51.2v51.2h-51.2v-51.2z m102.4 0h51.2v51.2h-51.2v-51.2z m102.4 0h51.2v51.2h-51.2v-51.2z m102.4 0h51.2v51.2h-51.2v-51.2zM204.8 742.4h614.4v25.6H204.8z"
                  fill="#101010"
                  p-id="7286"
                ></path>
                <path
                  d="M921.6 102.4m-51.2 0a51.2 51.2 0 1 0 102.4 0 51.2 51.2 0 1 0-102.4 0Z"
                  fill="#101010"
                  p-id="7287"
                ></path>
                <path
                  d="M102.4 921.6m-51.2 0a51.2 51.2 0 1 0 102.4 0 51.2 51.2 0 1 0-102.4 0Z"
                  fill="#101010"
                  p-id="7288"
                ></path>
                <path
                  d="M921.6 102.4m-25.6 0a25.6 25.6 0 1 0 51.2 0 25.6 25.6 0 1 0-51.2 0Z"
                  fill="#FFDD00"
                  p-id="7289"
                ></path>
                <path
                  d="M102.4 921.6m-25.6 0a25.6 25.6 0 1 0 51.2 0 25.6 25.6 0 1 0-51.2 0Z"
                  fill="#FFDD00"
                  p-id="7290"
                ></path>
                <path
                  d="M942.08 921.6l30.72 30.72-20.48 20.48-30.72-30.72-30.72 30.72-20.48-20.48 30.72-30.72-30.72-30.72 20.48-20.48 30.72 30.72 30.72-30.72 20.48 20.48z"
                  fill="#304FFE"
                  p-id="7291"
                ></path>
                <path
                  d="M89.6 89.6V51.2h25.6v38.4h38.4v25.6H115.2v38.4H89.6V115.2H51.2V89.6h38.4z"
                  fill="#101010"
                  p-id="7292"
                ></path>
              </svg>
            </div>
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
            <div class="text-3xl">
              <svg
                t="1761545442543"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="13743"
                width="36"
                height="36"
              >
                <path
                  d="M749.145152 95.397443H274.906043c-31.19881 0-56.566593 25.367783-56.566593 56.566593v633.423585c0 31.201881 25.367783 56.566593 56.566593 56.566592h33.101188v62.334139c0 13.564433 10.987313 24.551746 24.482122 24.551746 13.567504 0 24.554818-10.987313 24.554818-24.551746v-62.334139h41.304558v62.334139c0 13.564433 10.987313 24.551746 24.554818 24.551746 13.494809 0 24.482122-10.987313 24.482122-24.551746v-62.334139h41.373158v62.334139c0 13.564433 10.921785 24.551746 24.555842 24.551746 13.42928 0 24.416593-10.987313 24.416593-24.551746v-62.334139h41.373158v62.334139c0 13.564433 10.987313 24.551746 24.486218 24.551746 13.564433 0 24.551746-10.987313 24.551746-24.551746v-62.334139h41.373158v62.334139c0 13.564433 10.987313 24.551746 24.486218 24.551746 13.564433 0 24.551746-10.987313 24.551746-24.551746v-62.334139h30.590622c31.19881 0 56.566593-25.364711 56.566592-56.566592V151.964036c0.001024-31.19881-25.366759-56.566593-56.565568-56.566593z"
                  fill="#456a63"
                  p-id="13744"
                ></path>
                <path
                  d="M578.834115 792.916249H451.526261v-61.178172a16.310493 16.310493 0 0 0-16.346329-16.345305h-60.841314c28.62169-37.709697 121.884333-160.6773 141.483546-186.451565 7.191771 9.494489 123.512311 162.781384 141.487641 186.451565h-62.129361a16.310493 16.310493 0 0 0-16.346329 16.345305v61.178172z"
                  fill="#FFFFFF"
                  p-id="13745"
                ></path>
                <path
                  d="M528.779433 491.973827c-3.052202-4.069944-7.869583-6.442286-12.956245-6.442287-5.083591 0-9.900971 2.371318-13.022798 6.442287l-51.680611 68.095541c-77.934055-26.992689-131.718751-100.312093-131.718752-182.586398 0-106.281344 86.410802-192.692146 192.692147-192.692147 106.149263 0 192.625594 86.410802 192.625593 192.692147 0 79.08695-51.478906 151.387589-125.954277 180.350233l-49.985057-65.859376z"
                  fill="#F4CE73"
                  p-id="13746"
                ></path>
                <path
                  d="M756.739309 785.387621c0 4.139568-3.458685 7.528629-7.594157 7.528628H611.457149V748.084407h78.745996c6.240581 0 11.869903-3.528309 14.650775-9.088007a16.265442 16.265442 0 0 0 1.694531-7.258323c0-3.528309-1.152895-6.986993-3.323532-9.899947L599.115235 584.690739c82.205705-35.945542 138.226567-117.810293 138.226567-207.207769 0-124.255651-101.058505-225.383781-225.248628-225.383781-124.325276 0-225.383781 101.12813-225.383781 225.383781 0 92.651383 58.261123 175.467324 143.925512 209.648711l-102.2114 134.705425c-3.733086 4.948438-4.341274 11.595501-1.629002 17.158271 2.781896 5.559697 8.476747 9.088006 14.650775 9.088006h77.388325v44.831842H274.906043c-4.135473 0-7.528629-3.38906-7.528629-7.528628V151.964036c0-4.135473 3.393156-7.598253 7.528629-7.598253h474.239109c4.135473 0 7.594157 3.461756 7.594157 7.598253v633.423585z"
                  fill="#456a63"
                  p-id="13747"
                ></path>
                <path
                  d="M452.137521 373.076167c0 33.032588 26.857536 59.890124 59.955653 59.890125 32.962964 0 59.753948-26.857536 59.753947-59.890125s-26.792007-59.890124-59.753947-59.890124c-33.098117 0-59.955653 26.85856-59.955653 59.890124z"
                  fill="#27323A"
                  p-id="13748"
                ></path>
                <path
                  d="M484.829155 373.076167c0-14.991729 12.206761-27.19849 27.264019-27.198489 14.922105 0 27.131937 12.206761 27.131937 27.198489 0 14.987633-12.209832 27.19849-27.131937 27.19849-15.057258 0-27.264018-12.209832-27.264019-27.19849z"
                  fill="#FFFFFF"
                  p-id="13749"
                ></path>
              </svg>
            </div>
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
            <div class="text-3xl">
              <svg
                t="1761545537161"
                class="icon"
                viewBox="0 0 1024 1024"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                p-id="20467"
                width="32"
                height="32"
              >
                <path
                  d="M1024.986006 972.996729a49.304463 49.304463 0 0 1-49.221598 49.387328l-924.761137 1.61586a49.304463 49.304463 0 0 1-49.387328-49.221598L0.000083 51.003271A49.304463 49.304463 0 0 1 49.221681 1.615943L973.991105 0.000083a49.304463 49.304463 0 0 1 49.387327 49.221598l1.607574 923.775048zM173.576652 118.960565a53.613424 53.613424 0 1 0-107.226849 0 53.613424 53.613424 0 0 0 107.226849 0z m784.81104 0.16573a53.53056 53.53056 0 1 0-107.061119 0 53.53056 53.53056 0 0 0 107.061119 0z m-671.576504 145.178855a37.454819 37.454819 0 0 0-37.322236-37.579116l-69.440571-0.248593a37.454819 37.454819 0 0 0-37.587403 37.330521l-0.082864 24.527935a37.454819 37.454819 0 0 0 37.322235 37.587402l69.440572 0.240308a37.454819 37.454819 0 0 0 37.587402-37.322236l0.082865-24.527934z m595.631058-0.828646a37.12336 37.12336 0 0 0-37.255943-36.990777l-70.103489 0.248594a37.12336 37.12336 0 0 0-36.990777 37.247657l0.082865 25.190852a37.12336 37.12336 0 0 0 37.255943 36.990777l70.103489-0.248594a37.12336 37.12336 0 0 0 36.999063-37.247657l-0.091151-25.190852z m-500.54388-3.56318c-58.005251 0.165729-62.314212 54.359206-54.939259 97.283092 0.720922 4.159805-0.165729 8.427334-2.419647 11.60105-2.253918 3.190289-5.626509 4.955306-9.181403 4.806149-42.592427-1.657293-88.748033-1.07724-88.748033 55.685041-0.049719 120.650921-0.024859 241.334988 0.082865 362.035628 0 36.211849 22.539183 50.381703 57.508062 50.464568 153.415601 0.165729 306.822916 0.14087 460.230231-0.082864 42.095239-0.082865 54.027748-22.787777 53.944883-62.97713 0-117.551784-0.024859-235.111854-0.082864-352.671923 0-54.690665-48.807275-52.121861-88.49944-52.784778a9.197975 9.197975 0 0 1-9.032246-8.037871c-8.2036-62.894265 13.424072-105.403827-74.329585-105.486691-81.538809-0.049719-163.044473 0-244.533564 0.165729z m-208.155985 644.18974a53.696289 53.696289 0 1 0-107.392578 0 53.696289 53.696289 0 0 0 107.392578 0z m784.893905-0.082864a53.613424 53.613424 0 1 0-107.226849 0 53.613424 53.613424 0 0 0 107.226849 0z"
                  fill="#456a63"
                  p-id="20468"
                ></path>
                <path
                  d="M119.963228 118.968852m-53.613425 0a53.613424 53.613424 0 1 0 107.226849 0 53.613424 53.613424 0 1 0-107.226849 0Z"
                  fill="#6580A6"
                  p-id="20469"
                ></path>
                <path
                  d="M904.857132 119.134581m-53.530559 0a53.53056 53.53056 0 1 0 107.061119 0 53.53056 53.53056 0 1 0-107.061119 0Z"
                  fill="#6580A6"
                  p-id="20470"
                ></path>
                <path
                  d="M142.593537 226.358389m37.45459 0.130741l69.440149 0.242393q37.454591 0.130742 37.323849 37.585333l-0.085619 24.527785q-0.130742 37.454591-37.585332 37.323849l-69.440149-0.242393q-37.454591-0.130742-37.323849-37.585332l0.085619-24.527786q0.130742-37.454591 37.585332-37.323849Z"
                  fill="#E2F0FA"
                  p-id="20471"
                ></path>
                <path
                  d="M737.960358 226.862265m37.123134-0.129585l70.103062-0.244707q37.123134-0.129585 37.252719 36.99355l0.087932 25.190698q0.129585 37.123134-36.993549 37.252719l-70.103062 0.244707q-37.123134 0.129585-37.252719-36.99355l-0.087932-25.190698q-0.129585-37.123134 36.993549-37.252719Z"
                  fill="#E2F0FA"
                  p-id="20472"
                ></path>
                <path
                  d="M326.959107 357.204702c-7.374953-42.923885-3.065992-97.117362 54.939259-97.283091 81.489091-0.165729 162.994754-0.215448 244.533564-0.16573 87.753658 0.082865 66.125986 42.592427 74.329585 105.486692 0.580053 4.557555 4.441545 7.996438 9.032246 8.03787 39.692164 0.662917 88.499439-1.905887 88.49944 52.784778 0.058005 117.56007 0.082865 235.12014 0.082864 352.671924 0.082865 40.189352-11.849644 62.894265-53.944883 62.977129-153.407315 0.223735-306.81463 0.248594-460.230231 0.082865-34.96888-0.082865-57.508063-14.252719-57.508062-50.464568-0.107724-120.70064-0.132583-241.384707-0.082865-362.035629 0-56.762281 46.155607-57.342333 88.748033-55.68504 3.56318 0.149156 6.927484-1.615861 9.181403-4.80615 2.253918-3.173716 3.148856-7.441245 2.419647-11.60105z m108.967007 37.040496c-31.654294 0.248594-43.669667 26.350957-39.112112 54.193477 0.604912 3.521747-0.497188 7.126359-2.983127 9.711736a11.48504 11.48504 0 0 1-9.612299 3.463742c-38.532059-4.557555-47.812899 22.870642-47.812899 56.182229v181.30784c0 33.311587 6.96063 53.281966 43.503938 53.447695 89.278367 0.555193 178.523588 0.886652 267.735663 0.994376 17.956768 0.058005 29.499813-5.88339 34.637422-17.815898a76.351483 76.351483 0 0 0 6.214848-29.914137c0.223735-64.576417 0.198875-127.280093-0.082865-188.102741-0.165729-33.643045-6.877765-57.342333-45.32696-55.187853-6.42201 0.331459-12.015373-4.574128-12.761155-11.186726l-3.56318-34.305963c-1.541282-14.526172-12.181103-21.925985-31.902888-22.207724-53.083091-0.662917-106.066744-0.853506-158.934386-0.580053z"
                  fill="#E2F0FA"
                  p-id="20473"
                ></path>
                <path
                  d="M120.046092 904.111351m-53.696289 0a53.696289 53.696289 0 1 0 107.392578 0 53.696289 53.696289 0 1 0-107.392578 0Z"
                  fill="#6580A6"
                  p-id="20474"
                ></path>
                <path
                  d="M905.022862 904.028486m-53.613425 0a53.613424 53.613424 0 1 0 107.226849 0 53.613424 53.613424 0 1 0-107.226849 0Z"
                  fill="#6580A6"
                  p-id="20475"
                ></path>
                <path
                  d="M396.814002 448.438675c-4.557555-27.84252 7.457818-53.944883 39.112112-54.193477 52.867643-0.273453 105.851296-0.082865 158.934386 0.580053 19.721785 0.28174 30.361605 7.681552 31.902888 22.207724l3.56318 34.305963c0.745782 6.612599 6.339145 11.518185 12.761155 11.186726 38.449195-2.154481 45.161231 21.544807 45.32696 55.187853 0.28174 60.822648 0.306599 123.526324 0.082865 188.102741a76.351483 76.351483 0 0 1-6.214848 29.914137c-5.137608 11.932509-16.680653 17.873904-34.637422 17.815898a54139.150906 54139.150906 0 0 1-267.735663-0.994376c-36.543308-0.165729-43.503938-20.136108-43.503938-53.447695v-181.30784c0-33.311587 9.28084-60.739784 47.812899-56.182229 3.579753 0.414323 7.134646-0.870079 9.612299-3.463742 2.485939-2.585377 3.588039-6.189989 2.983127-9.711736z m40.57053 123.816351a13.755531 13.755531 0 0 0-13.896401-13.614661l-2.154481 0.024859a13.755531 13.755531 0 0 0-13.614661 13.896401l0.894938 85.516312a13.755531 13.755531 0 0 0 13.904688 13.606375l2.15448-0.016573a13.755531 13.755531 0 0 0 13.606375-13.904688l-0.894938-85.516312z m178.614739 0.041432a13.92126 13.92126 0 0 0-13.946119-13.896401h-0.994376a13.92126 13.92126 0 0 0-13.896401 13.94612l0.149156 85.682041a13.92126 13.92126 0 0 0 13.94612 13.896401h0.994376a13.92126 13.92126 0 0 0 13.8964-13.946119l-0.149156-85.682042z m-87.579642 0.389464a12.761155 12.761155 0 0 0-12.802587-12.719723l-5.137608 0.016573a12.761155 12.761155 0 0 0-12.719723 12.810874l0.298313 86.179229a12.761155 12.761155 0 0 0 12.810874 12.711437l5.137608-0.016573a12.761155 12.761155 0 0 0 12.711436-12.802588l-0.298313-86.179229z"
                  fill="#C8D9E5"
                  p-id="20476"
                ></path>
                <path
                  d="M407.575472 558.807075m13.754777-0.144045l2.154363-0.022561q13.754777-0.144045 13.898821 13.610732l0.895509 85.511623q0.144045 13.754777-13.610732 13.898822l-2.154363 0.022561q-13.754777 0.144045-13.898821-13.610732l-0.895509-85.511623q-0.144045-13.754777 13.610732-13.898822Z"
                  fill="#E2F0FA"
                  p-id="20477"
                ></path>
                <path
                  d="M587.137906 558.425309m13.921239-0.024298l0.994375-0.001735q13.921239-0.024297 13.945536 13.896942l0.149543 85.681911q0.024297 13.921239-13.896942 13.945536l-0.994374 0.001735q-13.921239 0.024297-13.945536-13.896941l-0.149543-85.681911q-0.024297-13.921239 13.896941-13.945537Z"
                  fill="#E2F0FA"
                  p-id="20478"
                ></path>
                <path
                  d="M497.714005 560.028337m12.761078-0.044544l5.137576-0.017934q12.761077-0.044545 12.805622 12.716533l0.300822 86.178704q0.044545 12.761077-12.716533 12.805622l-5.137576 0.017934q-12.761077 0.044545-12.805622-12.716533l-0.300822-86.178704q-0.044545-12.761077 12.716533-12.805622Z"
                  fill="#E2F0FA"
                  p-id="20479"
                ></path>
              </svg>
            </div>
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
              写入:
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
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  挂载点
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  文件系统
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  总容量
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  已用
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  可用
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
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
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  接口名称
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  IP地址
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  MAC地址
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  上传速率
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
                >
                  下载速率
                </th>
                <th
                  class="px-4 py-2 text-left text-sm font-medium text-gray-500 uppercase"
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
      radius: '126%', // 增大半径至95%
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
