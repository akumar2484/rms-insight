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
	<!-- <template>Added Print format -->
  <div>
    <!-- Button to Open Print Format Builder -->
    <button
      @click="showPrintBuilder = true"
      class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
    >
      Customize Print Format
    </button>

    <!-- Print Format Builder Modal -->
    <Modal v-if="showPrintBuilder" @close="showPrintBuilder = false">
      <template #header>
        <h3>Print Format Builder</h3>
      </template>

      <template #body>
        <div>
          <!-- Column Selection -->
          <h4 class="font-bold mb-2">Select Columns:</h4>
          <div v-for="column in availableColumns" :key="column.key" class="mb-1">
            <label>
              <input
                type="checkbox"
                v-model="selectedColumns"
                :value="column.key"
              />
              {{ column.label }}
            </label>
          </div>

          <!-- Custom Header -->
          <h4 class="font-bold mt-4 mb-2">Custom Header:</h4>
          <textarea
            v-model="customHeader"
            class="w-full border rounded p-2"
            placeholder="Enter custom header..."
          ></textarea>

          <!-- Custom Footer -->
          <h4 class="font-bold mt-4 mb-2">Custom Footer:</h4>
          <textarea
            v-model="customFooter"
            class="w-full border rounded p-2"
            placeholder="Enter custom footer..."
          ></textarea>
        </div>
      </template>

      <template #footer>
        <button
          @click="generatePrintPreview"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Preview & Print
        </button>
        <button
          @click="showPrintBuilder = false"
          class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Cancel
        </button>
      </template>
    </Modal>
  </div>
<!-- </template> -->

	<div class="mt-8 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="flex gap-2 overflow-visible py-1">
				<FormControl placeholder="Search by Title" v-model="searchQuery" :debounce="300">
					<template #prefix>
						<SearchIcon class="h-4 w-4 text-gray-500" />
					</template>
				</FormControl>
				<div>	
					<!-- <select v-model="searchType">
  						<option value="all">All</option>
 						<option value="table">Table</option>
				  		<option value="view">View</option>
					</select> -->
					<select v-model="searchType" class="border p-2 rounded">
    					<option v-for="option in options" :key="option.value" :value="option.value">
       				 		{{ option.label }}
   						 </option>
					</select>
				</div>
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

<script setup lang="jsx">
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import PageBreadcrumbs from '@/components/PageBreadcrumbs.vue'
import { ListView } from 'frappe-ui'
import { SearchIcon } from 'lucide-vue-next'
import { computed, inject, provide, ref, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import useDataSource from './useDataSource'
// import printReport from './print_report'

const props = defineProps({
	name: {
		type: String,
		required: true,
	},
})

const router = useRouter()
const dataSource = useDataSource(props.name)
provide('dataSource', dataSource)
dataSource.fetchTables()

const options = ref([
    { value: 'all', label: 'All' },
    { value: 'table', label: 'Table' },
    { value: 'view', label: 'View' },
]);

const searchQuery = ref('')
const searchType = ref('all');
const filteredTableList = computed(() => {
	let tableList = dataSource.tableList.filter((t) => !t.is_query_based)
	if (!tableList.length) return []
	if (searchType.value !== 'all') {
		console.log("Hiiiiiiiiiiiiiiiiiii",tableList,searchType.value)
        tableList = tableList.filter((table) =>
            searchType.value === 'table' ? table.table_type === 'Table' : table.table_type === 'View'
        );
    }
	if (searchType.value === 'view') {
		console.log("In view............",tableList,searchType.value)
        tableList = tableList.filter((table) => table.table_type === 'View'); // Show only views
    } else if (searchType.value === 'table') {
		console.log("In table............",tableList,searchType.value)
        tableList = tableList.filter((table) => table.table_type === 'Table'); // Show only tables
    }
	if (!searchQuery.value) return tableList
	return tableList.filter((table) => {
		return table.label.toLowerCase().includes(searchQuery.value.toLowerCase())
	})
})

const showDeleteDialog = ref(false)
const dropdownActions = computed(() => {
	return [
		{
			label: 'Sync Tables',
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
