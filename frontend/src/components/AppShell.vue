<template>
	<div>
		<Header />
		<RouterView v-slot="{ Component }">
			<Suspense>
				<div class="relative h-screen overflow-auto px-4 pt-24">
					<img
						src="../assets/summer-bg.jpg"
						alt="Background"
						class="absolute top-0 left-0 z-0 h-full w-full object-cover"
					/>
					<div class="relative z-10">
						<div class="font-avertareguler gap-5">
							<div
								class="relative mb-3 rounded-[40px] border border-gray-500 p-3 md:p-5"
							>
								<div
									class="absolute left-0 top-0 h-full w-full rounded-[40px] bg-white/50 blur-[1px] backdrop-blur-[1px]"
								></div>
								<div class="relative z-10">
									<button
										class="flex items-center gap-2 rounded-full border border-white bg-[#000733] py-2 px-4 text-sm text-white"
									>
										<span>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="w-5"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"
												/>
											</svg>
										</span>
										Back to RMS
									</button>
									<div class="my-6 text-black">
										<h1 class="text-2xl font-bold">Hello, Sohel 👋</h1>
										<p>Monday 29, July</p>
									</div>
									<Tabbar />
									<component :is="Component" :key="$route.fullPath" />
								</div>
							</div>
						</div>
					</div>
				</div>
				<template #fallback>
					<SuspenseFallback />
				</template>
			</Suspense>
		</RouterView>
	</div>
</template>

<script setup>
import Header from '@/components/Header.vue'
import Tabbar from '@/components/Tabbar.vue'
import SuspenseFallback from '@/components/SuspenseFallback'
import sessionStore from '@/stores/sessionStore'
import settingsStore from '@/stores/settingsStore'
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const session = sessionStore()
const route = useRoute()
const hideSidebar = computed(() => route.meta.hideSidebar || !session.isLoggedIn)
onMounted(() => session.isLoggedIn && settingsStore())
</script>
