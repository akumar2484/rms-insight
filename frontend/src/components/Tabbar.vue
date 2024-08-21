<template>
	<div class="flex items-center gap-2">
		<div v-for="route in tabbarItems" :key="route.path">
			<router-link
				:to="route.path"
				:class="[route.current && 'bg-blue-700 text-white']"
				aria-current="page"
			>
				<div
					class="rounded-md bg-[#EEF4FE] py-3 px-5 font-semibold text-[#102030] duration-200 hover:bg-blue-700 hover:text-white"
				>
					{{ route.label }}
				</div>
			</router-link>
		</div>
	</div>
</template>

<script setup>
import { Avatar } from 'frappe-ui'

import HelpDialog from '@/components/HelpDialog.vue'
import sessionStore from '@/stores/sessionStore'
import settingsStore from '@/stores/settingsStore'
import { createResource } from 'frappe-ui'
import {
	Book,
	Database,
	GanttChartSquare,
	HomeIcon,
	LayoutPanelTop,
	Settings,
	User,
	Users,
	BookOpen,
} from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const session = sessionStore()
const settings = settingsStore().settings

const showHelpDialog = ref(false)
const tabbarItems = ref([
	{
		path: '/',
		label: 'Home',
		name: 'Home',
		current: false,
	},
	{
		path: '/dashboard',
		label: 'Dashboards',
		name: 'Dashboard',
		current: false,
	},
	{
		path: '/data-source',
		label: 'Data Sources',
		name: 'Data Source',
	},
	{
		path: '/query',
		label: 'Query',
		name: 'QueryList',
		current: false,
	},
])

const route = useRoute()
const currentRoute = computed(() => {
	tabbarItems.value.forEach((item) => {
		// check if /<route> or /<route>/<id> is in sidebar item path
		item.current = route.path.match(new RegExp(`^${item.path}(/|$)`))
	})
	return route.path
})

const open = (url) => window.open(url, '_blank')
</script>
