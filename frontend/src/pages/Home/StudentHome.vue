<template>
	<div class="gai-student-sections">
		<section class="gai-section gai-rise" style="--delay: 90ms">
			<UpcomingEvaluations :forHome="true" />
		</section>

		<section
			v-if="props.myLiveClasses.data?.length"
			class="gai-section gai-rise"
			style="--delay: 160ms"
		>
			<div class="gai-section-head">
				<div>
					<div class="gai-section-kicker">{{ __('Calendar') }}</div>
					<h2>{{ __('Upcoming Live Classes') }}</h2>
				</div>
			</div>

			<div class="gai-live-grid">
				<article
					v-for="cls in props.myLiveClasses.data"
					:key="cls.name || cls.title"
					class="gai-live-card"
				>
					<div class="gai-live-orb"></div>
					<div class="gai-live-content">
						<h3>{{ cls.title }}</h3>
						<p>{{ cls.description }}</p>

						<div class="gai-live-meta">
							<div>
								<Calendar class="w-4 h-4 stroke-1.5" />
								<span>{{ dayjs(cls.date).format('DD MMMM YYYY') }}</span>
							</div>
							<div>
								<Clock class="w-4 h-4 stroke-1.5" />
								<span>
									{{ formatTime(cls.time) }} -
									{{ dayjs(getClassEnd(cls)).format('HH:mm A') }}
								</span>
							</div>
						</div>

						<div v-if="canAccessClass(cls)" class="gai-live-actions">
							<a
								v-if="user.data?.is_moderator || user.data?.is_evaluator"
								:href="cls.start_url"
								target="_blank"
								class="gai-action"
								:class="cls.join_url ? 'w-full' : 'w-1/2'"
							>
								<Monitor class="h-4 w-4 stroke-1.5" />
								{{ __('Start') }}
							</a>
							<a
								:href="cls.join_url"
								target="_blank"
								class="gai-action gai-action-primary"
							>
								<Video class="h-4 w-4 stroke-1.5" />
								{{ __('Join') }}
							</a>
						</div>
						<Tooltip
							v-else-if="hasClassEnded(cls)"
							:text="__('This class has ended')"
							placement="right"
						>
							<div class="gai-ended">
								<Info class="w-4 h-4 stroke-1.5" />
								<span>{{ __('Ended') }}</span>
							</div>
						</Tooltip>
					</div>
				</article>
			</div>
		</section>

		<section
			v-if="myCourses.data?.length"
			class="gai-section gai-rise"
			style="--delay: 230ms"
		>
			<div class="gai-section-head">
				<div>
					<div class="gai-section-kicker">{{ __('Learning path') }}</div>
					<h2>
						{{
							myCourses.data[0].membership
								? __('My Courses')
								: __('Our Popular Courses')
						}}
					</h2>
				</div>
				<router-link :to="{ name: 'Courses' }" class="gai-see-all">
					<span>{{ __('See all') }}</span>
					<MoveRight class="size-3 stroke-1.5 rtl:rotate-180" />
				</router-link>
			</div>

			<div class="gai-course-grid">
				<router-link
					v-for="course in myCourses.data"
					:key="course.name"
					:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
					class="gai-card-link"
				>
					<CourseCard :course="course" />
				</router-link>
			</div>
		</section>

		<section
			v-if="myBatches.data?.length"
			class="gai-section gai-rise"
			style="--delay: 300ms"
		>
			<div class="gai-section-head">
				<div>
					<div class="gai-section-kicker">{{ __('Cohorts') }}</div>
					<h2>
						{{
							myBatches.data?.[0].students?.includes(user.data?.name)
								? __('My Batches')
								: __('Our Upcoming Batches')
						}}
					</h2>
				</div>
				<router-link :to="{ name: 'Batches' }" class="gai-see-all">
					<span>{{ __('See all') }}</span>
					<MoveRight class="size-3 stroke-1.5 rtl:rotate-180" />
				</router-link>
			</div>

			<div class="gai-batch-grid">
				<router-link
					v-for="batch in myBatches.data"
					:key="batch.name"
					:to="{ name: 'BatchDetail', params: { batchName: batch.name } }"
					class="gai-card-link"
				>
					<BatchCard :batch="batch" />
				</router-link>
			</div>
		</section>
	</div>
</template>
<script setup lang="ts">
import { inject } from 'vue'
import { createResource, Tooltip } from 'frappe-ui'
import { formatTime } from '@/utils'
import {
	Calendar,
	Clock,
	Info,
	Monitor,
	MoveRight,
	Video,
} from 'lucide-vue-next'
import CourseCard from '@/components/CourseCard.vue'
import BatchCard from '@/pages/Batches/components/BatchCard.vue'
import UpcomingEvaluations from '@/components/UpcomingEvaluations.vue'

const dayjs = inject<any>('$dayjs')
const user = inject<any>('$user')

const props = defineProps<{
	myLiveClasses: any
}>()

const myCourses = createResource({
	url: 'lms.lms.api.get_my_courses',
	auto: true,
})

const myBatches = createResource({
	url: 'lms.lms.api.get_my_batches',
	auto: true,
})

const getClassEnd = (cls: { date: string; time: string; duration: number }) => {
	const classStart = new Date(`${cls.date}T${cls.time}`)
	return new Date(classStart.getTime() + cls.duration * 60000)
}

const canAccessClass = (cls: {
	date: string
	time: string
	duration: number
}) => {
	if (cls.date < dayjs().format('YYYY-MM-DD')) return false
	if (cls.date > dayjs().format('YYYY-MM-DD')) return false
	if (hasClassEnded(cls)) return false
	return true
}

const hasClassEnded = (cls: {
	date: string
	time: string
	duration: number
}) => {
	const classEnd = getClassEnd(cls)
	const now = new Date()
	return now > classEnd
}
</script>

<style scoped>
.gai-student-sections {
	--gai-accent: #6B3FA0;
	--gai-paper: rgb(var(--surface-white));
	--gai-surface: rgb(var(--surface-gray-1));
	--gai-surface-strong: rgb(var(--surface-gray-2));
	--gai-border: rgb(var(--outline-gray-2));
	--gai-ink: rgb(var(--text-ink-gray-9));
	--gai-muted: rgb(var(--text-ink-gray-6));
	max-width: 72rem;
	margin: 0 auto;
}

.gai-section {
	position: relative;
	margin-top: 1.25rem;
}

.gai-section + .gai-section {
	margin-top: 2rem;
}

.gai-section-head {
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
	gap: 1rem;
	margin-bottom: 1rem;
}

.gai-section-kicker {
	margin-bottom: 0.35rem;
	color: var(--gai-muted);
	font-size: 0.68rem;
	font-weight: 700;
	letter-spacing: 0.14em;
	text-transform: uppercase;
}

.gai-section-head h2 {
	margin: 0;
	color: var(--gai-ink);
	font-size: clamp(1.35rem, 2vw, 1.85rem);
	font-weight: 800;
	letter-spacing: -0.035em;
}

.gai-see-all {
	display: inline-flex;
	align-items: center;
	gap: 0.35rem;
	padding: 0.45rem 0.7rem;
	border: 1px solid var(--gai-border);
	border-radius: 999px;
	color: var(--gai-muted);
	font-size: 0.78rem;
	font-weight: 700;
	background: var(--gai-paper);
	transition:
		color 260ms ease,
		border-color 260ms ease,
		transform 260ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-see-all:hover {
	transform: translateY(-2px);
	border-color: color-mix(in oklab, var(--gai-accent) 58%, var(--gai-border));
	color: var(--gai-accent);
}

.gai-live-grid {
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: 1rem;
}

.gai-live-card {
	position: relative;
	min-height: 17rem;
	overflow: hidden;
	border: 1px solid var(--gai-border);
	border-radius: 1.25rem;
	background:
		radial-gradient(circle at 85% 0%, color-mix(in oklab, var(--gai-accent) 16%, transparent), transparent 12rem),
		var(--gai-paper);
	box-shadow: 0 18px 55px color-mix(in oklab, var(--gai-ink) 7%, transparent);
	transition:
		transform 360ms cubic-bezier(0.16, 1, 0.3, 1),
		border-color 360ms cubic-bezier(0.16, 1, 0.3, 1),
		box-shadow 360ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-live-card:hover {
	transform: translateY(-6px);
	border-color: color-mix(in oklab, var(--gai-accent) 45%, var(--gai-border));
	box-shadow: 0 28px 70px color-mix(in oklab, var(--gai-accent) 14%, transparent);
}

.gai-live-orb {
	position: absolute;
	inset: auto -3rem -4rem auto;
	width: 9rem;
	height: 9rem;
	border-radius: 999px;
	background: color-mix(in oklab, var(--gai-accent) 16%, transparent);
	filter: blur(10px);
	transition: transform 420ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-live-card:hover .gai-live-orb {
	transform: translate(-1.5rem, -1.5rem) scale(1.2);
}

.gai-live-content {
	position: relative;
	z-index: 1;
	display: flex;
	min-height: 17rem;
	flex-direction: column;
	padding: 1rem;
}

.gai-live-card h3 {
	margin: 0 0 0.5rem;
	color: var(--gai-ink);
	font-size: 1rem;
	font-weight: 800;
	letter-spacing: -0.02em;
	line-height: 1.2;
}

.gai-live-card p {
	margin: 0 0 1rem;
	color: var(--gai-muted);
	font-size: 0.9rem;
	line-height: 1.55;
}

.gai-live-meta {
	display: grid;
	gap: 0.6rem;
	margin-top: auto;
	color: var(--gai-muted);
	font-size: 0.82rem;
}

.gai-live-meta div {
	display: flex;
	align-items: center;
	gap: 0.55rem;
}

.gai-live-actions {
	display: flex;
	gap: 0.5rem;
	margin-top: 1rem;
}

.gai-action {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	gap: 0.45rem;
	width: 100%;
	min-height: 2.25rem;
	padding: 0.45rem 0.75rem;
	border: 1px solid var(--gai-border);
	border-radius: 999px;
	color: var(--gai-ink);
	font-weight: 700;
	background: var(--gai-surface);
	transition:
		transform 260ms ease,
		background 260ms ease,
		border-color 260ms ease;
}

.gai-action:hover {
	transform: translateY(-2px);
	border-color: color-mix(in oklab, var(--gai-accent) 48%, var(--gai-border));
}

.gai-action-primary {
	border-color: var(--gai-accent);
	color: white;
	background: var(--gai-accent);
}

.gai-ended {
	display: inline-flex;
	align-items: center;
	gap: 0.45rem;
	width: fit-content;
	margin-top: 1rem;
	color: color-mix(in oklab, var(--gai-accent) 72%, var(--gai-ink));
	font-weight: 700;
}

.gai-course-grid {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 1rem;
}

.gai-batch-grid {
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: 1rem;
}

.gai-card-link {
	display: block;
	height: 100%;
	border-radius: 1.25rem;
	transition:
		transform 360ms cubic-bezier(0.16, 1, 0.3, 1),
		filter 360ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-card-link:hover {
	transform: translateY(-6px);
	filter: drop-shadow(0 18px 28px color-mix(in oklab, var(--gai-accent) 12%, transparent));
}

.gai-rise {
	animation: gai-section-rise 720ms cubic-bezier(0.16, 1, 0.3, 1) both;
	animation-delay: var(--delay, 0ms);
}

@keyframes gai-section-rise {
	from {
		opacity: 0;
		transform: translateY(18px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@media (max-width: 1024px) {
	.gai-live-grid,
	.gai-batch-grid {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}

	.gai-course-grid {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
}

@media (max-width: 680px) {
	.gai-section-head {
		align-items: flex-start;
		flex-direction: column;
	}

	.gai-live-grid,
	.gai-course-grid,
	.gai-batch-grid {
		grid-template-columns: 1fr;
	}
}
</style>
