<template>
	<div v-if="isAdmin && currentTab === 'instructor'" class="w-full px-5 pt-5 pb-10">
		<div class="space-y-2">
			<div class="flex items-center justify-between">
				<div class="text-xl font-bold text-ink-gray-9">
					{{ __('Hey') }}, {{ user.data?.full_name }}
				</div>
			</div>

			<div class="text-lg text-ink-gray-6 leading-6">
				{{ subtitle }}
			</div>
		</div>

		<AdminHome :liveClasses="adminLiveClasses" :evals="adminEvals" />
	</div>

	<div v-else-if="currentTab === 'student'" class="gai-student-home">
		<section class="gai-hero gai-rise">
			<div class="gai-hero-copy">
				<div class="gai-eyebrow">
					<span></span>
					{{ dayjs().format('dddd, MMMM D') }}
				</div>
				<h1>
					<span>{{ __('Good morning,') }}</span>
					<em>{{ firstName }}</em>
				</h1>
				<p>{{ subtitle }}</p>
			</div>

			<button
				type="button"
				class="gai-streak"
				@click="showStreakModal = true"
			>
				<div class="gai-streak-top">
					<div>
						<div class="gai-streak-label">{{ __('Current streak') }}</div>
						<div class="gai-streak-value">
							{{ streakInfo.data?.current_streak || 0 }}
							<span>{{ __('days') }}</span>
						</div>
					</div>
					<div class="gai-flame" aria-hidden="true">
						<svg viewBox="0 0 24 24" fill="none">
							<path
								d="M12.7 2.4c.7 2.7-.5 4.5-1.9 6.1-1.3 1.5-2.8 3-2.8 5.2 0 2.1 1.6 3.9 4 3.9 2.5 0 4.3-1.7 4.3-4.4 0-1.9-.8-3.6-2.2-5.1 3.8 1.8 6 4.8 6 8.1 0 4-3.4 6.9-8.1 6.9S4 20.2 4 16.1c0-2.9 1.5-5.2 3.4-7.2 1.7-1.8 3.7-3.6 5.3-6.5Z"
								fill="currentColor"
							/>
							<path
								d="M13 20.1c1.7-.5 2.6-1.7 2.6-3.1 0-1.5-.8-2.8-2.4-4.1.1 1.7-.7 2.7-1.5 3.5-.8.8-1.5 1.5-1.5 2.4 0 .9.7 1.5 1.8 1.5.4 0 .7-.1 1-.2Z"
								fill="rgb(255 237 213)"
							/>
						</svg>
					</div>
				</div>

				<div class="gai-dot-grid" aria-hidden="true">
					<span
						v-for="dot in 28"
						:key="dot"
						:class="{
							active: dot <= Math.min(streakInfo.data?.current_streak || 0, 28),
							today: dot === Math.min(streakInfo.data?.current_streak || 0, 28),
						}"
					></span>
				</div>

				<div class="gai-streak-meta">
					<span>{{ __('Longest') }}</span>
					<strong>{{ streakInfo.data?.longest_streak || 0 }}</strong>
				</div>
			</button>
		</section>

		<StudentHome :myLiveClasses="myLiveClasses" />
	</div>

	<Streak v-model="showStreakModal" :streakInfo="streakInfo" />
</template>
<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import { call, createResource, usePageMeta } from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { useRouter } from 'vue-router'
import StudentHome from '@/pages/Home/StudentHome.vue'
import AdminHome from '@/pages/Home/AdminHome.vue'
import Streak from '@/pages/Home/Streak.vue'

const user = inject<any>('$user')
const dayjs = inject<any>('$dayjs')
const { brand } = sessionStore()
const router = useRouter()
const evalCount = ref(0)
const currentTab = ref<'student' | 'instructor'>('student')
const showStreakModal = ref(false)

const fetchEvalCount = () => {
	call('frappe.client.get_count', {
		doctype: 'LMS Certificate Request',
		filters: {
			member: user?.data?.name,
			status: 'Upcoming',
			date: ['>=', dayjs().format('YYYY-MM-DD')],
		},
	}).then((data: any) => {
		evalCount.value = data
	})
}

const isAdmin = computed(() => {
	return (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	)
})

const firstName = computed(() => {
	const displayName = user.data?.full_name || user.data?.name || __('Student')
	return String(displayName).split(' ')[0]
})

const isPersonaCaptured = async () => {
	let persona = await call('frappe.client.get_single_value', {
		doctype: 'LMS Settings',
		field: 'persona_captured',
	})
	return persona
}

const identifyUserPersona = async () => {
	if (user.data?.is_system_manager && !user.data?.developer_mode) {
		let personaCaptured = await isPersonaCaptured()
		if (personaCaptured) return
		let courseCount = await call('frappe.client.get_count', {
			doctype: 'LMS Course',
			filters: {
				title: ['not like', '%A guide to Frappe Learning%'],
			},
		})
		if (!courseCount) {
			router.push({ name: 'PersonaForm' })
		}
	}
}

onMounted(() => {
	identifyUserPersona()
	if (isAdmin.value) {
		currentTab.value = 'instructor'
	} else {
		currentTab.value = 'student'
		fetchEvalCount()
	}
})

const myLiveClasses = createResource({
	url: 'lms.lms.api.get_my_live_classes',
	auto: !isAdmin.value ? true : false,
})

const adminLiveClasses = createResource({
	url: 'lms.lms.api.get_admin_live_classes',
	auto: isAdmin.value ? true : false,
})

const adminEvals = createResource({
	url: 'lms.lms.api.get_admin_evals',
	auto: isAdmin.value ? true : false,
})

const streakInfo = createResource({
	url: 'lms.lms.api.get_streak_info',
	auto: true,
})

const subtitle = computed(() => {
	if (isAdmin.value) {
		let liveClassSuffix =
			adminLiveClasses.data?.length > 1 ? __('live classes') : __('live class')
		let evalSuffix =
			adminEvals.data?.length > 1 ? __('evaluations') : __('evaluation')
		if (adminLiveClasses.data?.length > 0 && adminEvals.data?.length > 0) {
			return __('You have {0} upcoming {1} and {2} {3} scheduled.').format(
				adminLiveClasses.data.length,
				liveClassSuffix,
				adminEvals.data.length,
				evalSuffix
			)
		} else if (adminLiveClasses.data?.length > 0) {
			return __('You have {0} upcoming {1}.').format(
				adminLiveClasses.data.length,
				liveClassSuffix
			)
		} else if (adminEvals.data?.length > 0) {
			return __('You have {0} {1} scheduled.').format(
				adminEvals.data.length,
				evalSuffix
			)
		}
		return __('Manage your courses and batches at a glance')
	} else {
		let liveClassSuffix =
			myLiveClasses.data?.length > 1 ? __('live classes') : __('live class')
		let evalSuffix = evalCount.value > 1 ? __('evaluations') : __('evaluation')
		if (myLiveClasses.data?.length > 0 && evalCount.value > 0) {
			return __('You have {0} upcoming {1} and {2} {3} scheduled.').format(
				myLiveClasses.data.length,
				liveClassSuffix,
				evalCount.value,
				evalSuffix
			)
		} else if (myLiveClasses.data?.length > 0) {
			return __('You have {0} upcoming {1}.').format(
				myLiveClasses.data.length,
				liveClassSuffix
			)
		} else if (evalCount.value > 0) {
			return __('You have {0} {1} scheduled.').format(
				evalCount.value,
				evalSuffix
			)
		}
		return __('Resume where you left off')
	}
})

usePageMeta(() => {
	return {
		title: __('Home'),
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.gai-student-home {
	--gai-accent: #6B3FA0;
	--gai-accent-soft: color-mix(in oklab, var(--gai-accent) 14%, transparent);
	--gai-paper: rgb(var(--surface-white));
	--gai-surface: rgb(var(--surface-gray-1));
	--gai-border: rgb(var(--outline-gray-2));
	--gai-ink: rgb(var(--text-ink-gray-9));
	--gai-muted: rgb(var(--text-ink-gray-6));
	position: relative;
	min-height: 100%;
	padding: 2rem 1.25rem 3rem;
	color: var(--gai-ink);
	background:
		radial-gradient(circle at 12% 4%, var(--gai-accent-soft), transparent 28rem),
		linear-gradient(180deg, color-mix(in oklab, var(--gai-surface) 55%, transparent), transparent 18rem);
}

.gai-hero {
	display: flex;
	align-items: stretch;
	justify-content: space-between;
	gap: 2rem;
	max-width: 72rem;
	margin: 0 auto 2rem;
}

.gai-hero-copy {
	position: relative;
	flex: 1;
	overflow: hidden;
	padding: clamp(2rem, 5vw, 4rem);
	border: 1px solid var(--gai-border);
	border-radius: 1.5rem;
	background:
		radial-gradient(circle at 85% 12%, var(--gai-accent-soft), transparent 20rem),
		var(--gai-paper);
	box-shadow: 0 24px 80px color-mix(in oklab, var(--gai-ink) 8%, transparent);
}

.gai-eyebrow {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	margin-bottom: 1.25rem;
	color: var(--gai-muted);
	font-size: 0.72rem;
	font-weight: 600;
	letter-spacing: 0.14em;
	text-transform: uppercase;
}

.gai-eyebrow span {
	width: 1.5rem;
	height: 1px;
	background: color-mix(in oklab, var(--gai-accent) 46%, transparent);
}

.gai-hero h1 {
	display: grid;
	gap: 0.15em;
	max-width: 46rem;
	margin: 0;
	font-size: clamp(2.5rem, 6vw, 4.85rem);
	font-weight: 800;
	letter-spacing: -0.055em;
	line-height: 0.98;
}

.gai-hero h1 em {
	color: var(--gai-accent);
	font-style: normal;
}

.gai-hero p {
	max-width: 38rem;
	margin: 1.4rem 0 0;
	color: var(--gai-muted);
	font-size: 1.05rem;
	line-height: 1.7;
}

.gai-streak {
	position: relative;
	flex: 0 0 19rem;
	overflow: hidden;
	padding: 1.5rem;
	border: 1px solid var(--gai-border);
	border-radius: 1.5rem;
	color: var(--gai-ink);
	text-align: left;
	background:
		radial-gradient(ellipse 120% 90% at 110% -10%, color-mix(in oklab, var(--gai-accent) 20%, transparent), transparent 60%),
		var(--gai-paper);
	box-shadow: 0 24px 80px color-mix(in oklab, var(--gai-ink) 8%, transparent);
	transition:
		transform 360ms cubic-bezier(0.16, 1, 0.3, 1),
		border-color 360ms cubic-bezier(0.16, 1, 0.3, 1),
		box-shadow 360ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-streak:hover {
	transform: translateY(-5px);
	border-color: color-mix(in oklab, var(--gai-accent) 55%, var(--gai-border));
	box-shadow: 0 28px 90px color-mix(in oklab, var(--gai-accent) 18%, transparent);
}

.gai-streak-top {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 1rem;
}

.gai-streak-label,
.gai-streak-meta span {
	color: var(--gai-muted);
	font-size: 0.7rem;
	font-weight: 700;
	letter-spacing: 0.12em;
	text-transform: uppercase;
}

.gai-streak-value {
	margin-top: 0.75rem;
	color: var(--gai-accent);
	font-size: 4rem;
	font-weight: 800;
	letter-spacing: -0.06em;
	line-height: 1;
}

.gai-streak-value span {
	color: var(--gai-muted);
	font-size: 0.85rem;
	font-weight: 700;
	letter-spacing: 0.04em;
}

.gai-flame {
	display: grid;
	width: 2.75rem;
	height: 2.75rem;
	place-items: center;
	border-radius: 1rem;
	color: var(--gai-accent);
	background: color-mix(in oklab, var(--gai-accent) 12%, transparent);
	animation: gai-pulse 2.4s ease-in-out infinite;
}

.gai-flame svg {
	width: 1.7rem;
	height: 1.7rem;
}

.gai-dot-grid {
	display: grid;
	grid-template-columns: repeat(14, 1fr);
	gap: 0.28rem;
	margin: 1.75rem 0;
}

.gai-dot-grid span {
	aspect-ratio: 1;
	border-radius: 0.25rem;
	background: var(--gai-border);
	transition:
		transform 220ms ease,
		background 220ms ease,
		box-shadow 220ms ease;
}

.gai-dot-grid span.active {
	background: color-mix(in oklab, var(--gai-accent) 44%, var(--gai-border));
}

.gai-dot-grid span.today {
	background: var(--gai-accent);
	box-shadow: 0 0 0 2px var(--gai-paper), 0 0 0 3px var(--gai-accent);
}

.gai-dot-grid span:hover {
	transform: scale(1.28);
}

.gai-streak-meta {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding-top: 1rem;
	border-top: 1px solid var(--gai-border);
}

.gai-streak-meta strong {
	font-size: 1.25rem;
}

.gai-rise {
	animation: gai-rise 760ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes gai-rise {
	from {
		opacity: 0;
		transform: translateY(18px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@keyframes gai-pulse {
	0%,
	100% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.08);
	}
}

@media (max-width: 820px) {
	.gai-student-home {
		padding: 1rem 1rem 2rem;
	}

	.gai-hero {
		flex-direction: column;
		gap: 1rem;
	}

	.gai-streak {
		flex-basis: auto;
	}
}
</style>
