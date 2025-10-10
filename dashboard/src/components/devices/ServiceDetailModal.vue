<template>
	<a-modal
		:open="visible"
		:title="'服务详情 - ' + deviceName"
		@cancel="handleCancel"
		@update:open="handleUpdateOpen"
		centered
		width="660px"
		:body-style="{ height: height - 120 + 'px' }"
		:footer="null"
		:destroyOnClose="true"
	>
		<div class="flex flex-col size-full">
			<div class="flex-1 overflow-auto">
				<a-list :data-source="paginatedServices" :pagination="false">
					<template #renderItem="{ item, index }">
						<a-list-item>
							<div style="width: 100%">
								<div>
									<strong
									>{{
											(servicesPagination.current - 1) *
											servicesPagination.pageSize +
											index +
											1
										}}. PID: {{ item.pid || 'N/A' }}</strong
									>
									- {{ item.process_name || '未知进程' }}
									<span style="margin-left: 10px; font-size: 12px; color: #666"
									>({{ item.status }})</span
									>
								</div>
								<div style="font-size: 12px; color: #666">
									协议: {{ item.protocol }} | 地址: {{ item.local_address }}
								</div>
							</div>
						</a-list-item>
					</template>
				</a-list>
			</div>
			<div class="border-t border-gray-200 pt-[12px]">
				<a-pagination
					v-model:current="servicesPagination.current"
					v-model:page-size="servicesPagination.pageSize"
					:total="servicesList.length"
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
	servicesList: {
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
const servicesPagination = ref({
	current: 1,
	pageSize: 12
})

// 计算分页后的服务列表
const paginatedServices = computed(() => {
	const start =
		(servicesPagination.value.current - 1) * servicesPagination.value.pageSize
	const end = start + servicesPagination.value.pageSize
	return props.servicesList.slice(start, end)
})

// 处理分页变化
const handlePageChange = (page, pageSize) => {
	servicesPagination.value.current = page
	servicesPagination.value.pageSize = pageSize
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
