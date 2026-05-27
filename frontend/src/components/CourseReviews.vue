<template>
	<div v-if="reviews.data?.length || membership" class="gai-reviews">

		<!-- Section header -->
		<div class="gai-reviews-header">
			<div class="gai-reviews-title">
				<div class="gai-eyebrow"><span></span>{{ __('Student Reviews') }}</div>
				<div class="gai-reviews-summary" v-if="reviews.data?.length">
					<div class="gai-reviews-score">{{ parseFloat(avg_rating) || 5 }}</div>
					<div class="gai-reviews-stars">
						<Star
							v-for="i in 5"
							:key="i"
							class="size-4 text-transparent rounded-sm"
							:class="i <= Math.ceil(parseFloat(avg_rating) || 5) ? 'fill-yellow-500' : 'fill-gray-300'"
						/>
					</div>
					<span class="gai-reviews-count">
						{{ reviews.data.length }} {{ reviews.data.length === 1 ? __('review') : __('reviews') }}
					</span>
				</div>
			</div>
			<Button
				v-if="membership && !hasReviewed.data"
				variant="subtle"
				@click="openReviewModal()"
			>
				{{ __('Write a Review') }}
			</Button>
		</div>

		<!-- Review cards -->
		<div class="gai-reviews-grid">
			<div
				v-for="(review, index) in reviews.data"
				:key="index"
				class="gai-review-card"
			>
				<div class="gai-review-top">
					<router-link
						:to="{ name: 'Profile', params: { username: review.owner_details.username } }"
						class="gai-review-avatar"
					>
						<UserAvatar :user="review.owner_details" :size="'2xl'" />
					</router-link>
					<div class="gai-review-meta">
						<router-link
							:to="{ name: 'Profile', params: { username: review.owner_details.username } }"
							class="gai-review-name"
						>
							{{ review.owner_details.full_name }}
						</router-link>
						<span class="gai-review-date">{{ review.creation }}</span>
					</div>
					<div class="gai-review-stars">
						<Star
							v-for="i in 5"
							:key="i"
							class="size-3.5 text-transparent"
							:class="i <= Math.ceil(review.rating) ? 'fill-yellow-500' : 'fill-gray-300'"
						/>
					</div>
				</div>
				<p v-if="review.review" class="gai-review-text">{{ review.review }}</p>
			</div>
		</div>

	</div>
	<ReviewModal
		v-model="showReviewModal"
		v-model:reloadReviews="reviews"
		v-model:hasReviewed="hasReviewed"
		:courseName="courseName"
	/>
</template>

<script setup>
import { Star } from 'lucide-vue-next'
import { createResource, Button } from 'frappe-ui'
import { watch, ref, inject } from 'vue'
import UserAvatar from '@/components/UserAvatar.vue'
import ReviewModal from '@/components/Modals/ReviewModal.vue'

const user = inject('$user')

const props = defineProps({
	courseName: {
		type: String,
		required: true,
	},
	avg_rating: {
		type: String,
		required: true,
	},
	membership: {
		type: Object || null,
		required: false,
	},
})

const hasReviewed = createResource({
	url: 'frappe.client.get_count',
	cache: ['eligible_to_review', props.courseName, props.membership?.member],
	params: {
		doctype: 'LMS Course Review',
		filters: {
			course: props.courseName,
			owner: props.membership?.member,
		},
	},
	auto: user.data?.name ? true : false,
})

const reviews = createResource({
	url: 'lms.lms.utils.get_reviews',
	cache: ['course_reviews', props.courseName],
	makeParams() {
		return { course: props.courseName }
	},
	auto: true,
})

watch(() => props.courseName, () => reviews.reload())

const showReviewModal = ref(false)
function openReviewModal() {
	showReviewModal.value = true
}
</script>

<style scoped>
/* ── Section wrapper ────────────────────────────────────────── */
.gai-reviews {
	margin-top: 3rem;
	padding-top: 2.5rem;
	border-top: 1px solid rgb(var(--outline-gray-2));
}

/* ── Header ─────────────────────────────────────────────────── */
.gai-reviews-header {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 1rem;
	margin-bottom: 1.75rem;
}

.gai-reviews-title {
	display: flex;
	flex-direction: column;
	gap: 0.6rem;
}

.gai-eyebrow {
	display: flex;
	align-items: center;
	gap: 0.6rem;
	color: rgb(var(--text-ink-gray-5));
	font-size: 0.68rem;
	font-weight: 600;
	letter-spacing: 0.14em;
	text-transform: uppercase;
}

.gai-eyebrow span {
	width: 1rem;
	height: 1px;
	background: color-mix(in oklab, #ee6708 50%, transparent);
	flex-shrink: 0;
}

.gai-reviews-summary {
	display: flex;
	align-items: center;
	gap: 0.6rem;
}

.gai-reviews-score {
	font-size: 2rem;
	font-weight: 700;
	letter-spacing: -0.03em;
	color: rgb(var(--text-ink-gray-9));
	line-height: 1;
}

.gai-reviews-stars {
	display: flex;
	gap: 0.15rem;
}

.gai-reviews-count {
	font-size: 0.8rem;
	font-family: 'JetBrains Mono', monospace;
	color: rgb(var(--text-ink-gray-5));
	letter-spacing: 0.02em;
}

/* ── Cards grid ─────────────────────────────────────────────── */
.gai-reviews-grid {
	display: grid;
	gap: 0.85rem;
}

/* ── Individual card ────────────────────────────────────────── */
.gai-review-card {
	padding: 1.1rem 1.25rem;
	border: 1.5px solid rgb(var(--outline-gray-2));
	border-radius: 8px;
	background: rgb(var(--surface-cards));
	transition: border-color 0.2s ease,
	            box-shadow 0.2s ease,
	            transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.gai-review-card:hover {
	border-color: color-mix(in oklab, #ee6708 40%, rgb(var(--outline-gray-2)));
	box-shadow: 0 0 0 3px color-mix(in oklab, #ee6708 7%, transparent),
	            0 4px 16px rgb(var(--brand-shadow-rgb) / 0.06);
	transform: translateY(-2px);
}

/* ── Card top row ───────────────────────────────────────────── */
.gai-review-top {
	display: flex;
	align-items: center;
	gap: 0.85rem;
	margin-bottom: 0.85rem;
}

.gai-review-avatar {
	flex-shrink: 0;
}

.gai-review-meta {
	display: flex;
	flex-direction: column;
	gap: 0.2rem;
	flex: 1;
	min-width: 0;
}

.gai-review-name {
	font-size: 0.9rem;
	font-weight: 600;
	color: rgb(var(--text-ink-gray-9));
	text-decoration: none;
	transition: color 0.15s ease;
}

.gai-review-name:hover {
	color: #ee6708;
}

.gai-review-date {
	font-size: 0.72rem;
	font-family: 'JetBrains Mono', monospace;
	color: rgb(var(--text-ink-gray-4));
	letter-spacing: 0.02em;
}

.gai-review-stars {
	display: flex;
	gap: 0.15rem;
	flex-shrink: 0;
}

/* ── Review text ────────────────────────────────────────────── */
.gai-review-text {
	font-size: 0.9rem;
	line-height: 1.7;
	color: rgb(var(--text-ink-gray-6));
	margin: 0;
	padding-top: 0.75rem;
	border-top: 1px solid rgb(var(--outline-gray-1));
}
</style>
