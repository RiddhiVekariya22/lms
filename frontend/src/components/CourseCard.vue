<template>
	<div v-if="course.title" class="gai-course-card">

		<!-- Image / Gradient placeholder -->
		<div class="gai-card-image" :style="imageStyle">
			<div v-if="course.featured" class="gai-card-featured">
				<Star class="size-3 fill-current" />
				{{ __('Featured') }}
			</div>
			<div v-if="!course.image" class="gai-card-title-overlay">
				{{ course.title }}
			</div>
			<div v-if="course.image" class="gai-card-image-scrim"></div>
		</div>

		<!-- Body -->
		<div class="gai-card-body">

			<!-- Category eyebrow -->
			<div v-if="course.category" class="gai-card-eyebrow">
				<span></span>{{ course.category }}
			</div>

			<!-- Tags -->
			<div v-if="course.tags" class="gai-card-tags">
				<span
					v-for="tag in course.tags?.split(', ')"
					:key="tag"
					class="gai-card-tag"
				>{{ tag }}</span>
			</div>

			<!-- Title (only shown when image exists — otherwise shown in overlay) -->
			<div
				v-if="course.image"
				class="gai-card-name"
				:class="course.title.length > 40 ? 'text-base' : 'text-lg'"
			>
				{{ course.title }}
			</div>

			<!-- Intro -->
			<div class="gai-card-intro">{{ course.short_introduction }}</div>

			<!-- Progress -->
			<template v-if="user && course.membership">
				<ProgressBar :progress="course.membership.progress" class="mt-auto mb-1" />
				<div class="gai-card-progress-label">
					{{ Math.ceil(course.membership.progress) }}% {{ __('completed') }}
				</div>
			</template>

			<!-- Footer -->
			<div class="gai-card-footer">
				<div class="gai-card-instructors">
					<div
						class="h-6"
						:class="{ 'avatar-group overlap': course.instructors.length > 1 }"
					>
						<UserAvatar
							v-for="instructor in course.instructors"
							:user="instructor"
						/>
					</div>
					<CourseInstructors :instructors="course.instructors" />
				</div>

				<div class="gai-card-stats">
					<Tooltip v-if="course.lessons" :text="__('Lessons')">
						<span class="gai-stat">
							<BookOpen class="h-3.5 w-3.5 stroke-1.5" />
							{{ course.lessons }}
						</span>
					</Tooltip>
					<Tooltip :text="__('Average Rating')">
						<span class="gai-stat">
							<Star class="h-3.5 w-3.5 stroke-1.5" />
							{{ parseFloat(course.rating) || 5 }}
						</span>
					</Tooltip>
					<span v-if="course.paid_course" class="gai-card-price">
						{{ course.price }}
					</span>
					<Tooltip
						v-if="course.paid_certificate || course.enable_certification"
						:text="__('Get Certified')"
					>
						<GraduationCap class="size-4 stroke-1.5 text-[#ee6708]" />
					</Tooltip>
				</div>
			</div>

		</div>
	</div>
</template>

<script setup>
import { Award, BookOpen, GraduationCap, Star, Users } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { Tooltip } from 'frappe-ui'
import { formatAmount } from '@/utils'
import { theme } from '@/utils/theme'
import { computed } from 'vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import colors from '@/utils/frappe-ui-colors.json'

const { user } = sessionStore()

const props = defineProps({
	course: {
		type: Object,
		default: null,
	},
})

const gradientColor = computed(() => {
	let themeMode = theme.value === 'dark' ? 'darkMode' : 'lightMode'
	let color = props.course.card_gradient?.toLowerCase() || 'blue'
	let colorMap = colors[themeMode][color]
	return `linear-gradient(135deg, #0f0a08 0%, ${colorMap[700] || colorMap[600] || '#2a1206'} 65%, #c03810 100%)`
})

const imageStyle = computed(() => {
	if (props.course.image) {
		return {
			backgroundImage: `url('${encodeURI(props.course.image)}')`,
			backgroundSize: 'cover',
			backgroundPosition: 'center',
		}
	}
	return { background: gradientColor.value }
})
</script>

<style scoped>
.gai-course-card {
	display: flex;
	flex-direction: column;
	height: 100%;
	border: 1.5px solid rgb(var(--outline-gray-2));
	border-radius: 8px;
	overflow: hidden;
	background: rgb(var(--surface-cards));
	transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.gai-course-card:hover {
	border-color: color-mix(in oklab, #ee6708 45%, rgb(var(--outline-gray-2)));
	box-shadow: 0 0 0 3px color-mix(in oklab, #ee6708 8%, transparent);
}

/* ── Image area ─────────────────────────────────────────────── */
.gai-card-image {
	position: relative;
	width: 100%;
	height: 168px;
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	justify-content: flex-end;
	padding: 0.75rem;
}

.gai-card-image-scrim {
	position: absolute;
	inset: 0;
	background: linear-gradient(to top, rgba(0,0,0,0.4) 0%, transparent 50%);
	pointer-events: none;
}

.gai-card-featured {
	position: absolute;
	top: 0.6rem;
	right: 0.6rem;
	display: flex;
	align-items: center;
	gap: 0.3rem;
	padding: 0.2rem 0.6rem;
	border-radius: 99px;
	background: #ee6708;
	color: #fff;
	font-size: 0.65rem;
	font-weight: 600;
	letter-spacing: 0.06em;
	text-transform: uppercase;
}

.gai-card-title-overlay {
	color: #fff;
	font-weight: 700;
	font-size: 1.1rem;
	line-height: 1.25;
	letter-spacing: -0.02em;
	text-shadow: 0 1px 8px rgba(0,0,0,0.4);
	text-wrap: pretty;
}

/* ── Body ───────────────────────────────────────────────────── */
.gai-card-body {
	display: flex;
	flex-direction: column;
	flex: 1;
	padding: 1rem;
	gap: 0.5rem;
}

.gai-card-eyebrow {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	color: rgb(var(--text-ink-gray-5));
	font-size: 0.65rem;
	font-weight: 600;
	letter-spacing: 0.12em;
	text-transform: uppercase;
}

.gai-card-eyebrow span {
	width: 1rem;
	height: 1px;
	background: color-mix(in oklab, #ee6708 50%, transparent);
	flex-shrink: 0;
}

.gai-card-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 0.35rem;
}

.gai-card-tag {
	padding: 0.15rem 0.55rem;
	border: 1px solid rgb(var(--outline-gray-2));
	border-radius: 99px;
	color: rgb(var(--text-ink-gray-5));
	font-size: 0.7rem;
	font-weight: 500;
	background: transparent;
}

.gai-card-name {
	font-weight: 700;
	letter-spacing: -0.02em;
	line-height: 1.25;
	color: rgb(var(--text-ink-gray-9));
	text-wrap: pretty;
}

.gai-card-intro {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
	text-overflow: ellipsis;
	font-size: 0.85rem;
	line-height: 1.55;
	color: rgb(var(--text-ink-gray-5));
	flex-shrink: 0;
}

.gai-card-progress-label {
	font-size: 0.75rem;
	color: rgb(var(--text-ink-gray-5));
}

/* ── Footer ─────────────────────────────────────────────────── */
.gai-card-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-top: auto;
	padding-top: 0.75rem;
	border-top: 1px solid rgb(var(--outline-gray-1));
	gap: 0.5rem;
}

.gai-card-instructors {
	display: flex;
	align-items: center;
	gap: 0.4rem;
	min-width: 0;
	overflow: hidden;
}

.gai-card-stats {
	display: flex;
	align-items: center;
	gap: 0.6rem;
	flex-shrink: 0;
}

.gai-stat {
	display: flex;
	align-items: center;
	gap: 0.25rem;
	font-size: 0.78rem;
	color: rgb(var(--text-ink-gray-5));
}

.gai-card-price {
	font-size: 0.85rem;
	font-weight: 700;
	color: rgb(var(--text-ink-gray-9));
}

/* ── Avatar group ───────────────────────────────────────────── */
:deep(.avatar-group) {
	display: inline-flex;
	align-items: center;
}

:deep(.avatar-group.overlap .avatar + .avatar) {
	margin-inline-start: -8px;
}
</style>
