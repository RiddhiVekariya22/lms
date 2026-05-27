<template>
	<div class="">
		<div
			v-if="title && (outline.data?.length || allowEdit)"
			class="flex items-center justify-between gap-x-2 mb-4 px-2"
			:class="{
				'sticky top-0 z-10 bg-surface-white border-b px-3 py-2.5 sm:px-5':
					allowEdit,
			}"
		>
			<div
				class="font-semibold text-lg leading-5 text-ink-gray-9"
				:class="{ 'font-medium text-p-base': allowEdit }"
			>
				{{ __(title) }}
			</div>
			<Button size="sm" v-if="allowEdit" @click="openChapterModal()">
				<template #prefix>
					<Plus class="size-4 stroke-1.5" />
				</template>
				{{ __('Add') }}
			</Button>
		</div>
		<div :class="{ 'gai-outline-container': showOutline && outline.data?.length }">
			<Draggable
				:list="outline.data"
				:disabled="!allowEdit"
				item-key="name"
				group="chapters"
				@end="updateChapterOrder"
			>
				<template #item="{ element: chapter, index }">
					<div class="gai-chapter-item">
						<Disclosure
							v-slot="{ open }"
							:key="chapter.name"
							:defaultOpen="openChapterDetail(chapter.idx)"
						>
							<DisclosureButton
								class="gai-chapter-btn group"
								:class="{ 'gai-chapter-btn--open': open }"
							>
								<span class="gai-chapter-chevron" :class="{ 'gai-chapter-chevron--open': open, 'hidden': chapter.is_scorm_package }">
									<ChevronRight class="h-3.5 w-3.5 stroke-1.5" />
								</span>
								<span
									class="gai-chapter-title"
									@click="redirectToChapter(chapter)"
								>
									{{ chapter.title }}
								</span>
								<span class="gai-chapter-count" v-if="chapter.lessons?.length && !allowEdit">
									{{ chapter.lessons.length }} {{ chapter.lessons.length === 1 ? __('lesson') : __('lessons') }}
								</span>
								<div class="flex ms-auto gap-x-3">
									<Tooltip :text="__('Edit Chapter')" placement="bottom">
										<FilePenLine
											v-if="allowEdit"
											@click.prevent="openChapterModal(chapter)"
											class="h-4 w-4 text-ink-gray-6 invisible group-hover:visible transition-opacity"
										/>
									</Tooltip>
									<Tooltip :text="__('Delete Chapter')" placement="bottom">
										<Trash2
											v-if="allowEdit"
											@click.prevent="trashChapter(chapter.name)"
											class="h-4 w-4 text-ink-red-3 invisible group-hover:visible transition-opacity"
										/>
									</Tooltip>
								</div>
								<Check
									v-if="chapter.is_scorm_package && isScormChapterComplete(chapter)"
									class="h-4 w-4 text-green-700 ms-2"
								/>
							</DisclosureButton>

							<DisclosurePanel v-if="!chapter.is_scorm_package" class="gai-lesson-panel">
								<Draggable
									v-if="!chapter.is_scorm_package"
									:list="chapter.lessons"
									:disabled="!allowEdit"
									item-key="name"
									group="items"
									@end="updateOutline"
									:data-chapter="chapter.name"
								>
									<template #item="{ element: lesson }">
										<div
											class="gai-lesson"
											:class="{ 'gai-lesson--active': isActiveLesson(lesson.number) }"
										>
											<router-link
												:to="{
													name: allowEdit ? 'LessonForm' : 'Lesson',
													params: {
														courseName: courseName,
														chapterNumber: lesson.number.split('-')[0],
														lessonNumber: lesson.number.split('-')[1],
													},
												}"
												class="gai-lesson-link group"
											>
												<span class="gai-lesson-icon">
													<MonitorPlay v-if="lesson.icon === 'icon-youtube'" class="h-3.5 w-3.5 stroke-1.5" />
													<HelpCircle v-else-if="lesson.icon === 'icon-quiz'" class="h-3.5 w-3.5 stroke-1.5" />
													<NotebookPen v-else-if="lesson.icon === 'icon-assignment'" class="h-3.5 w-3.5 stroke-1.5" />
													<SquareCode v-else-if="lesson.icon === 'icon-code'" class="h-3.5 w-3.5 stroke-1.5" />
													<FileText v-else class="h-3.5 w-3.5 stroke-1.5" />
												</span>
												<span class="gai-lesson-title">{{ lesson.title }}</span>
												<span v-if="lesson.is_complete" class="gai-lesson-done">
													<Check class="h-3 w-3" />
												</span>
												<Trash2
													v-if="allowEdit"
													@click.prevent="trashLesson(lesson.name, chapter.name)"
													class="h-4 w-4 text-ink-red-3 ms-auto invisible group-hover:visible"
												/>
											</router-link>
										</div>
									</template>
								</Draggable>
								<div v-if="allowEdit" class="px-4 pb-3 pt-1">
									<router-link
										v-if="!chapter.is_scorm_package"
										:to="{
											name: 'LessonForm',
											params: {
												courseName: courseName,
												chapterNumber: chapter.idx,
												lessonNumber: chapter.lessons.length + 1,
											},
										}"
									>
										<Button size="sm">{{ __('Add Lesson') }}</Button>
									</router-link>
								</div>
							</DisclosurePanel>
						</Disclosure>
					</div>
				</template>
			</Draggable>
		</div>
	</div>
	<ChapterModal
		v-if="user.data"
		v-model="showChapterModal"
		v-model:outline="outline"
		:course="courseName"
		:chapterDetail="getCurrentChapter()"
	/>
</template>
<script setup>
import { Button, createResource, Tooltip, toast } from 'frappe-ui'
import { getCurrentInstance, inject, ref, watch } from 'vue'
import Draggable from 'vuedraggable'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
	Check,
	ChevronRight,
	FileText,
	FilePenLine,
	HelpCircle,
	MonitorPlay,
	NotebookPen,
	Plus,
	SquareCode,
	Trash2,
} from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import ChapterModal from '@/components/Modals/ChapterModal.vue'

const route = useRoute()
const router = useRouter()
const user = inject('$user')
const showChapterModal = ref(false)
const currentChapter = ref(null)
const app = getCurrentInstance()
const { $dialog } = app.appContext.config.globalProperties

const props = defineProps({
	courseName: {
		type: String,
		required: true,
	},
	showOutline: {
		type: Boolean,
		default: false,
	},
	title: {
		type: String,
		default: '',
	},
	allowEdit: {
		type: Boolean,
		default: false,
	},
	getProgress: {
		type: Boolean,
		default: false,
	},
	lessonProgress: {
		type: Number,
		default: 0,
	},
})

const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	cache: ['course_outline', props.courseName],
	makeParams() {
		return {
			course: props.courseName,
			progress: props.getProgress,
		}
	},
	auto: true,
})

watch(
	() => props.courseName,
	() => {
		outline.reload()
	}
)

watch(
	() => props.lessonProgress,
	() => {
		outline.reload()
	}
)

const deleteLesson = createResource({
	url: 'lms.lms.api.delete_lesson',
	makeParams(values) {
		return {
			lesson: values.lesson,
			chapter: values.chapter,
		}
	},
	onSuccess() {
		outline.reload()
		toast.success(__('Lesson deleted successfully'))
	},
})

const updateLessonIndex = createResource({
	url: 'lms.lms.api.update_lesson_index',
	makeParams(values) {
		return {
			lesson: values.lesson,
			sourceChapter: values.sourceChapter,
			targetChapter: values.targetChapter,
			idx: values.idx,
		}
	},
	onSuccess() {
		toast.success(__('Lesson moved successfully'))
	},
})

const updateChapterIndex = createResource({
	url: 'lms.lms.api.update_chapter_index',
	makeParams(values) {
		return {
			chapter: values.chapter,
			course: values.course,
			idx: values.idx,
		}
	},
	onSuccess() {
		toast.success(__('Chapter moved successfully'))
	},
})

const trashLesson = (lessonName, chapterName) => {
	$dialog({
		title: __('Delete this lesson?'),
		message: __(
			'Deleting this lesson will permanently remove it from the course. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					deleteLesson.submit({
						lesson: lessonName,
						chapter: chapterName,
					})
					close()
				},
			},
		],
	})
}

const openChapterDetail = (index) => {
	return index == route.params.chapterNumber || index == 1
}

const openChapterModal = (chapter = null) => {
	currentChapter.value = chapter
	showChapterModal.value = true
}

const getCurrentChapter = () => {
	return currentChapter.value
}

const updateOutline = (e) => {
	updateLessonIndex.submit({
		lesson: e.item.__draggable_context.element.name,
		sourceChapter: e.from.dataset.chapter,
		targetChapter: e.to.dataset.chapter,
		idx: e.newIndex,
	})
}

const updateChapterOrder = (e) => {
	updateChapterIndex.submit({
		chapter: e.item.__draggable_context.element.name,
		course: props.courseName,
		idx: e.newIndex,
	})
}

const deleteChapter = createResource({
	url: 'lms.lms.api.delete_chapter',
	makeParams(values) {
		return {
			chapter: values.chapter,
		}
	},
	onSuccess() {
		outline.reload()
		toast.success(__('Chapter deleted successfully'))
	},
})

const trashChapter = (chapterName) => {
	$dialog({
		title: __('Delete this chapter?'),
		message: __(
			'Deleting this chapter will also delete all its lessons and permanently remove it from the course. This action cannot be undone. Are you sure you want to continue?'
		),
		actions: [
			{
				label: __('Delete'),
				theme: 'red',
				variant: 'solid',
				onClick(close) {
					deleteChapter.submit({ chapter: chapterName })
					close()
				},
			},
		],
	})
}

const redirectToChapter = (chapter) => {
	if (!chapter.is_scorm_package) return
	event.preventDefault()
	if (props.allowEdit) return
	if (!user.data) {
		toast.success(__('Please enroll for this course to view this lesson'))
		return
	}

	router.push({
		name: 'SCORMChapter',
		params: {
			courseName: props.courseName,
			chapterName: chapter.name,
		},
	})
}

const isScormChapterComplete = (chapter) => {
	return chapter.lessons?.length && chapter.lessons.every((l) => l.is_complete)
}

const isActiveLesson = (lessonNumber) => {
	return (
		route.params.chapterNumber == lessonNumber.split('-')[0] &&
		route.params.lessonNumber == lessonNumber.split('-')[1]
	)
}
</script>

<style scoped>
/* ── Container ──────────────────────────────────────────────── */
.gai-outline-container {
	border: 1.5px solid rgb(var(--outline-gray-2));
	border-radius: 8px;
	overflow: hidden;
	background: rgb(var(--surface-cards));
}

/* ── Chapter item ───────────────────────────────────────────── */
.gai-chapter-item {
	border-bottom: 1px solid rgb(var(--outline-gray-1));
}

.gai-chapter-item:last-child {
	border-bottom: none;
}

/* ── Chapter button ─────────────────────────────────────────── */
.gai-chapter-btn {
	display: flex;
	align-items: center;
	width: 100%;
	padding: 0.8rem 1rem;
	gap: 0.6rem;
	background: rgb(var(--surface-gray-1));
	transition: background 0.2s ease;
	text-align: left;
}

.gai-chapter-btn:hover {
	background: rgb(var(--surface-gray-2));
}

.gai-chapter-btn--open {
	background: rgb(var(--surface-gray-1));
	border-left: 2.5px solid #ee6708;
}

.gai-chapter-chevron {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 1.25rem;
	height: 1.25rem;
	border-radius: 4px;
	border: 1px solid rgb(var(--outline-gray-2));
	background: rgb(var(--surface-cards));
	color: rgb(var(--text-ink-gray-6));
	flex-shrink: 0;
	transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1),
	            border-color 0.2s ease,
	            color 0.2s ease;
}

.gai-chapter-chevron--open {
	transform: rotate(90deg);
	border-color: color-mix(in oklab, #ee6708 50%, rgb(var(--outline-gray-2)));
	color: #ee6708;
}

.gai-chapter-title {
	font-size: 0.9rem;
	font-weight: 600;
	color: rgb(var(--text-ink-gray-9));
	letter-spacing: -0.01em;
	line-height: 1.3;
	flex: 1;
	text-align: left;
}

.gai-chapter-count {
	font-size: 0.7rem;
	font-family: 'JetBrains Mono', monospace;
	color: rgb(var(--text-ink-gray-4));
	letter-spacing: 0.04em;
	flex-shrink: 0;
}

/* ── Lesson panel ───────────────────────────────────────────── */
.gai-lesson-panel {
	padding: 0.4rem 0.5rem 0.5rem;
	background: rgb(var(--surface-cards));
}

/* ── Lesson row ─────────────────────────────────────────────── */
.gai-lesson {
	border-radius: 6px;
	margin-bottom: 2px;
	border: 1px solid transparent;
	transition: border-color 0.18s ease, background 0.18s ease;
}

.gai-lesson:hover {
	background: rgb(var(--surface-gray-1));
	border-color: rgb(var(--outline-gray-1));
}

.gai-lesson--active {
	background: color-mix(in oklab, #ee6708 8%, rgb(var(--surface-cards)));
	border-color: color-mix(in oklab, #ee6708 30%, transparent);
	border-left: 2.5px solid #ee6708;
}

.gai-lesson--active .gai-lesson-title {
	color: rgb(var(--text-ink-gray-9));
	font-weight: 600;
}

.gai-lesson--active .gai-lesson-icon {
	color: #ee6708;
	border-color: color-mix(in oklab, #ee6708 35%, transparent);
	background: color-mix(in oklab, #ee6708 10%, transparent);
}

/* ── Lesson link ────────────────────────────────────────────── */
.gai-lesson-link {
	display: flex;
	align-items: center;
	gap: 0.6rem;
	padding: 0.55rem 0.75rem;
	text-decoration: none;
}

/* ── Lesson icon box ────────────────────────────────────────── */
.gai-lesson-icon {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 1.5rem;
	height: 1.5rem;
	border-radius: 4px;
	border: 1px solid rgb(var(--outline-gray-2));
	background: rgb(var(--surface-gray-1));
	color: rgb(var(--text-ink-gray-5));
	flex-shrink: 0;
	transition: color 0.18s ease, background 0.18s ease, border-color 0.18s ease;
}

.gai-lesson:hover .gai-lesson-icon {
	border-color: color-mix(in oklab, #ee6708 25%, rgb(var(--outline-gray-2)));
	color: rgb(var(--text-ink-gray-7));
}

/* ── Lesson title ───────────────────────────────────────────── */
.gai-lesson-title {
	font-size: 0.85rem;
	color: rgb(var(--text-ink-gray-7));
	line-height: 1.4;
	flex: 1;
	transition: color 0.18s ease;
}

.gai-lesson:hover .gai-lesson-title {
	color: rgb(var(--text-ink-gray-9));
}

/* ── Done badge ─────────────────────────────────────────────── */
.gai-lesson-done {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 1.1rem;
	height: 1.1rem;
	border-radius: 99px;
	background: #16a34a;
	color: #fff;
	flex-shrink: 0;
}
</style>
