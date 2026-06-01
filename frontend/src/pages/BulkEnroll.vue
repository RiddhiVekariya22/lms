<template>
	<div v-if="userResource.data?.is_uni_admin">
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
		>
			<Breadcrumbs
				class="h-7"
				:items="[{ label: __('Bulk Enroll'), route: { name: 'BulkEnroll' } }]"
			/>
		</header>

		<div class="pt-8 pb-16 mx-5 max-w-3xl">
			<!-- Step 1: Upload CSV -->
			<div class="mb-8">
				<h2 class="text-base font-semibold text-ink-gray-9 mb-1">
					{{ __('Step 1 — Upload Student CSV') }}
				</h2>
				<p class="text-sm text-ink-gray-6 mb-4">
					{{
						__(
							'CSV must have columns: email, first_name, last_name (last_name optional)'
						)
					}}
				</p>
				<input
					type="file"
					accept=".csv"
					class="block text-sm text-ink-gray-7 file:mr-4 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-sm file:bg-surface-gray-3 file:text-ink-gray-8 hover:file:bg-surface-gray-4 cursor-pointer"
					@change="handleFileUpload"
				/>
				<div
					v-if="csvError"
					class="mt-2 text-sm text-ink-red-3"
				>
					{{ csvError }}
				</div>

				<div
					v-if="parsedRows.length"
					class="mt-4 border rounded-md overflow-hidden"
				>
					<table class="w-full text-sm">
						<thead class="bg-surface-gray-2 text-ink-gray-7">
							<tr>
								<th class="text-left px-3 py-2 font-medium">#</th>
								<th class="text-left px-3 py-2 font-medium">
									{{ __('Email') }}
								</th>
								<th class="text-left px-3 py-2 font-medium">
									{{ __('First Name') }}
								</th>
								<th class="text-left px-3 py-2 font-medium">
									{{ __('Last Name') }}
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="(row, i) in parsedRows"
								:key="i"
								class="border-t"
							>
								<td class="px-3 py-2 text-ink-gray-5">{{ i + 1 }}</td>
								<td class="px-3 py-2">{{ row.email }}</td>
								<td class="px-3 py-2">{{ row.first_name }}</td>
								<td class="px-3 py-2">{{ row.last_name || '—' }}</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Step 2: Select course/batch + cost preview -->
			<div
				v-if="parsedRows.length"
				class="mb-8"
			>
				<h2 class="text-base font-semibold text-ink-gray-9 mb-4">
					{{ __('Step 2 — Select Course or Batch') }}
				</h2>
				<div class="flex gap-4 mb-4">
					<label class="flex items-center gap-2 cursor-pointer">
						<input
							type="radio"
							value="LMS Course"
							v-model="enrollType"
							@change="documentName = ''; costPreview = null"
						/>
						<span class="text-sm text-ink-gray-8">{{ __('Course') }}</span>
					</label>
					<label class="flex items-center gap-2 cursor-pointer">
						<input
							type="radio"
							value="LMS Batch"
							v-model="enrollType"
							@change="documentName = ''; costPreview = null"
						/>
						<span class="text-sm text-ink-gray-8">{{ __('Batch') }}</span>
					</label>
				</div>

				<div
					v-if="enrollType"
					class="mb-4"
				>
					<Link
						:label="enrollType === 'LMS Course' ? __('Select Course') : __('Select Batch')"
						:doctype="enrollType"
						v-model="documentName"
						@update:modelValue="fetchCostPreview"
					/>
				</div>

				<div
					v-if="costPreview"
					class="bg-surface-gray-1 rounded-md px-4 py-3 text-sm text-ink-gray-8 space-y-1"
				>
					<div>
						<span class="text-ink-gray-5">{{ __('Unit price:') }}</span>
						{{ costPreview.unit_price }} {{ costPreview.currency }}
					</div>
					<div>
						<span class="text-ink-gray-5">{{ __('Students:') }}</span>
						{{ parsedRows.length }}
					</div>
					<div class="font-semibold text-ink-gray-9 border-t pt-2 mt-2">
						<span class="text-ink-gray-5">{{ __('Total:') }}</span>
						{{ costPreview.total_amount }} {{ costPreview.currency }}
					</div>
					<div
						v-if="costPreview.unit_price === 0"
						class="text-ink-green-5 font-medium"
					>
						{{ __('This is a free enrollment — no payment required.') }}
					</div>
				</div>
			</div>

			<!-- Step 3: Enroll / Pay -->
			<div v-if="costPreview && !results.length">
				<h2 class="text-base font-semibold text-ink-gray-9 mb-4">
					{{ __('Step 3 — Enroll') }}
				</h2>
				<Button
					variant="solid"
					size="md"
					:loading="submitting"
					@click="submitEnrollment"
				>
					{{
						costPreview.unit_price === 0
							? __('Enroll Students')
							: __('Proceed to Payment')
					}}
				</Button>
			</div>

			<!-- Results -->
			<Transition name="success-pop">
				<div v-if="results.length">
					<!-- Success banner -->
					<div
						v-if="enrolledCount > 0"
						class="mb-6 flex items-center gap-4 rounded-xl bg-green-50 border border-green-200 px-5 py-4"
					>
						<div class="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-green-100">
							<CheckCircle2 class="w-6 h-6 text-green-600" />
						</div>
						<div>
							<div class="font-semibold text-green-800 text-base">
								{{ __('Enrollment Complete') }}
							</div>
							<div class="text-sm text-green-700 mt-0.5">
								{{ enrolledCount }} of {{ results.length }}
								{{ results.length === 1 ? __('student') : __('students') }}
								{{ __('enrolled successfully') }}.
								{{ failedCount > 0 ? `${failedCount} failed — check the table below.` : '' }}
							</div>
						</div>
					</div>

					<!-- Per-student table -->
					<div class="border rounded-md overflow-hidden">
						<table class="w-full text-sm">
							<thead class="bg-surface-gray-2 text-ink-gray-7">
								<tr>
									<th class="text-left px-3 py-2 font-medium">{{ __('Email') }}</th>
									<th class="text-left px-3 py-2 font-medium">{{ __('Status') }}</th>
								</tr>
							</thead>
							<tbody>
								<tr
									v-for="(r, i) in results"
									:key="i"
									class="border-t"
								>
									<td class="px-3 py-2">{{ r.email }}</td>
									<td
										class="px-3 py-2 font-medium"
										:class="r.status === 'Enrolled' ? 'text-green-600' : 'text-red-500'"
									>
										{{ r.status }}
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</Transition>
		</div>
	</div>

	<NotPermitted
		v-else
		:text="__('You need the Uni Admin role to access this page.')"
	/>
</template>

<script setup>
import { Button, Breadcrumbs, call, toast } from 'frappe-ui'
import { ref, computed } from 'vue'
import { usersStore } from '@/stores/user'
import Link from '@/components/Controls/Link.vue'
import NotPermitted from '@/components/NotPermitted.vue'
import { getLmsRoute } from '@/utils/basePath'
import { CheckCircle2 } from 'lucide-vue-next'

const { userResource } = usersStore()

const parsedRows = ref([])
const csvError = ref('')
const enrollType = ref('LMS Course')
const documentName = ref('')
const costPreview = ref(null)
const submitting = ref(false)
const results = ref([])

const enrolledCount = computed(() => results.value.filter((r) => r.status === 'Enrolled').length)
const failedCount = computed(() => results.value.filter((r) => r.status === 'Failed').length)

function handleFileUpload(event) {
	csvError.value = ''
	parsedRows.value = []
	costPreview.value = null
	results.value = []

	const file = event.target.files[0]
	if (!file) return

	const reader = new FileReader()
	reader.onload = (e) => {
		try {
			parsedRows.value = parseCSV(e.target.result)
		} catch (err) {
			csvError.value = err.message
		}
	}
	reader.readAsText(file)
}

function parseCSV(text) {
	const lines = text.trim().split('\n')
	if (lines.length < 2) throw new Error('CSV must have a header row and at least one student row')

	const headers = lines[0].split(',').map((h) => h.trim().toLowerCase())
	const emailIdx = headers.indexOf('email')
	const firstIdx = headers.indexOf('first_name')
	const lastIdx = headers.indexOf('last_name')

	if (emailIdx === -1 || firstIdx === -1) {
		throw new Error('CSV must have email and first_name columns')
	}

	const rows = []
	for (let i = 1; i < lines.length; i++) {
		const cols = lines[i].split(',').map((c) => c.trim())
		const email = cols[emailIdx] || ''
		const firstName = cols[firstIdx] || ''
		if (!email || !firstName) {
			throw new Error(`Row ${i + 1}: email and first_name are required`)
		}
		rows.push({
			email,
			first_name: firstName,
			last_name: lastIdx !== -1 ? cols[lastIdx] || '' : '',
		})
	}
	return rows
}

async function fetchCostPreview() {
	results.value = []
	if (!documentName.value) {
		costPreview.value = null
		return
	}
	try {
		const result = await call('lms.lms.api.create_bulk_enrollment', {
			students_csv: buildCSVString(),
			enroll_type: enrollType.value,
			document_name: documentName.value,
		})

		if (result.free) {
			await loadResults(result.name)
		} else {
			costPreview.value = {
				unit_price: result.unit_price,
				currency: result.currency,
				total_amount: result.total_amount,
				bulk_name: result.name,
			}
		}
	} catch (e) {
		toast.error(e.message || __('Failed to fetch pricing'))
	}
}

function buildCSVString() {
	const header = 'email,first_name,last_name'
	const rows = parsedRows.value.map((r) => `${r.email},${r.first_name},${r.last_name}`)
	return [header, ...rows].join('\n')
}

async function submitEnrollment() {
	if (!costPreview.value) return
	submitting.value = true
	try {
		if (costPreview.value.unit_price === 0) {
			await loadResults(costPreview.value.bulk_name)
		} else {
			const paymentUrl = await call('lms.lms.payments.get_payment_link', {
				doctype: 'LMS Bulk Enrollment',
				docname: costPreview.value.bulk_name,
				address: {},
				payment_for_certificate: 0,
			})
			window.location.href = paymentUrl
		}
	} catch (e) {
		toast.error(e.message || __('Something went wrong'))
	} finally {
		submitting.value = false
	}
}

async function loadResults(bulkName) {
	const doc = await call('frappe.client.get', {
		doctype: 'LMS Bulk Enrollment',
		name: bulkName,
	})
	results.value = (doc.students || []).map((s) => ({
		email: s.email,
		status: s.status,
	}))
	costPreview.value = null
}
</script>

<style scoped>
.success-pop-enter-active {
	animation: pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes pop-in {
	from {
		opacity: 0;
		transform: scale(0.92) translateY(8px);
	}
	to {
		opacity: 1;
		transform: scale(1) translateY(0);
	}
}
</style>
