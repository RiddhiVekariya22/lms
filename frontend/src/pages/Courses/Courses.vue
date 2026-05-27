<template>
	<header
		class="sticky flex items-center justify-between top-0 z-10 border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />

		<Dropdown
			placement="right"
			side="bottom"
			v-if="canCreateCourse()"
			:options="courseMenu"
		>
			<template v-slot="{ open }">
				<Button variant="solid">
					<template #prefix>
						<Plus class="h-4 w-4 stroke-1.5" />
					</template>
					{{ __('Create') }}
					<template #suffix>
						<ChevronDown
							:class="[
								'w-4 h-4 stroke-1.5 ms-1 transform transition-transform',
								open ? 'rotate-180' : '',
							]"
						/>
					</template>
				</Button>
			</template>
		</Dropdown>
	</header>
	<div class="gai-courses-page">
		<section class="gai-page-hero gai-rise">
			<div class="gai-eyebrow"><span></span>{{ __('Learning path') }}</div>
			<h1>{{ __('Courses') }}</h1>
			<p v-if="courseCount">
				{{ courseCount }} {{ __('courses available') }}
			</p>
		</section>

		<div class="gai-controls gai-rise" style="--delay: 60ms">
			<TabButtons :buttons="courseTabs" v-model="currentTab" class="w-fit" />
			<div class="gai-search-row">
				<FormControl
					v-model="title"
					:placeholder="__('Search')"
					type="text"
					@input="updateCourses()"
				/>
				<Select
					v-if="categories.length"
					v-model="currentCategory"
					:options="categories"
					:placeholder="__('Category')"
					@update:modelValue="updateCourses()"
				/>
				<Tooltip :text="__('Only show courses that offer a certificate')">
					<FormControl
						type="checkbox"
						v-model="certification"
						:label="__('Certification')"
						@change="updateCourses()"
					/>
				</Tooltip>
			</div>
		</div>

		<div v-if="courses.data?.length" class="gai-grid">
			<router-link
				v-for="(course, i) in courses.data"
				:key="course.name"
				:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
				class="gai-card-link gai-rise"
				:style="`--delay: ${80 + i * 45}ms`"
			>
				<CourseCard :course="course" />
			</router-link>
		</div>
		<EmptyState v-else-if="!courses.list.loading" type="Courses" />

		<div
			v-if="!courses.list.loading && courses.hasNextPage"
			class="gai-load-more gai-rise"
		>
			<Button @click="courses.next()">{{ __('Load More') }}</Button>
		</div>
	</div>
	<NewCourseModal
		v-if="showCourseModal"
		v-model="showCourseModal"
		:courses="courses"
	/>

	<CourseImportModal
		v-if="showCourseImportModal"
		v-model="showCourseImportModal"
	/>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	call,
	createListResource,
	Dropdown,
	FormControl,
	Select,
	TabButtons,
	Tooltip,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { ChevronDown, Plus } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { canCreateCourse } from '@/utils'
import CourseCard from '@/components/CourseCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useRouter } from 'vue-router'
import NewCourseModal from '@/pages/Courses/NewCourseModal.vue'
import CourseImportModal from '@/pages/Courses/CourseImportModal.vue'

const user = inject('$user')
const dayjs = inject('$dayjs')
const start = ref(0)
const pageLength = ref(30)
const categories = ref([
	{
		label: '',
		value: null,
	},
])
const currentCategory = ref(null)
const title = ref('')
const certification = ref(false)
const filters = ref({})
const currentTab = ref('live')
const { brand } = sessionStore()
const courseCount = ref(0)
const router = useRouter()
const showCourseModal = ref(false)
const showCourseImportModal = ref(false)

onMounted(() => {
	setFiltersFromQuery()
	updateCourses()
	getCourseCount()
})

const setFiltersFromQuery = () => {
	let queries = new URLSearchParams(location.search)
	title.value = queries.get('title') || ''
	currentCategory.value = queries.get('category') || null
	certification.value = queries.get('certification') || false
	if (queries.get('newCourse') == '1') {
		showCourseModal.value = true
	}
}

const courses = createListResource({
	doctype: 'LMS Course',
	url: 'lms.lms.utils.get_courses',
	cache: ['courses', user.data?.name],
	pageLength: pageLength.value,
	start: start.value,
})

const setCategories = (data) => {
	let allCategories = data.map((course) => course.category)
	allCategories = allCategories.filter(
		(category, index) => allCategories.indexOf(category) === index && category
	)
	if (categories.value.length <= allCategories.length) {
		updateCategories(data)
	}
}

const getCourseCount = () => {
	if (!user.data) return
	if (!user.data.is_moderator) return
	call('frappe.client.get_count', {
		doctype: 'LMS Course',
	}).then((data) => {
		courseCount.value = data
	})
}

const updateCourses = () => {
	updateFilters()
	courses.update({
		filters: filters.value,
	})
	courses.reload().then((data) => {
		setCategories(data)
	})
}

const updateFilters = () => {
	updateCategoryFilter()
	updateTitleFilter()
	updateCertificationFilter()
	updateTabFilter()
	updateStudentFilter()
	setQueryParams()
}

const updateCategoryFilter = () => {
	if (currentCategory.value) {
		filters.value['category'] = currentCategory.value
	} else {
		delete filters.value['category']
	}
}

const updateTitleFilter = () => {
	if (title.value) {
		filters.value['title'] = ['like', `%${title.value}%`]
	} else {
		delete filters.value['title']
	}
}

const updateCertificationFilter = () => {
	if (certification.value) {
		filters.value['certification'] = 1
	} else {
		delete filters.value['certification']
	}
}

const updateTabFilter = () => {
	delete filters.value['live']
	delete filters.value['created']
	delete filters.value['published_on']
	delete filters.value['upcoming']

	if (currentTab.value == 'enrolled' && user.data?.is_student) {
		filters.value['enrolled'] = 1
		delete filters.value['published']
	} else {
		delete filters.value['published']
		delete filters.value['enrolled']

		if (currentTab.value == 'live') {
			filters.value['published'] = 1
			filters.value['upcoming'] = 0
			filters.value['live'] = 1
		} else if (currentTab.value == 'upcoming') {
			filters.value['upcoming'] = 1
		} else if (currentTab.value == 'new') {
			filters.value['published'] = 1
			filters.value['published_on'] = [
				'>=',
				dayjs().add(-3, 'month').format('YYYY-MM-DD'),
			]
		} else if (currentTab.value == 'created') {
			filters.value['created'] = 1
		} else if (currentTab.value == 'unpublished') {
			filters.value['published'] = 0
		}
	}
}

const updateStudentFilter = () => {
	if (!user.data || (user.data?.is_student && currentTab.value != 'enrolled')) {
		filters.value['published'] = 1
	}
}

const setQueryParams = () => {
	let queries = new URLSearchParams(location.search)
	let filterKeys = {
		title: title.value,
		category: currentCategory.value,
		certification: certification.value,
	}

	Object.keys(filterKeys).forEach((key) => {
		if (filterKeys[key]) {
			queries.set(key, filterKeys[key])
		} else {
			queries.delete(key)
		}
	})

	let queryString = ''
	if (queries.toString()) {
		queryString = `?${queries.toString()}`
	}

	history.replaceState({}, '', `${location.pathname}${queryString}`)
}

const updateCategories = (data) => {
	data.forEach((course) => {
		if (
			course.category &&
			!categories.value.find((category) => category.value === course.category)
		)
			categories.value.push({
				label: course.category,
				value: course.category,
			})
	})
}

watch(currentTab, () => {
	updateCourses()
})

const courseTabs = computed(() => {
	let tabs = [
		{
			label: __('Live'),
			value: 'live',
		},
		{
			label: __('New'),
			value: 'new',
		},
		{
			label: __('Upcoming'),
			value: 'upcoming',
		},
	]
	if (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	) {
		tabs.push({ label: __('Created'), value: 'created' })
		tabs.push({ label: __('Unpublished'), value: 'unpublished' })
	} else if (user.data) {
		tabs.push({ label: __('Enrolled'), value: 'enrolled' })
	}
	return tabs
})

const courseMenu = computed(() => {
	return [
		{
			label: __('New Course'),
			icon: 'book-open',
			onClick() {
				showCourseModal.value = true
			},
		},
		{
			label: __('Import via Data Import Tool'),
			icon: 'upload',
			onClick() {
				router.push({
					name: 'NewDataImport',
					params: { doctype: 'LMS Course' },
				})
			},
		},
		{
			label: __('Import via ZIP'),
			icon: 'folder-plus',
			onClick() {
				showCourseImportModal.value = true
			},
		},
	]
})

const breadcrumbs = computed(() => [
	{
		label: __('Courses'),
		route: { name: 'Courses' },
	},
])

usePageMeta(() => {
	return {
		title: __('Courses'),
		icon: brand.favicon,
	}
})
</script>

<style scoped>
.gai-courses-page {
	--gai-accent: #6B3FA0;
	--gai-accent-soft: color-mix(in oklab, var(--gai-accent) 12%, transparent);
	--gai-paper: rgb(var(--surface-white));
	--gai-surface: rgb(var(--surface-gray-1));
	--gai-border: rgb(var(--outline-gray-2));
	--gai-ink: rgb(var(--text-ink-gray-9));
	--gai-muted: rgb(var(--text-ink-gray-5));
	padding: 2rem 1.5rem 4rem;
	max-width: 82rem;
	margin: 0 auto;
}

/* Hero */
.gai-page-hero {
	margin: -2rem -1.5rem 2.5rem;
	padding: clamp(2rem, 5vw, 3.5rem) clamp(1.25rem, 4vw, 3rem);
	border-bottom: 1px solid var(--gai-border);
	background: linear-gradient(
		180deg,
		color-mix(in oklab, var(--gai-accent-soft) 80%, var(--gai-surface)) 0%,
		var(--gai-surface) 40%,
		transparent 100%
	);
}

.gai-eyebrow {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	margin-bottom: 0.85rem;
	color: var(--gai-muted);
	font-size: 0.7rem;
	font-weight: 600;
	letter-spacing: 0.14em;
	text-transform: uppercase;
}

.gai-eyebrow span {
	width: 1.5rem;
	height: 1px;
	background: color-mix(in oklab, var(--gai-accent) 50%, transparent);
}

.gai-page-hero h1 {
	margin: 0 0 0.5rem;
	font-size: clamp(2rem, 4vw, 3.25rem);
	font-weight: 700;
	letter-spacing: -0.03em;
	line-height: 1.1;
	color: var(--gai-ink);
}

.gai-page-hero p {
	margin: 0;
	color: var(--gai-muted);
	font-size: 0.95rem;
}

/* Controls */
.gai-controls {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	margin-bottom: 2rem;
	padding-bottom: 1.5rem;
	border-bottom: 1px solid var(--gai-border);
}

.gai-search-row {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 0.75rem;
}

/* Grid */
.gai-grid {
	display: grid;
	grid-template-columns: repeat(1, 1fr);
	gap: 1.5rem;
}

@media (min-width: 768px)  { .gai-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .gai-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1600px) { .gai-grid { grid-template-columns: repeat(4, 1fr); } }

/* Card hover */
.gai-card-link {
	display: block;
	border-radius: 0.875rem;
	overflow: hidden;
	transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1),
	            box-shadow 0.35s ease;
}

.gai-card-link:hover {
	transform: translateY(-4px);
	box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

/* Load more */
.gai-load-more {
	display: flex;
	justify-content: center;
	margin-top: 3rem;
}
</style>
