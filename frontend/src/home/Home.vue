<script setup>
import { inject } from 'vue'
import sessionStore from '@/stores/sessionStore'
import HomeQuickActions from './HomeQuickActions.vue'
import HomeRecentRecords from './HomeRecentRecords.vue'

const session = sessionStore()

const $dayjs = inject('$dayjs')
const today = $dayjs().format('dddd, D MMMM')

document.title = 'Home | RMS Insights'
</script>

<template>
	<div class="mt-6 flex items-stretch justify-between gap-4">
		<div class="space-y-2 rounded-lg bg-white p-4 md:w-1/4">
			<HomeQuickActions></HomeQuickActions>
			<div class="mt-8 space-y-1 max-h-[250px] overflow-y-auto">
				<HomeRecentRecords></HomeRecentRecords>
			</div>
		</div>
		<div class="rounded-lg bg-white p-4 md:w-3/4">2</div>
	</div>
</template>
