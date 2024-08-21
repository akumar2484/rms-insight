<template>
	<div class="mt-8 flex items-center justify-between">
		<button
			class="flex items-center gap-2 rounded-full border border-white bg-[#000733] py-2 px-4 text-sm text-white"
			@click="showDialog = true"
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
			Create a new dashboard
		</button>
	</div>
	<div class="mt-6 flex items-stretch justify-between gap-4">
		<div class="md:w-full">
			<div
				class="relative max-h-[500px] overflow-y-auto rounded-lg border border-blue-200 bg-white p-4 sm:rounded-lg"
			>
				<div
					v-if="dashboards?.list?.length"
					class="flex flex-1 flex-col space-y-6 overflow-y-auto p-1"
				>
					<DashboardsGroup
						v-if="favorites.length > 0"
						:dashboards="favorites"
						title="Favorites"
					/>
					<DashboardsGroup
						v-if="settings.enable_permissions"
						:dashboards="privates"
						title="Private"
					/>
					<DashboardsGroup
						:dashboards="sortedDashboards"
						title="All"
						:enableSearch="true"
					/>
				</div>
				<div v-else class="flex flex-1 flex-col items-center justify-center space-y-1">
					<div class="text-base font-light text-gray-600">
						You haven't created any dashboards yet.
					</div>
					<div
						class="cursor-pointer text-sm font-light text-blue-500 hover:underline"
						@click="showDialog = true"
					>
						Create a new dashboard
					</div>
				</div>
			</div>
		</div>
	</div>

	<Dialog :options="{ title: 'New Dashboard' }" v-model="showDialog">
		<template #body-content>
			<Input
				type="text"
				label="Title"
				placeholder="Enter a suitable title..."
				v-model="newDashboardTitle"
			/>
		</template>
		<template #actions>
			<Button
				class="w-full"
				variant="solid"
				@click="createDashboard"
				:loading="dashboards.creating"
			>
				Create
			</Button>
		</template>
	</Dialog>
</template>

<script setup>
import PageBreadcrumbs from '@/components/PageBreadcrumbs.vue'
import useDashboards from '@/dashboard/useDashboards'
import settingsStore from '@/stores/settingsStore'
import { updateDocumentTitle } from '@/utils'
import { Plus } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardsGroup from './DashboardListGroup.vue'

const settings = settingsStore().settings

const dashboards = useDashboards()
dashboards.reload()
const sortedDashboards = computed(() => {
	// sort alphabetically
	return dashboards.list.sort((a, b) => a.title.localeCompare(b.title))
})
const favorites = computed(() => {
	return dashboards.list.filter((dashboard) => dashboard.is_favourite)
})
const privates = computed(() => {
	return dashboards.list.filter((dashboard) => dashboard.is_private)
})

const showDialog = ref(false)
const route = useRoute()
if (route.hash == '#new') {
	showDialog.value = true
}

const newDashboardTitle = ref('')
const router = useRouter()

async function createDashboard() {
	const name = await dashboards.create(newDashboardTitle.value)
	showDialog.value = false
	newDashboardTitle.value = ''
	router.push(`/dashboard/${name}`)
}

const pageMeta = ref({ title: 'Dashboards' })
updateDocumentTitle(pageMeta)
</script>
