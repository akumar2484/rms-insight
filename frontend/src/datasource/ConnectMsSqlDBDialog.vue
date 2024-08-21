<script setup>
import { computed } from 'vue'
import MsSQLForm from './MsSQLForm.vue';

const props = defineProps({ show: Boolean })
const emit = defineEmits(['update:show'])
const show = computed({
	get: () => props.show,
	set: (value) => emit('update:show', value),
})
</script>
<template>
	<Dialog v-model="show" :options="{ title: 'Connect to MSSQL DB' }">
		<template #body-content>
			<MsSQLForm @submit="show = false" />
		</template>
	</Dialog>
</template>
