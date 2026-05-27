<template>
	<div class="gai-dashboard">

		<!-- Stat cards -->
		<div class="gai-stats gai-rise" style="--delay: 0ms">
			<div class="gai-stat-card" v-for="(stat, i) in stats" :key="i">
				<div class="gai-stat-watermark">
					<component :is="stat.icon" class="size-16 stroke-1" />
				</div>
				<div class="gai-stat-label">{{ __(stat.title) }}</div>
				<div class="gai-stat-value">
					<Star v-if="stat.isStar" class="size-5 text-transparent fill-amber-500 mb-1" />
					{{ stat.value }}
				</div>
			</div>
		</div>

		<!-- Main grid -->
		<div class="gai-main-grid">

			<!-- Students table -->
			<div class="gai-block gai-rise" style="--delay: 80ms">
				<div class="gai-block-header">
					<div>
						<div class="gai-eyebrow"><span></span>{{ __('Enrolled') }}</div>
						<div class="gai-block-title">{{ __('Students') }}</div>
					</div>
					<div class="flex items-center gap-x-2">
						<FormControl
							v-model="searchFilter"
							:placeholder="__('Search by name')"
							type="text"
						/>
						<Button @click="showEnrollmentModal = true">
							<template #prefix>
								<Plus class="size-4 stroke-1.5" />
							</template>
							{{ __('Enroll') }}
						</Button>
					</div>
				</div>

				<div v-if="progressList.loading || progressList.data?.length" class="max-h-[63vh] overflow-y-auto">
					<ListView
						:columns="progressColumns"
						:rows="progressList.data"
						rowKey="name"
						:options="{ selectable: false, showTooltip: false }"
					>
						<ListHeader class="gai-table-header">
							<ListHeaderItem
								:item="item"
								v-for="item in progressColumns"
								:key="item.key"
							/>
						</ListHeader>
						<ListRows v-for="row in progressList.data">
							<ListRow
								:row="row"
								@click="() => { showProgressModal = true; currentStudent = row }"
								class="gai-table-row cursor-pointer"
							>
								<template #default="{ column, item }">
									<ListRowItem :item="row[column.key]" :align="column.align" class="w-full">
										<template #prefix>
											<div v-if="column.key == 'member_name'">
												<Avatar
													class="flex items-center"
													:image="row['member_image']"
													:label="item"
													size="sm"
												/>
											</div>
											<ProgressBar
												v-else-if="column.key == 'progress'"
												:progress="Math.ceil(row[column.key])"
												class="!mx-0 !me-4"
											/>
										</template>
										<div v-if="column.key == 'creation'">
											{{ dayjs(row[column.key]).format('DD MMM YYYY') }}
										</div>
										<div v-else-if="column.key == 'progress'" class="gai-progress-pct">
											{{ Math.ceil(row[column.key]) }}%
										</div>
										<div v-else>{{ row[column.key].toString() }}</div>
									</ListRowItem>
								</template>
							</ListRow>
						</ListRows>
					</ListView>
					<div v-if="progressList.data && progressList.hasNextPage" class="flex justify-center my-3">
						<Button @click="progressList.next()">{{ __('Load More') }}</Button>
					</div>
				</div>
			</div>

			<!-- Right column -->
			<div class="gai-sidebar">

				<!-- Progress Summary -->
				<div
					v-if="chartDetails.data?.average_progress > 0"
					class="gai-block gai-rise"
					style="--delay: 140ms"
				>
					<div class="gai-block-header gai-block-header--sm">
						<div class="gai-eyebrow"><span></span>{{ __('Distribution') }}</div>
						<div class="gai-block-title">{{ __('Progress Summary') }}</div>
					</div>
					<div class="gai-progress-summary">
						<div class="gai-dist-list">
							<div
								v-for="row in chartDetails.data?.progress_distribution"
								:key="row.name"
								class="gai-dist-row"
							>
								<span
									class="gai-dist-pill"
									:style="{ background: distColor(row.name) }"
								></span>
								<Tooltip :text="row.name.split('(')[1]?.replace(')', '')">
									<span class="gai-dist-label">{{ row.name.split('(')[0].trim() }}</span>
								</Tooltip>
								<span class="gai-dist-pct">
									{{ Math.round((row.value / course.data?.enrollments) * 100) }}%
								</span>
							</div>
						</div>
						<ECharts
							class="gai-donut"
							:options="{
								color: progressColors,
								series: [{
									type: 'pie',
									radius: ['52%', '72%'],
									center: ['50%', '50%'],
									label: { show: false },
									labelLine: { show: false },
									emphasis: { label: { show: false }, scale: false },
									data: chartDetails.data?.progress_distribution || [],
								}],
							}"
						/>
					</div>
				</div>

				<!-- Lesson Completion -->
				<div
					v-if="lessonProgress.data?.length"
					class="gai-block gai-rise"
					style="--delay: 200ms"
				>
					<div class="gai-block-header gai-block-header--sm">
						<div>
							<div class="gai-eyebrow"><span></span>{{ __('Per Lesson') }}</div>
							<div class="gai-block-title">{{ __('Lesson Completion') }}</div>
						</div>
						<Select
							:options="lessonProgressSortingOptions"
							@update:modelValue="(value: string) => updateLessonProgress(value)"
							:placeholder="__('Sort by')"
							class="!w-32"
						/>
					</div>
					<div class="gai-lesson-list">
						<div
							v-for="progress in lessonProgress.data"
							:key="progress.title"
							class="gai-lesson-row"
						>
							<span class="gai-lesson-idx">
								{{ progress.chapter_idx }}.{{ progress.idx }}
							</span>
							<span class="gai-lesson-name">{{ progress.title }}</span>
							<span
								class="gai-lesson-pct"
								:class="completionClass(progress.completion_count, course.data?.enrollments)"
							>
								{{ Math.ceil((progress.completion_count / course.data?.enrollments) * 100) }}%
							</span>
						</div>
					</div>
				</div>

			</div>
		</div>
	</div>

	<CourseEnrollmentModal
		v-if="showEnrollmentModal"
		v-model="showEnrollmentModal"
		:course="course"
		:students="progressList"
	/>
	<StudentCourseProgress
		v-if="showProgressModal"
		v-model="showProgressModal"
		:course="course"
		:student="currentStudent"
		:lessons="lessonProgress"
	/>
</template>

<script setup lang="ts">
import {
	Avatar,
	Button,
	createListResource,
	createResource,
	ECharts,
	FormControl,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	Select,
	Tooltip,
} from 'frappe-ui'
import { computed, inject, ref, watch } from 'vue'
import type dayjsType from 'dayjs'
import { BookOpen, GraduationCap, Plus, Star, Users } from 'lucide-vue-next'
import { formatAmount } from '@/utils'
import colors from '@/utils/frappe-ui-colors.json'
import CourseEnrollmentModal from '@/pages/Courses/CourseEnrollmentModal.vue'
import NumberChartGraph from '@/components/NumberChartGraph.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import StudentCourseProgress from '@/pages/Courses/StudentCourseProgress.vue'

const props = defineProps<{ course: any }>()

const dayjs = inject<typeof dayjsType>('$dayjs')!
const showEnrollmentModal = ref(false)
const searchFilter = ref<string | null>(null)
const showProgressModal = ref(false)
const currentStudent = ref<any>(null)
const theme = ref<'darkMode' | 'lightMode'>(
	localStorage.getItem('theme') == 'dark' ? 'darkMode' : 'lightMode'
)

type Filters = { course: string | undefined; member_name?: string[] }

const chartDetails = createResource({
	url: 'lms.lms.api.get_course_progress_distribution',
	makeParams() { return { course: props.course.data?.name } },
	auto: true,
})

const progressList = createListResource({
	doctype: 'LMS Enrollment',
	filters: { course: props.course.data?.name },
	fields: ['name', 'member', 'member_name', 'member_image', 'member_username', 'progress', 'creation'],
	pageLength: 100,
	auto: true,
	cache: ['courseProgress', props.course.data?.name],
})

const lessonProgress = createResource({
	url: 'lms.lms.api.get_lesson_completion_stats',
	params: { course: props.course.data?.name },
	auto: true,
})

const updateLessonProgress = (value: string) => {
	if (value == 'completion_rate') {
		lessonProgress.data?.sort((a: any, b: any) => {
			return (b.completion_count / (props.course.data?.enrollments || 1)) -
			       (a.completion_count / (props.course.data?.enrollments || 1))
		})
	} else if (value == 'index') {
		lessonProgress.data?.sort((a: any, b: any) => a.chapter_idx - b.chapter_idx || a.idx - b.idx)
	}
}

watch([searchFilter], () => {
	let filters: Filters = { course: props.course.data?.name }
	if (searchFilter.value) filters.member_name = ['like', `%${searchFilter.value}%`]
	progressList.update({ filters })
	progressList.reload()
})

const averageCompletionRate = computed(() => Math.ceil(chartDetails.data?.average_progress) || 0)

const stats = computed(() => [
	{ title: 'Enrolled', value: formatAmount(props.course.data?.enrollments), icon: Users },
	{ title: 'Avg Completion', value: averageCompletionRate.value + '%', icon: GraduationCap },
	{ title: 'Average Rating', value: props.course.data?.rating || 5, icon: Star, isStar: true },
	{ title: 'Lessons', value: props.course.data?.lessons, icon: BookOpen },
])

const progressColors = computed(() => [
	colors[theme.value]['red'][400],
	colors[theme.value]['amber'][400],
	colors[theme.value]['blue'][400],
	colors[theme.value]['green'][400],
])

const distColor = (name: string) => {
	const t = theme.value
	if (name.startsWith('Just')) return colors[t]['red'][400]
	if (name.startsWith('In'))   return colors[t]['amber'][400]
	if (name.startsWith('Adv'))  return colors[t]['blue'][400]
	return colors[t]['green'][400]
}

const completionClass = (count: number, total: number) => {
	const pct = Math.ceil((count / total) * 100)
	if (pct >= 75) return 'gai-pct--high'
	if (pct >= 40) return 'gai-pct--mid'
	return 'gai-pct--low'
}

const progressColumns = computed(() => [
	{ label: __('Name'),       key: 'member_name', width: '40%' },
	{ label: __('Progress'),   key: 'progress',    width: '30%' },
	{ label: __('Enrolled On'),key: 'creation',    align: 'right' },
])

const lessonProgressSortingOptions = [
	{ label: __('Lesson Index'),    value: 'index',           onClick() { updateLessonProgress('index') } },
	{ label: __('Completion Rate'), value: 'completion_rate', onClick() { updateLessonProgress('completion_rate') } },
]
</script>

<style scoped>
/* ── Page wrapper ───────────────────────────────────────────── */
.gai-dashboard {
	padding: 1.75rem 1.5rem 3rem;
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
}

/* ── Stat cards ─────────────────────────────────────────────── */
.gai-stats {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 1rem;
}

.gai-stat-card {
	position: relative;
	overflow: hidden;
	padding: 1.1rem 1.25rem 1.25rem;
	border: 1.5px solid rgb(var(--outline-gray-2));
	border-left: 2.5px solid #ee6708;
	border-radius: 8px;
	background: rgb(var(--surface-cards));
	transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
	            box-shadow 0.2s ease,
	            border-color 0.2s ease;
}

.gai-stat-card:hover {
	transform: translateY(-2px);
	box-shadow: 0 0 0 3px color-mix(in oklab, #ee6708 8%, transparent),
	            0 4px 16px rgb(var(--brand-shadow-rgb) / 0.06);
	border-color: color-mix(in oklab, #ee6708 50%, rgb(var(--outline-gray-2)));
}

.gai-stat-watermark {
	position: absolute;
	bottom: -0.5rem;
	right: -0.5rem;
	color: rgb(var(--text-ink-gray-9));
	opacity: 0.18;
	pointer-events: none;
}

.gai-stat-label {
	font-size: 0.68rem;
	font-family: 'JetBrains Mono', monospace;
	font-weight: 500;
	letter-spacing: 0.1em;
	text-transform: uppercase;
	color: rgb(var(--text-ink-gray-5));
	margin-bottom: 0.6rem;
}

.gai-stat-value {
	display: flex;
	align-items: center;
	gap: 0.4rem;
	font-size: 2rem;
	font-weight: 700;
	letter-spacing: -0.03em;
	color: rgb(var(--text-ink-gray-9));
	line-height: 1;
}

/* ── Main grid ──────────────────────────────────────────────── */
.gai-main-grid {
	display: grid;
	grid-template-columns: 2fr 1fr;
	gap: 1.25rem;
	align-items: start;
}

.gai-sidebar {
	display: flex;
	flex-direction: column;
	gap: 1.25rem;
}

/* ── Generic block ──────────────────────────────────────────── */
.gai-block {
	border: 1.5px solid rgb(var(--outline-gray-2));
	border-radius: 8px;
	background: rgb(var(--surface-cards));
	overflow: hidden;
}

.gai-block-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	padding: 1rem 1.25rem;
	border-bottom: 1px solid rgb(var(--outline-gray-1));
	background: rgb(var(--surface-gray-1));
}

.gai-block-header--sm {
	padding: 0.9rem 1.1rem;
}

.gai-eyebrow {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	font-size: 0.65rem;
	font-family: 'JetBrains Mono', monospace;
	font-weight: 600;
	letter-spacing: 0.14em;
	text-transform: uppercase;
	color: rgb(var(--text-ink-gray-4));
	margin-bottom: 0.2rem;
}

.gai-eyebrow span {
	width: 0.85rem;
	height: 1px;
	background: color-mix(in oklab, #ee6708 50%, transparent);
	flex-shrink: 0;
}

.gai-block-title {
	font-size: 0.95rem;
	font-weight: 600;
	color: rgb(var(--text-ink-gray-9));
	letter-spacing: -0.01em;
}

/* ── Table ──────────────────────────────────────────────────── */
.gai-table-header {
	background: rgb(var(--surface-gray-1));
	border-bottom: 1px solid rgb(var(--outline-gray-2));
	border-radius: 0 !important;
	padding: 0.6rem 1rem;
	font-family: 'JetBrains Mono', monospace;
	font-size: 0.7rem;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: rgb(var(--text-ink-gray-5));
}

:deep(.gai-table-row) {
	border-bottom: 1px solid rgb(var(--outline-gray-1));
	transition: background 0.15s ease;
}

:deep(.gai-table-row:hover) {
	background: rgb(var(--surface-gray-1));
}

:deep(.gai-table-row:last-child) {
	border-bottom: none;
}

.gai-progress-pct {
	font-size: 0.75rem;
	font-family: 'JetBrains Mono', monospace;
	color: rgb(var(--text-ink-gray-5));
}

/* ── Progress summary ───────────────────────────────────────── */
.gai-progress-summary {
	display: grid;
	grid-template-columns: 1fr auto;
	align-items: center;
	gap: 1rem;
	padding: 1rem 1.1rem;
}

.gai-dist-list {
	display: flex;
	flex-direction: column;
	gap: 0.65rem;
}

.gai-dist-row {
	display: flex;
	align-items: center;
	gap: 0.5rem;
}

.gai-dist-pill {
	width: 0.5rem;
	height: 0.5rem;
	border-radius: 99px;
	flex-shrink: 0;
}

.gai-dist-label {
	font-size: 0.8rem;
	color: rgb(var(--text-ink-gray-7));
	flex: 1;
}

.gai-dist-pct {
	font-size: 0.75rem;
	font-family: 'JetBrains Mono', monospace;
	color: rgb(var(--text-ink-gray-5));
}

.gai-donut {
	width: 6rem;
	height: 6rem;
}

/* ── Lesson completion ──────────────────────────────────────── */
.gai-lesson-list {
	padding: 0.25rem 0;
	max-height: 40vh;
	overflow-y: auto;
}

.gai-lesson-row {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 0.55rem 1.1rem;
	border-bottom: 1px solid rgb(var(--outline-gray-1));
	transition: background 0.15s ease;
}

.gai-lesson-row:last-child {
	border-bottom: none;
}

.gai-lesson-row:hover {
	background: rgb(var(--surface-gray-1));
}

.gai-lesson-idx {
	font-size: 0.7rem;
	font-family: 'JetBrains Mono', monospace;
	color: rgb(var(--text-ink-gray-4));
	background: rgb(var(--surface-gray-1));
	border: 1px solid rgb(var(--outline-gray-2));
	border-radius: 4px;
	padding: 0.1rem 0.4rem;
	flex-shrink: 0;
}

.gai-lesson-name {
	font-size: 0.82rem;
	color: rgb(var(--text-ink-gray-7));
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.gai-lesson-pct {
	font-size: 0.75rem;
	font-family: 'JetBrains Mono', monospace;
	font-weight: 600;
	flex-shrink: 0;
}

.gai-pct--high { color: #16a34a; }
.gai-pct--mid  { color: #d97706; }
.gai-pct--low  { color: rgb(var(--text-ink-gray-4)); }
</style>
