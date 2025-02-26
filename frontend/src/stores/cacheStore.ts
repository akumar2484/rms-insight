import { DataSource } from '@/datasource/useDataSource'
import { DataSourceTable, DataSourceView } from '@/datasource/useDataSourceTable'
import { defineStore } from 'pinia'
import { ref } from 'vue'

type DataSourceCache = Record<string, DataSource>
type TableCache = Record<string, DataSourceTable>
type ViewCache = Record<string, DataSourceView>

const useCacheStore = defineStore('insights:cache', () => {
	const dataSourceCache = ref<DataSourceCache>({})
	function getDataSource(name: string) {
		return dataSourceCache.value[name]
	}
	function setDataSource(name: string, dataSource: DataSource) {
		dataSourceCache.value[name] = dataSource
	}

	const tableCache = ref<TableCache>({})
	function getTable(name: string) {
		return tableCache.value[name]
	}
	function setTable(name: string, table: DataSourceTable) {
		tableCache.value[name] = table
	}

	const viewCache = ref<ViewCache>({})
	function getView(name: string) {
		return viewCache.value[name]
	}
	function setView(name: string, view: DataSourceView) {
		viewCache.value[name] = view
	}
	return {
		getDataSource,
		setDataSource,
		getTable,
		setTable,
		getView,
		setView
	}
})

export default useCacheStore
