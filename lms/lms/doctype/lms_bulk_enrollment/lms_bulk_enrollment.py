# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LMSBulkEnrollment(Document):
	def on_payment_authorized(self, payment_status):
		if payment_status in ("Authorized", "Completed"):
			from lms.lms.utils import complete_bulk_enrollment

			complete_bulk_enrollment(self.name, None)
