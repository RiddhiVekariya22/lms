<template>
	<div
		ref="dashboardRef"
		class="gai-dashboard"
		:data-dark="isDark ? 'true' : null"
		:data-anim="animationMode"
	>
		<div ref="cursorRef" class="cursor-blob" aria-hidden="true"></div>

		<header class="gai-header">
			<div class="gai-header-inner">
				<router-link :to="{ name: 'Home' }" class="gai-logo">
					g<span>a</span>i.
				</router-link>
				<div class="gai-user">
					<span>{{ userName }}</span>
					<div class="gai-avatar">{{ userInitial }}</div>
				</div>
			</div>
		</header>

		<main>
			<section class="gai-greeting">
				<div class="gai-greeting-copy rv" style="--rv-d: 0ms">
					<div class="eyebrow">{{ eyebrowText }}</div>
					<h1>
						<span>{{ __('Good morning,') }}</span>
						<em>{{ __('what will you build today?') }}</em>
					</h1>
					<p>
						{{ subtitle }}
					</p>
				</div>

				<aside class="streak-card rv" style="--rv-d: 120ms">
					<div class="streak-top">
						<div>
							<div class="mono-label">{{ __('Current streak') }}</div>
							<div class="streak-count">
								{{ animatedStreak }}
								<span>{{ __('days') }}</span>
							</div>
						</div>
						<svg
							class="flame"
							viewBox="0 0 64 64"
							role="img"
							aria-label="Streak"
						>
							<path
								d="M33.7 4.8c2.9 8.2-.4 12.7-3.5 16.9-2.7 3.6-5.2 7-3.5 12.4 2.2-3.1 4.6-5.5 7.6-7.6 1.1 6.7 7.4 9.4 7.4 17.1 0 8.4-6.8 15.1-15.2 15.1S11.3 52 11.3 43.6c0-8.8 6.5-15.2 11.2-21.1 4.3-5.5 6.4-10.2 5.7-17.7 2.1.7 4 2.1 5.5 4z"
							/>
							<path
								class="flame-core"
								d="M30.9 38.1c1.3 4.1 5.5 5.7 5.5 10.2 0 4.6-3.7 8.4-8.4 8.4s-8.5-3.8-8.5-8.4c0-4.3 2.9-7.4 5.6-10.3 1.6-1.7 3-3.7 3.6-6.8 1.3 1.8 1.8 4.1 2.2 6.9z"
							/>
						</svg>
					</div>

					<div class="dot-grid" aria-label="Recent learning activity">
						<span
							v-for="(dot, index) in activityDots"
							:key="index"
							class="activity-dot"
							:class="dot"
							:style="{ '--dot-d': `${index * 20}ms` }"
						></span>
					</div>

					<div class="streak-stats">
						<div>
							<div class="mono-label">{{ __('Longest') }}</div>
							<strong>{{ longestStreak }}</strong>
						</div>
						<div>
							<div class="mono-label">{{ __('Courses') }}</div>
							<strong>{{ courseCount }}</strong>
						</div>
					</div>
				</aside>
			</section>

			<section class="course-section">
				<div class="section-title">
					<div class="eyebrow">{{ __('Enrolled Programs') }}</div>
					<h2>{{ __('Your learning tracks') }}</h2>
				</div>

				<div class="course-list">
					<router-link
						v-for="(course, index) in displayCourses"
						:key="course.key"
						class="course-row rv"
						:style="{ '--rv-d': `${index * 80}ms` }"
						:to="course.to"
					>
						<div class="course-art" :class="course.artClass">
							<span
								v-if="course.badge"
								class="course-badge"
								:class="course.badgeClass"
							>
								{{ course.badge }}
							</span>
						</div>

						<div class="course-copy">
							<div class="course-tags">
								<span
									v-for="tag in course.tags"
									:key="tag.label"
									:class="tag.class"
								>
									{{ tag.label }}
								</span>
							</div>
							<h3>{{ course.title }}</h3>
							<p v-if="course.description">{{ course.description }}</p>
						</div>

						<div class="course-arrow" aria-hidden="true">-></div>
					</router-link>

					<div v-if="!displayCourses.length" class="empty-row rv">
						{{ __('No courses returned by the student home API.') }}
					</div>
				</div>
			</section>

			<section class="live-section">
				<div class="section-title">
					<div class="eyebrow">{{ __('Schedule') }}</div>
					<h2>{{ __('Upcoming checkpoints') }}</h2>
				</div>
				<div class="mini-grid">
					<div class="mini-panel rv" style="--rv-d: 0ms">
						<div class="mono-label">{{ __('Live classes') }}</div>
						<strong>{{ liveClassCount }}</strong>
						<p v-if="nextLiveClassLabel">{{ nextLiveClassLabel }}</p>
					</div>
					<div class="mini-panel rv" style="--rv-d: 80ms">
						<div class="mono-label">{{ __('Evaluations') }}</div>
						<strong>{{ evalCount }}</strong>
					</div>
					<div class="mini-panel rv" style="--rv-d: 160ms">
						<div class="mono-label">{{ __('Batches') }}</div>
						<strong>{{ batchCount }}</strong>
						<p v-if="nextBatchLabel">{{ nextBatchLabel }}</p>
					</div>
				</div>
			</section>
		</main>
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	inject,
	nextTick,
	onBeforeUnmount,
	onMounted,
	ref,
	watch,
} from 'vue'
import { call, createResource } from 'frappe-ui'

type CourseView = {
	key: string
	title: string
	description?: string
	badge?: string
	tags: Array<{ label: string; class?: string }>
	artClass: string
	badgeClass: string
	to: any
}

const user = inject<any>('$user')
const dayjs = inject<any>('$dayjs')
const dashboardRef = ref<HTMLElement | null>(null)
const cursorRef = ref<HTMLElement | null>(null)
const evalCount = ref(0)
const animatedStreak = ref(0)
const isDark = ref(false)
const animationMode = ref<'off' | 'low' | 'regular'>('regular')

const myLiveClasses = createResource({
	url: 'lms.lms.api.get_my_live_classes',
	auto: true,
})

const myCourses = createResource({
	url: 'lms.lms.api.get_my_courses',
	auto: true,
})

const myBatches = createResource({
	url: 'lms.lms.api.get_my_batches',
	auto: true,
})

const streakInfo = createResource({
	url: 'lms.lms.api.get_streak_info',
	auto: true,
})

let revealObserver: IntersectionObserver | null = null
let rafId = 0
let cursorX = 0
let cursorY = 0
let blobX = 0
let blobY = 0

const courseCount = computed(() =>
	Array.isArray(myCourses.data) ? myCourses.data.length : 0
)

const liveClassCount = computed(() =>
	Array.isArray(myLiveClasses.data) ? myLiveClasses.data.length : 0
)

const batchCount = computed(() =>
	Array.isArray(myBatches.data) ? myBatches.data.length : 0
)

const currentStreak = computed(() => streakInfo.data?.current_streak ?? 0)
const longestStreak = computed(() => streakInfo.data?.longest_streak ?? currentStreak.value)

const userName = computed(() => user?.data?.full_name || user?.data?.name || __('Student'))
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())

const eyebrowText = computed(() => {
	const date = dayjs ? dayjs().format('dddd, MMMM YYYY') : __('Today')
	return `${date} · ${courseCount.value} ${__('courses')} · ${batchCount.value} ${__('batches')}`
})

const subtitle = computed(() => {
	if (liveClassCount.value && evalCount.value) {
		return __('You have {0} upcoming live classes and {1} evaluations scheduled.').format(
			liveClassCount.value,
			evalCount.value
		)
	}
	if (liveClassCount.value) {
		return __('You have {0} upcoming live classes ready on your calendar.').format(
			liveClassCount.value
		)
	}
	if (evalCount.value) {
		return __('You have {0} upcoming evaluations scheduled.').format(evalCount.value)
	}
	return `${courseCount.value} ${__('courses')} · ${liveClassCount.value} ${__('live classes')} · ${batchCount.value} ${__('batches')}`
})

const activityDots = computed(() => {
	const active = Math.min(20, Math.max(3, currentStreak.value || courseCount.value + liveClassCount.value))
	return Array.from({ length: 42 }, (_, index) => {
		if (index === active - 1) return 'today'
		if (index < active) return 'active'
		if (index < active + 5) return 'active-dim'
		return 'base'
	})
})

const displayCourses = computed<CourseView[]>(() => {
	const apiCourses = Array.isArray(myCourses.data) ? myCourses.data.slice(0, 3) : []
	return apiCourses
		.filter((course: any) => course?.name && course?.title)
		.map((course: any, index: number) => {
		const visual = courseVisuals[index % courseVisuals.length]
		const tags = getCourseTags(course, visual.tagClass)
		return {
			key: course.name,
			title: course.title,
			description: course.short_introduction || course.description || '',
			badge: course.category || course.status || '',
			tags,
			artClass: visual.artClass,
			badgeClass: visual.badgeClass,
			to: course.name
				? { name: 'CourseDetail', params: { courseName: course.name } }
				: { name: 'Courses' },
		}
	})
})

const nextLiveClassLabel = computed(() => {
	const liveClasses = Array.isArray(myLiveClasses.data) ? myLiveClasses.data : []
	const nextClass = liveClasses[0]
	if (!nextClass) return ''
	if (!dayjs || !nextClass.date) return nextClass.title || ''
	return [nextClass.title, dayjs(nextClass.date).format('DD MMM')]
		.filter(Boolean)
		.join(' - ')
})

const nextBatchLabel = computed(() => {
	const batches = Array.isArray(myBatches.data) ? myBatches.data : []
	const nextBatch = batches[0]
	if (!nextBatch) return ''
	return nextBatch.title || nextBatch.name || ''
})

const courseVisuals = [
	{
		artClass: 'mesh-warm',
		badgeClass: 'badge-warm',
		tagClass: 'tag-warm',
	},
	{
		artClass: 'mesh-cool',
		badgeClass: 'badge-cool',
		tagClass: 'tag-cool',
	},
	{
		artClass: 'mesh-green',
		badgeClass: 'badge-green',
		tagClass: 'tag-green',
	},
]

function getCourseTags(course: any, highlightClass: string) {
	const tags: Array<{ label: string; class?: string }> = []

	if (course.category) tags.push({ label: course.category, class: highlightClass })
	if (course.status) tags.push({ label: course.status })
	if (course.lessons) tags.push({ label: `${course.lessons} ${__('lessons')}` })
	if (course.enrollments) tags.push({ label: `${course.enrollments} ${__('enrolled')}` })
	if (course.rating) tags.push({ label: `${course.rating} ${__('rating')}` })
	if (course.membership?.progress !== undefined) {
		tags.push({ label: `${Math.ceil(course.membership.progress)}% ${__('complete')}` })
	}

	return tags
}

onMounted(async () => {
	isDark.value =
		document.documentElement.getAttribute('data-theme') === 'dark' ||
		window.matchMedia?.('(prefers-color-scheme: dark)').matches ||
		false

	await fetchEvalCount()
	await nextTick()
	setupReveal()
	setupCursor()
	animateStreak()
})

onBeforeUnmount(() => {
	revealObserver?.disconnect()
	cancelAnimationFrame(rafId)
	window.removeEventListener('mousemove', onMouseMove)
	document.documentElement.removeEventListener('mouseleave', hideCursor)
})

watch(currentStreak, () => {
	animateStreak()
})

async function fetchEvalCount() {
	if (!user?.data?.name || !dayjs) return

	try {
		evalCount.value = await call('frappe.client.get_count', {
			doctype: 'LMS Certificate Request',
			filters: {
				member: user.data.name,
				status: 'Upcoming',
				date: ['>=', dayjs().format('YYYY-MM-DD')],
			},
		})
	} catch {
		evalCount.value = 0
	}
}

function setupReveal() {
	const root = dashboardRef.value
	if (!root) return

	if (animationMode.value === 'off') {
		root.querySelectorAll('.rv').forEach((item) => item.classList.add('in'))
		return
	}

	revealObserver = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					entry.target.classList.add('in')
					revealObserver?.unobserve(entry.target)
				}
			})
		},
		{ threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
	)

	root.querySelectorAll('.rv').forEach((item) => revealObserver?.observe(item))
}

function animateStreak() {
	if (animationMode.value === 'off') {
		animatedStreak.value = currentStreak.value
		return
	}

	const target = currentStreak.value
	const startedAt = performance.now()
	const duration = animationMode.value === 'low' ? 450 : 800

	const tick = (now: number) => {
		const progress = Math.min(1, (now - startedAt) / duration)
		const eased = 1 - Math.pow(1 - progress, 3)
		animatedStreak.value = Math.round(target * eased)
		if (progress < 1) requestAnimationFrame(tick)
	}

	requestAnimationFrame(tick)
}

function setupCursor() {
	if (animationMode.value === 'off') return
	window.addEventListener('mousemove', onMouseMove)
	document.documentElement.addEventListener('mouseleave', hideCursor)
	rafId = requestAnimationFrame(moveCursor)
}

function onMouseMove(event: MouseEvent) {
	cursorX = event.clientX
	cursorY = event.clientY
	cursorRef.value?.classList.add('visible')
}

function hideCursor() {
	cursorRef.value?.classList.remove('visible')
}

function moveCursor() {
	blobX += (cursorX - blobX) * 0.18
	blobY += (cursorY - blobY) * 0.18
	if (cursorRef.value) {
		cursorRef.value.style.transform = `translate3d(${blobX - 14}px, ${blobY - 14}px, 0)`
	}
	rafId = requestAnimationFrame(moveCursor)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

.gai-dashboard {
	--accent: #6B3FA0;
	--accent-dim: color-mix(in oklab, #ee6708 45%, var(--border));
	--accent-glow: color-mix(in oklab, #ee6708 18%, transparent);
	--ink: #0a0a0a;
	--paper: #fafaf8;
	--surface: #f1ede4;
	--muted: #7a7a7a;
	--border: #e5e5e0;
	--gap: 24px;
	--r: 12px;
	min-height: 100vh;
	background: var(--paper);
	color: var(--ink);
	font-family: 'Space Grotesk', sans-serif;
	transition:
		background-color 150ms ease,
		color 150ms ease;
}

.gai-dashboard[data-dark='true'] {
	--ink: #fafaf8;
	--paper: #0a0a0a;
	--surface: #161613;
	--muted: #888888;
	--border: #2a2a28;
	--accent-glow: color-mix(in oklab, #ee6708 22%, transparent);
}

.gai-header {
	position: sticky;
	top: 0;
	z-index: 30;
	border-bottom: 1px solid var(--border);
	background: color-mix(in oklab, var(--paper) 85%, transparent);
	backdrop-filter: blur(14px);
}

.gai-header-inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 18px 40px;
}

.gai-logo {
	color: var(--ink);
	font-size: 20px;
	font-weight: 700;
	letter-spacing: -0.03em;
	text-decoration: none;
	transition: transform 180ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-logo span {
	color: var(--accent);
	display: inline-block;
	transition: transform 180ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-logo:hover span {
	transform: scale(1.15);
}

.gai-user {
	display: flex;
	align-items: center;
	gap: 12px;
	color: var(--muted);
	font-size: 14px;
}

.gai-avatar {
	display: grid;
	width: 34px;
	height: 34px;
	place-items: center;
	border-radius: 50%;
	background: var(--accent);
	color: var(--paper);
	font-weight: 700;
}

.gai-greeting,
.course-section,
.live-section {
	max-width: 1100px;
	margin: 0 auto;
}

.gai-greeting {
	display: flex;
	align-items: flex-start;
	gap: 48px;
	padding: 80px 40px 48px;
}

.gai-greeting-copy {
	flex: 1;
}

.eyebrow {
	display: flex;
	align-items: center;
	gap: 10px;
	color: var(--muted);
	font-family: 'JetBrains Mono', monospace;
	font-size: 11px;
	letter-spacing: 0.14em;
	line-height: 1.5;
	text-transform: uppercase;
}

.eyebrow::before {
	content: '';
	width: 20px;
	height: 1px;
	background: color-mix(in oklab, var(--accent) 30%, var(--muted));
	opacity: 0.7;
}

.gai-greeting h1 {
	margin: 22px 0 0;
	max-width: 760px;
	font-size: clamp(38px, 5vw, 64px);
	font-weight: 700;
	letter-spacing: -0.03em;
	line-height: 1.1;
}

.gai-greeting h1 span,
.gai-greeting h1 em {
	display: block;
}

.gai-greeting h1 em {
	color: var(--accent);
	font-style: normal;
	animation: accent-arrive 900ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

.gai-greeting p {
	max-width: 560px;
	margin: 22px 0 0;
	color: var(--muted);
	font-size: 16px;
	line-height: 1.65;
}

.streak-card {
	position: relative;
	flex: 0 0 300px;
	overflow: hidden;
	border: 1.5px solid var(--border);
	border-radius: var(--r);
	background: var(--paper);
	padding: 24px;
}

.streak-card::before {
	content: '';
	position: absolute;
	inset: 0;
	background: radial-gradient(ellipse 120% 80% at 110% -10%, var(--accent-glow), transparent 60%);
	pointer-events: none;
}

.streak-top,
.streak-stats,
.dot-grid {
	position: relative;
}

.streak-top {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 16px;
}

.mono-label {
	color: var(--muted);
	font-family: 'JetBrains Mono', monospace;
	font-size: 10px;
	letter-spacing: 0.1em;
	text-transform: uppercase;
}

.streak-count {
	margin-top: 8px;
	color: var(--accent);
	font-size: 64px;
	font-weight: 700;
	letter-spacing: -0.04em;
	line-height: 0.95;
}

.streak-count span {
	margin-left: 4px;
	color: var(--muted);
	font-family: 'JetBrains Mono', monospace;
	font-size: 13px;
	font-weight: 400;
	letter-spacing: 0.12em;
	text-transform: uppercase;
}

.flame {
	width: 28px;
	height: 28px;
	fill: var(--accent);
	opacity: 0.9;
	animation: flame-pulse 2s ease-in-out infinite;
}

.flame-core {
	fill: oklch(0.95 0.12 60);
	opacity: 0.8;
}

.dot-grid {
	display: grid;
	grid-template-columns: repeat(14, 1fr);
	gap: 4px;
	margin-top: 24px;
}

.activity-dot {
	aspect-ratio: 1;
	border-radius: 3px;
	background: var(--border);
	opacity: 0;
	transform: scale(0.5);
	animation: dot-arrive 360ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
	animation-delay: var(--dot-d);
	transition: transform 0.2s ease;
}

.activity-dot:hover {
	transform: scale(1.3);
}

.activity-dot.active-dim {
	background: var(--accent-dim);
}

.activity-dot.active,
.activity-dot.today {
	background: var(--accent);
}

.activity-dot.today {
	box-shadow:
		0 0 0 2px var(--paper),
		0 0 0 3px var(--accent);
}

.activity-dot.today:hover {
	box-shadow:
		0 0 0 2px var(--paper),
		0 0 0 4px var(--accent);
}

.streak-stats {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16px;
	margin-top: 24px;
	padding-top: 18px;
	border-top: 1px solid var(--border);
}

.streak-stats strong {
	display: block;
	margin-top: 6px;
	font-size: 20px;
	font-weight: 700;
}

.course-section,
.live-section {
	padding: 0 40px 48px;
}

.section-title {
	margin-bottom: 18px;
}

.section-title h2 {
	margin: 8px 0 0;
	font-size: 24px;
	font-weight: 700;
	letter-spacing: -0.02em;
}

.course-row {
	position: relative;
	display: grid;
	grid-template-columns: 280px 1fr auto;
	gap: 28px;
	align-items: center;
	min-height: 190px;
	padding: 28px 28px 28px 0;
	border-bottom: 1px solid var(--border);
	color: var(--ink);
	text-decoration: none;
	transition:
		border-color 300ms cubic-bezier(0.16, 1, 0.3, 1),
		padding-left 300ms cubic-bezier(0.16, 1, 0.3, 1);
}

.course-row::before {
	content: '';
	position: absolute;
	inset: 0 -18px 0 -18px;
	z-index: 0;
	border-left: 1px solid transparent;
	border-radius: var(--r);
	background: var(--surface);
	opacity: 0;
	transition:
		opacity 300ms cubic-bezier(0.16, 1, 0.3, 1),
		border-color 300ms cubic-bezier(0.16, 1, 0.3, 1);
}

.course-row:hover {
	border-bottom-color: transparent;
	padding-left: 12px;
}

.course-row:hover::before {
	border-left-color: var(--accent);
	opacity: 1;
}

.course-art,
.course-copy,
.course-arrow {
	position: relative;
	z-index: 1;
}

.course-art {
	aspect-ratio: 16 / 9;
	overflow: hidden;
	border-radius: var(--r);
	transform: translateY(0);
	transition: transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
}

.course-row:hover .course-art {
	transform: translateY(-4px);
}

.mesh-warm {
	background:
		radial-gradient(ellipse 70% 90% at 30% 40%, oklch(0.78 0.14 18) 0%, transparent 70%),
		radial-gradient(ellipse 60% 80% at 75% 60%, oklch(0.82 0.1 55) 0%, transparent 65%),
		radial-gradient(ellipse 80% 60% at 55% 80%, oklch(0.74 0.16 340) 0%, transparent 70%);
}

.mesh-cool {
	background:
		radial-gradient(ellipse 70% 90% at 30% 40%, oklch(0.72 0.18 240) 0%, transparent 70%),
		radial-gradient(ellipse 60% 80% at 75% 60%, oklch(0.78 0.12 200) 0%, transparent 65%),
		radial-gradient(ellipse 80% 60% at 55% 80%, oklch(0.8 0.14 280) 0%, transparent 70%);
}

.mesh-green {
	background:
		radial-gradient(ellipse 70% 90% at 30% 40%, oklch(0.7 0.14 155) 0%, transparent 70%),
		radial-gradient(ellipse 60% 80% at 75% 60%, oklch(0.76 0.1 190) 0%, transparent 65%),
		radial-gradient(ellipse 80% 60% at 55% 80%, oklch(0.74 0.16 120) 0%, transparent 70%);
}

.course-badge {
	position: absolute;
	top: 12px;
	left: 12px;
	border-radius: 99px;
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(12px);
	font-family: 'JetBrains Mono', monospace;
	font-size: 10px;
	letter-spacing: 0.12em;
	padding: 5px 9px;
	text-transform: uppercase;
}

.gai-dashboard[data-dark='true'] .course-badge {
	background: rgba(0, 0, 0, 0.65);
	color: #fff;
}

.badge-warm {
	color: #c04010;
}

.badge-cool {
	color: #1a4db5;
}

.badge-green {
	color: #007a52;
}

.course-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	margin-bottom: 12px;
}

.course-tags span {
	border: 1px solid var(--border);
	border-radius: 99px;
	color: var(--muted);
	font-family: 'JetBrains Mono', monospace;
	font-size: 11px;
	letter-spacing: 0.12em;
	padding: 4px 10px;
	text-transform: uppercase;
}

.course-tags .tag-warm {
	border-color: #c04010;
	color: #c04010;
}

.course-tags .tag-cool {
	border-color: #1a4db5;
	color: #1a4db5;
}

.course-tags .tag-green {
	border-color: #007a52;
	color: #007a52;
}

.course-copy h3 {
	margin: 0;
	font-size: 22px;
	font-weight: 700;
	letter-spacing: -0.02em;
	line-height: 1.18;
}

.course-copy p {
	max-width: 560px;
	margin: 10px 0 0;
	color: var(--muted);
	font-size: 14px;
	line-height: 1.6;
}

.course-arrow {
	color: var(--accent);
	font-family: 'JetBrains Mono', monospace;
	font-size: 24px;
	opacity: 0;
	transform: translateX(0);
	transition:
		opacity 350ms cubic-bezier(0.16, 1, 0.3, 1),
		transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
}

.course-row:hover .course-arrow {
	opacity: 1;
	transform: translateX(4px);
}

.mini-grid {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: var(--gap);
}

.mini-panel {
	border: 1px solid var(--border);
	border-radius: var(--r);
	background: var(--surface);
	padding: 20px;
}

.mini-panel strong {
	display: block;
	margin-top: 8px;
	font-size: 34px;
	letter-spacing: -0.03em;
	line-height: 1;
}

.mini-panel p {
	margin: 12px 0 0;
	color: var(--muted);
	font-size: 14px;
	line-height: 1.55;
}

.rv {
	opacity: 0;
	transform: translateY(16px);
	transition:
		opacity 0.75s cubic-bezier(0.16, 1, 0.3, 1),
		transform 0.75s cubic-bezier(0.16, 1, 0.3, 1);
	transition-delay: var(--rv-d, 0ms);
}

.rv.in {
	opacity: 1;
	transform: none;
}

.gai-dashboard[data-anim='low'] .rv {
	transition-duration: 450ms;
}

.gai-dashboard[data-anim='off'] .rv,
.gai-dashboard[data-anim='off'] .activity-dot,
.gai-dashboard[data-anim='off'] .flame,
.gai-dashboard[data-anim='off'] .gai-greeting h1 em {
	animation: none;
	opacity: 1;
	transform: none;
	transition: none;
}

.cursor-blob {
	position: fixed;
	top: 0;
	left: 0;
	z-index: 9999;
	width: 28px;
	height: 28px;
	border-radius: 50%;
	background: var(--accent);
	mix-blend-mode: screen;
	opacity: 0;
	pointer-events: none;
	transition: opacity 160ms ease;
}

.cursor-blob.visible {
	opacity: 0.65;
}

.gai-dashboard[data-dark='true'] .cursor-blob.visible {
	opacity: 0.8;
}

.gai-dashboard[data-anim='off'] .cursor-blob {
	display: none;
}

@keyframes accent-arrive {
	from {
		color: var(--ink);
	}
	to {
		color: var(--accent);
	}
}

@keyframes flame-pulse {
	0%,
	100% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.08);
	}
}

@keyframes dot-arrive {
	to {
		opacity: 1;
		transform: scale(1);
	}
}

@media (max-width: 820px) {
	.gai-header-inner {
		padding: 16px 20px;
	}

	.gai-greeting {
		flex-direction: column;
		gap: 32px;
		padding: 56px 20px 40px;
	}

	.streak-card {
		flex: unset;
		width: 100%;
	}

	.course-section,
	.live-section {
		padding: 0 20px 40px;
	}

	.course-row {
		grid-template-columns: 1fr;
		gap: 16px;
		padding: 20px 0;
	}

	.course-row:hover {
		padding-left: 0;
	}

	.course-arrow {
		display: none;
	}

	.mini-grid {
		grid-template-columns: 1fr;
	}
}
</style>
