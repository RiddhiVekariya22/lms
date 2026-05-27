<template>
	<FrappeUIProvider>
		<Layout class="isolate text-p-base">
			<router-view />
		</Layout>
		<InstallPrompt v-if="isMobile && !settings.data?.disable_pwa" />
		<Dialogs />
		<div class="cursor-blob" ref="blobEl"></div>
	</FrappeUIProvider>
</template>
<script setup>
import { FrappeUIProvider } from 'frappe-ui'
import { Dialogs } from '@/utils/dialogs'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useScreenSize } from './utils/composables'
import { useSettings } from '@/stores/settings'
import { useRouter } from 'vue-router'
import DesktopLayout from './components/DesktopLayout.vue'
import MobileLayout from './components/MobileLayout.vue'
import NoSidebarLayout from './components/NoSidebarLayout.vue'
import InstallPrompt from './components/InstallPrompt.vue'

const { isMobile } = useScreenSize()
const blobEl = ref(null)

onMounted(() => {
	if (window !== window.top) return
	const blob = blobEl.value
	if (!blob) return
	let raf = 0, tx = 0, ty = 0, x = 0, y = 0

	const onMove = (e) => {
		tx = e.clientX; ty = e.clientY
		blob.classList.add('on')
		tick()
	}
	const onLeave = () => blob.classList.remove('on')

	function tick() {
		cancelAnimationFrame(raf)
		raf = requestAnimationFrame(() => {
			x += (tx - x) * 0.18
			y += (ty - y) * 0.18
			blob.style.transform = `translate(${(x - 8).toFixed(2)}px, ${(y - 8).toFixed(2)}px)`
			if (Math.abs(tx - x) > 0.2 || Math.abs(ty - y) > 0.2) tick()
		})
	}

	window.addEventListener('mousemove', onMove)
	window.addEventListener('mouseleave', onLeave)

	onUnmounted(() => {
		window.removeEventListener('mousemove', onMove)
		window.removeEventListener('mouseleave', onLeave)
		cancelAnimationFrame(raf)
	})
})
const router = useRouter()
const noSidebar = ref(false)
const { settings } = useSettings()

router.beforeEach((to, from, next) => {
	if (to.query.fromLesson || to.path === '/persona') {
		noSidebar.value = true
	} else {
		noSidebar.value = false
	}
	next()
})

const Layout = computed(() => {
	if (noSidebar.value) {
		return NoSidebarLayout
	}
	if (isMobile.value) {
		return MobileLayout
	}
	return DesktopLayout
})

onUnmounted(() => {
	noSidebar.value = false
})
</script>
