<template>
	<div class="mt-8 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<div class="flex gap-2 overflow-visible py-1">
				<FormControl placeholder="Search by Title" v-model="searchQuery" :debounce="300">
					<template #prefix>
						<SearchIcon class="h-4 w-4 text-gray-500" />
					</template>
				</FormControl>
			</div>
		</div>
		<button
			class="flex items-center gap-2 rounded-full border border-white bg-[#000733] py-2 px-4 text-sm text-white"
			@click="new_dialog = true"
		>
			<span>
				<svg
					class="h-6 w-6"
					xmlns="http://www.w3.org/2000/svg"
					width="1em"
					height="1em"
					viewBox="0 0 20 20"
				>
					<path
						fill="white"
						d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5z"
					/>
				</svg>
			</span>
			New Data Source
		</button>
	</div>

	<div class="mt-6 flex items-stretch justify-between gap-4">
		<div class="md:w-full">
			<div
				class="relative max-h-[500px] overflow-y-auto rounded-lg border border-blue-200 bg-white p-4 sm:rounded-lg"
			>
				<ListView
					:columns="dataSourceListColumns"
					:rows="filteredSourceList"
					:row-key="'name'"
					:options="{
						showTooltip: false,
						getRowRoute: (dataSource) => ({
							name: 'DataSource',
							params: { name: dataSource.name },
						}),
						emptyState: {
							title: 'No Data Sources.',
							description: 'No data sources to display.',
							button: {
								label: 'New Data Source',
								variant: 'solid',
								onClick: () => (new_dialog = true),
							},
						},
					}"
				>
				</ListView>
			</div>
		</div>
	</div>

	<NewDialogWithTypes
		v-model:show="new_dialog"
		title="Select Source Type"
		:types="databaseTypes"
	/>

	<ConnectMariaDBDialog v-model:show="showConnectMariaDBDialog" />
	<ConnectPostgreDBDialog v-model:show="showConnectPostgreDBDialog" />
	<ConnectMsSqlDBDialog v-model:show="showConnectMSSQLDBDialog" />
	<UploadCSVFileDialog v-model:show="showCSVFileUploadDialog" />
</template>

<script setup lang="jsx">
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import NewDialogWithTypes from '@/components/NewDialogWithTypes.vue'
import PageBreadcrumbs from '@/components/PageBreadcrumbs.vue'
import ConnectMariaDBDialog from '@/datasource/ConnectMariaDBDialog.vue'
import ConnectPostgreDBDialog from '@/datasource/ConnectPostgreDBDialog.vue'
import ConnectMsSqlDBDialog from './ConnectMsSqlDBDialog.vue'
import UploadCSVFileDialog from '@/datasource/UploadCSVFileDialog.vue'
import useDataSourceStore from '@/stores/dataSourceStore'
import { updateDocumentTitle } from '@/utils'
import { ListView } from 'frappe-ui'
import { PlusIcon, SearchIcon } from 'lucide-vue-next'
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const new_dialog = ref(false)

const route = useRoute()
if (route.hash == '#new') {
	new_dialog.value = true
}

const sources = useDataSourceStore()
const searchQuery = ref('')
const filteredSourceList = computed(() => {
	if (searchQuery.value) {
		return sources.list.filter((source) => {
			return source.title.toLowerCase().includes(searchQuery.value.toLowerCase())
		})
	}
	return sources.list
})

const router = useRouter()
const showConnectMariaDBDialog = ref(false)
const showConnectPostgreDBDialog = ref(false)
const showCSVFileUploadDialog = ref(false)
const showConnectMSSQLDBDialog = ref(false)
const databaseTypes = ref([
	{
		label: 'MariaDB',
		description: 'Connect to a MariaDB database',
		imgSrc: '/src/assets/MariaDBIcon.png',
		onClick: () => {
			new_dialog.value = false
			showConnectMariaDBDialog.value = true
		},
	},
	{
		label: 'PostgreSQL',
		description: 'Connect to a PostgreSQL database',
		imgSrc: '/src/assets/PostgreSQLIcon.png',
		onClick: () => {
			new_dialog.value = false
			showConnectPostgreDBDialog.value = true
		},
	},
	{
		label: 'CSV',
		description: 'Upload a CSV file',
		imgSrc: '/src/assets/SheetIcon.png',
		onClick: () => {
			new_dialog.value = false
			showCSVFileUploadDialog.value = true
		},
	},
	{
		label: 'MSSQL',
		description: 'Connect to a MSSQL database',
		imgSrc: '/src/assets/PostgreSQLIcon.png',
		onClick: () => {
			new_dialog.value = false
			showConnectMSSQLDBDialog.value = true
		},
	},
])

const dataSourceListColumns = [
	{ label: 'Title', key: 'title' },
	{
		label: 'Status',
		key: 'status',
		prefix: ({ row }) => {
			const color = row.status == 'Inactive' ? 'text-gray-500' : 'text-green-500'
			return <IndicatorIcon class={color} />
		},
	},
	{ label: 'Database Type', key: 'database_type' },
	{ label: 'Created', key: 'created_from_now' },
]

const pageMeta = ref({ title: 'Data Sources' })
updateDocumentTitle(pageMeta)
</script>
