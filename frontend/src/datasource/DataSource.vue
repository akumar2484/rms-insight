<script setup lang="jsx">
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import PageBreadcrumbs from '@/components/PageBreadcrumbs.vue'
import { ListView } from 'frappe-ui'
import { SearchIcon } from 'lucide-vue-next'
import { computed, inject, provide, ref, watchEffect, watch } from 'vue'
import { useRouter } from 'vue-router'
import useDataSource from './useDataSource'

const props = defineProps({
	name: {
		type: String,
		required: true,
	},
})

const router = useRouter()
const dataSource = useDataSource(props.name)
const dropdownOptions = ref([
	{ label: 'Tables', value: 'tables' },
	{ label: 'Views', value: 'views' },
])

const selectedOption = ref('tables')

provide('dataSource', dataSource)
if (selectedOption.value === 'tables') {
	dataSource.fetchTables()
}

watch(selectedOption, (newValue) => {
	if (newValue === 'tables') {
		dataSource.fetchTables()
	} else if (newValue === 'views') {
		dataSource.fetchViews()
	}
})

const searchQuery = ref('')
const filteredTableList = computed(() => {
	const tableList = dataSource.tableList.filter((t) => !t.is_query_based)
	if (!tableList.length) return []
	if (!searchQuery.value) return tableList
	return tableList.filter((table) => {
		return table.label.toLowerCase().includes(searchQuery.value.toLowerCase())
	})
})

const filteredViewList = computed(() => {
	const viewList = dataSource.viewList.filter((t) => !t.is_query_based)
	if (!viewList.length) return []
	if (!searchQuery.value) return viewList
	return viewList.filter((view) => {
		return view.label.toLowerCase().includes(searchQuery.value.toLowerCase())
	})
})

const showDeleteDialog = ref(false)
const dropdownActions = computed(() => {
	return [
		{
			label: 'Sync Tables/Views',
			icon: 'refresh-cw',
			onClick: syncTables,
		},
		{
			label: 'Delete',
			icon: 'trash',
			onClick: () => (showDeleteDialog.value = true),
		},
	]
})

const $notify = inject('$notify')
function syncTables() {
	dataSource
		.syncTables()
		.catch((err) => $notify({ title: 'Error Syncing Tables', variant: 'error' }))
}

watchEffect(() => {
	if (dataSource.doc?.name) {
		const title = dataSource.doc.title || dataSource.doc.name
		document.title = `${title} - Frappe Insights`
	}
})

const tableListColumns = [
	{ label: 'Table', key: 'label' },
	{
		label: 'Status',
		key: 'status',
		getLabel: ({ row }) => (row.hidden ? 'Disabled' : 'Enabled'),
		prefix: ({ row }) => {
			const color = row.hidden ? 'text-gray-500' : 'text-green-500'
			return <IndicatorIcon class={color} />
		},
	},
]
</script>

<template>
	<!-- <header class="sticky top-0 z-10 flex items-center justify-between bg-white px-5 py-2.5">
		<PageBreadcrumbs
			class="h-7"
			:items="[
				{ label: 'Data Sources', route: { path: '/data-source' } },
				{ label: dataSource.doc.title },
			]"
		/>
	</header> -->

	<div class="mt-8 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="flex gap-2 overflow-visible py-1">
				<FormControl placeholder="Search by Title" v-model="searchQuery" :debounce="300">
					<template #prefix>
						<SearchIcon class="h-4 w-4 text-gray-500" />
					</template>
				</FormControl>

				<select
					v-model="selectedOption"
					id="dropdown"
					class="h-7 rounded border border-gray-100 bg-gray-100 py-1.5 pl-2 pr-2 text-base text-gray-800 placeholder-gray-500 transition-colors hover:border-gray-200 hover:bg-gray-200 focus:border-gray-500 focus:bg-white focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400"
				>
					<option value="" disabled hidden>Select an option</option>
					<option
						v-for="option in dropdownOptions"
						:key="option.value"
						:value="option.value"
					>
						{{ option.label }}
					</option>
				</select>
			</div>
		</div>
		<div>
			<Button
				variant="outline"
				iconLeft="link-2"
				@click="router.push(`/data-source/${dataSource.doc.name}/relationships`)"
			>
				Manage Relationships
			</Button>
			<Dropdown
				placement="left"
				:button="{ icon: 'more-horizontal', variant: 'outline' }"
				:options="dropdownActions"
			/>
		</div>
	</div>

	<div class="mt-6 flex items-stretch justify-between gap-4">
		<div class="md:w-full">
			<div
				class="relative max-h-[500px] overflow-y-auto rounded-lg border border-blue-200 bg-white p-4 sm:rounded-lg"
			>
				<ListView
					:columns="tableListColumns"
					:rows="selectedOption === 'tables' ? filteredTableList : filteredViewList"
					:row-key="'name'"
					:options="{
						showTooltip: false,
						getRowRoute: (table) => {
							const type =
								selectedOption && selectedOption === 'tables' ? 'table' : 'view'
							return {
								name: 'DataSourceTable',
								params: {
									name: dataSource.doc.name,
									table: table.name,
									type: type,
								},
							}
						},
						emptyState: {
							title: selectedOption === 'tables' ? 'No tables.' : 'No views.',
							description:
								selectedOption === 'tables'
									? 'No tables to display.'
									: 'No views to display.',
							button: {
								label: 'Sync Tables/Views',
								variant: 'solid',
								onClick: syncTables,
							},
						},
					}"
				>
				</ListView>
			</div>
		</div>
	</div>

	<!-- <div class="mb-4 flex h-full flex-col gap-2 overflow-auto px-4">
		<div class="flex gap-2 overflow-visible py-1">
			<FormControl placeholder="Search by Title" v-model="searchQuery" :debounce="300">
				<template #prefix>
					<SearchIcon class="h-4 w-4 text-gray-500" />
				</template>
			</FormControl>
			<Button
				variant="outline"
				iconLeft="link-2"
				@click="router.push(`/data-source/${dataSource.doc.name}/relationships`)"
			>
				Manage Relationships
			</Button>
			<Dropdown
				placement="left"
				:button="{ icon: 'more-horizontal', variant: 'outline' }"
				:options="dropdownActions"
			/>
		</div>
		<ListView
			:columns="tableListColumns"
			:rows="filteredTableList"
			:row-key="'name'"
			:options="{
				showTooltip: false,
				getRowRoute: (table) => ({
					name: 'DataSourceTable',
					params: { name: dataSource.doc.name, table: table.name },
				}),
				emptyState: {
					title: 'No tables.',
					description: 'No tables to display.',
					button: {
						label: 'Sync Tables',
						variant: 'solid',
						onClick: syncTables,
					},
				},
			}"
		>
		</ListView>
	</div> -->

	<Dialog
		v-model="showDeleteDialog"
		:dismissable="true"
		:options="{
			title: 'Delete Data Source',
			message: 'Are you sure you want to delete this data source?',
			icon: { name: 'trash', appearance: 'danger' },
			actions: [
				{
					label: 'Delete',
					variant: 'solid',
					theme: 'red',
					onClick: async () => {
						await dataSource.delete()
						router.push({ name: 'DataSourceList' })
					},
				},
			],
		}"
	>
	</Dialog>
</template>
