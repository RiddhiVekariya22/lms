<template>
	<div class="gai-overview">
		<!-- Hero — title + enrollment card -->
		<section class="gai-overview-hero gai-rise">
			<div class="gai-overview-copy">
				<div class="gai-eyebrow" v-if="course.data.category">
					<span></span>{{ course.data.category }}
				</div>
				<div class="gai-eyebrow" v-else>
					<span></span>{{ __('Course') }}
				</div>

				<h1>{{ course.data.title }}</h1>
				<p class="gai-intro">{{ course.data.short_introduction }}</p>
				<div class="gai-meta-row">
					<Tooltip
						v-if="parseInt(course.data.rating) > 0"
						:text="__('Average Rating')"
					>
						<div class="gai-meta-item">
							<Star class="size-4 fill-current text-orange-500" />
							<span>{{ course.data.rating }}</span>
						</div>
					</Tooltip>
					<span
						v-if="parseInt(course.data.rating) > 0 && course.data.enrollment_count"
						class="gai-meta-dot"
					>·</span>
					<Tooltip
						v-if="course.data.enrollment_count"
						:text="__('Enrolled Students')"
					>
						<div class="gai-meta-item">
							<Users class="h-4 w-4" />
							<span>{{ course.data.enrollment_count_formatted }}</span>
						</div>
					</Tooltip>
					<span v-if="course.data.enrollment_count" class="gai-meta-dot">·</span>
					<div class="gai-meta-item">
						<span
							class="h-6 me-1"
							:class="{ 'avatar-group overlap': course.data.instructors.length > 1 }"
						>
							<UserAvatar
								v-for="instructor in course.data.instructors"
								:user="instructor"
							/>
						</span>
						<CourseInstructors :instructors="course.data.instructors" />
					</div>
				</div>

				<div v-if="course.data.tags" class="gai-tags">
					<span
						v-for="tag in course.data.tags.split(', ')"
						:key="tag"
						class="gai-tag"
					>{{ tag }}</span>
				</div>

				<!-- Mobile enrollment card -->
				<div class="gai-mobile-enroll">
					<CourseCardOverlay :course="course" />
				</div>
			</div>

			<!-- Desktop enrollment card -->
			<div class="gai-enroll-card">
				<CourseCardOverlay :course="course" />
			</div>
		</section>

		<!-- Body — description, outline, reviews -->
		<section class="gai-overview-body gai-rise" style="--delay: 80ms">
			<div
				v-html="course.data.description"
				class="gai-prose ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal"
			></div>

			<div class="gai-outline-wrap">
				<CourseOutline
					:title="__('Course Outline')"
					:courseName="course.data.name"
					:showOutline="true"
					:getProgress="course.data.membership ? true : false"
				/>
			</div>

			<CourseReviews
				:courseName="course.data.name"
				:avg_rating="course.data.rating"
				:membership="course.data.membership || null"
			/>
		</section>

		<RelatedCourses :courseName="course.data.name" />
	</div>
</template>
<script setup lang="ts">
import { Star, Users } from 'lucide-vue-next'
import { Badge, Tooltip } from 'frappe-ui'
import CourseCardOverlay from '@/components/CourseCardOverlay.vue'
import CourseOutline from '@/components/CourseOutline.vue'
import CourseReviews from '@/components/CourseReviews.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import RelatedCourses from '@/components/RelatedCourses.vue'

const props = defineProps<{
	course: any
}>()
</script>

<style scoped>
.gai-overview {
	--gai-accent: #6B3FA0;
	--gai-accent-soft: color-mix(in oklab, var(--gai-accent) 12%, transparent);
	--gai-paper: rgb(var(--surface-white));
	--gai-surface: rgb(var(--surface-gray-1));
	--gai-border: rgb(var(--outline-gray-2));
	--gai-ink: rgb(var(--text-ink-gray-9));
	--gai-muted: rgb(var(--text-ink-gray-5));
}

/* ── Hero ─────────────────────────────────────────────────── */
.gai-overview-hero {
	display: flex;
	align-items: flex-start;
	gap: 2.5rem;
	padding: clamp(2rem, 5vw, 3.5rem) clamp(1.25rem, 4vw, 3rem);
	border-bottom: 1px solid var(--gai-border);
	background: linear-gradient(
		180deg,
		color-mix(in oklab, var(--gai-accent-soft) 80%, var(--gai-surface)) 0%,
		var(--gai-surface) 40%,
		transparent 100%
	);
}

.gai-overview-copy {
	flex: 1;
	min-width: 0;
}

.gai-eyebrow {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	margin-bottom: 1rem;
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

.gai-overview-copy h1 {
	margin: 0 0 1rem;
	font-size: clamp(1.75rem, 4vw, 3rem);
	font-weight: 700;
	letter-spacing: -0.03em;
	line-height: 1.1;
	color: var(--gai-ink);
	text-wrap: pretty;
}

.gai-intro {
	margin: 0 0 1.25rem;
	max-width: 52rem;
	color: var(--gai-muted);
	font-size: 1.05rem;
	line-height: 1.7;
}

/* Metadata */
.gai-meta-row {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 0.5rem;
	margin-bottom: 1.25rem;
	color: var(--gai-muted);
	font-size: 0.9rem;
}

.gai-meta-item {
	display: flex;
	align-items: center;
	gap: 0.35rem;
}

.gai-meta-dot {
	color: var(--gai-border);
}

/* Tags */
.gai-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
	margin-bottom: 1.5rem;
}

.gai-tag {
	padding: 0.25rem 0.75rem;
	border: 1px solid var(--gai-border);
	border-radius: 99px;
	color: var(--gai-muted);
	font-size: 0.75rem;
	font-weight: 500;
	letter-spacing: 0.02em;
	background: var(--gai-paper);
	transition: border-color 0.2s ease, color 0.2s ease;
}

.gai-tag:hover {
	border-color: color-mix(in oklab, var(--gai-accent) 50%, transparent);
	color: var(--gai-accent);
}

/* Mobile enrollment card */
.gai-mobile-enroll { display: block; margin-top: 1.5rem; }

/* Desktop enrollment card */
.gai-enroll-card {
	display: none;
	flex-shrink: 0;
	width: 22rem;
}

@media (min-width: 768px) {
	.gai-mobile-enroll { display: none; }
	.gai-enroll-card   { display: block; }
}

/* ── Body ─────────────────────────────────────────────────── */
.gai-overview-body {
	max-width: 52rem;
	padding: clamp(2rem, 4vw, 3rem) clamp(1.25rem, 4vw, 3rem);
}

.gai-prose {
	margin-bottom: 0;
	font-size: 1rem;
	line-height: 1.75;
}

.gai-outline-wrap {
	margin-top: 3rem;
	padding-top: 2.5rem;
	border-top: 1px solid var(--gai-border);
}
</style>
