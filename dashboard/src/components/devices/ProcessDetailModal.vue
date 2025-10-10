<template>
	<a-modal
		:open="visible"
		:title="'进程详情 - ' + deviceName"
		@cancel="handleCancel"
		@update:open="handleUpdateOpen"
		width="660px"
		centered
		:body-style="{ height: height - 120 + 'px' }"
		:footer="null"
		:destroyOnClose="true"
	>
		<div class="flex flex-col size-full">
			<div class="flex-1 overflow-auto">
				<a-list :data-source="paginatedProcesses" :pagination="false">
					<template #renderItem="{ item, index }">
						<a-list-item>
							<div style="width: 100%">
								<div>
									<strong
									>{{
											(processesPagination.current - 1) *
											processesPagination.pageSize +
											index +
											1
										}}. PID: {{ item.pid }}</strong
									>
									- {{ item.name }}
									<span style="margin-left: 10px; font-size: 12px; color: #666"
									>({{ item.status }})</span
									>
								</div>
								<div style="font-size: 12px; color: #666">
									CPU: {{ item.cpu_percent }}% | 内存:
									{{ item.memory_percent }}%
								</div>
								<!-- 显示端口信息 -->
								<div
									v-if="item.ports && item.ports.length > 0"
									style="font-size: 12px; color: #888; margin-top: 5px"
								>
									<div v-for="(port, portIndex) in item.ports" :key="portIndex">
										{{ port.protocol }}: {{ port.local_address }}
									</div>
								</div>
							</div>
						</a-list-item>
					</template>
				</a-list>
			</div>
			<div class="border-t border-gray-200 pt-[12px]">
				<a-pagination
					v-model:current="processesPagination.current"
					v-model:page-size="processesPagination.pageSize"
					:total="processesList.length"
					show-size-changer
					@change="handlePageChange"
				/>
			</div>
		</div>
	</a-modal>
</template>

<script setup>
import {ref, computed} from 'vue'
import {useWindowSize} from '@vueuse/core'

const props = defineProps({
	visible: {
		type: Boolean,
		default: false
	},
	processesList: {
		type: Array,
		default: () => []
	},
	deviceName: {
		type: String,
		default: ''
	}
})

const emit = defineEmits(['update:visible', 'cancel'])

const {height} = useWindowSize()

// 分页相关数据
const processesPagination = ref({
	current: 1,
	pageSize: 10
})

// 计算分页后的进程列表
const paginatedProcesses = computed(() => {
	const start =
		(processesPagination.value.current - 1) * processesPagination.value.pageSize
	const end = start + processesPagination.value.pageSize
	return props.processesList.slice(start, end)
})

// 处理分页变化
const handlePageChange = (page, pageSize) => {
	processesPagination.value.current = page
	processesPagination.value.pageSize = pageSize
}

// 关闭模态框
const handleCancel = () => {
	emit('update:visible', false)
	emit('cancel')
}

// 处理模态框开启状态变化
const handleUpdateOpen = (open) => {
	emit('update:visible', open)
}
</script>

<style lang="less" scoped></style>
