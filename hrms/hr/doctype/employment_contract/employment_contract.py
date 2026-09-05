# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class EmploymentContract(Document):
	def validate(self):
		self.validate_dates()
		self.set_active_flag()
		self.validate_no_overlapping_active_contracts()

	def on_submit(self):
		self.db_set("status", "Active" if self.is_currently_active() else "Expired")
		self.db_set("is_active", 1 if self.is_currently_active() else 0)
		self.validate_no_overlapping_active_contracts(on_submit=True)

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		self.db_set("is_active", 0)

	def validate_dates(self):
		if self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("Contract End Date cannot be before Start Date."))

	def is_currently_active(self, on_date=None):
		on_date = getdate(on_date or frappe.utils.today())
		if getdate(self.start_date) > on_date:
			return False
		if self.end_date and getdate(self.end_date) < on_date:
			return False
		return True

	def set_active_flag(self):
		if self.docstatus == 2 or self.status == "Cancelled":
			self.is_active = 0
			return
		self.is_active = 1 if self.is_currently_active() else 0
		if self.docstatus == 1:
			self.status = "Active" if self.is_active else "Expired"

	def validate_no_overlapping_active_contracts(self, on_submit=False):
		"""Block concurrent active contracts for the same employee."""
		if self.docstatus == 2:
			return

		filters = {
			"employee": self.employee,
			"docstatus": 1,
			"name": ["!=", self.name or ""],
			"status": ["in", ["Active", "Draft"]],
		}
		others = frappe.get_all(
			"Employment Contract",
			filters=filters,
			fields=["name", "start_date", "end_date", "status", "is_active"],
		)
		start = getdate(self.start_date)
		end = getdate(self.end_date) if self.end_date else None

		for row in others:
			other_start = getdate(row.start_date)
			other_end = getdate(row.end_date) if row.end_date else None
			# overlap if ranges intersect
			if other_end and other_end < start:
				continue
			if end and end < other_start:
				continue
			frappe.throw(
				_(
					"Employee {0} already has an overlapping Employment Contract {1}. "
					"Only one active contract is allowed for a given period."
				).format(frappe.bold(self.employee), frappe.bold(row.name))
			)


@frappe.whitelist()
def get_applicable_contract(employee: str, on_date: str | None = None, salary_structure: str | None = None):
	"""Return the employment contract applicable for payroll on a given date."""
	on_date = getdate(on_date or frappe.utils.today())
	filters = {
		"employee": employee,
		"docstatus": 1,
		"start_date": ["<=", on_date],
		"status": ["!=", "Cancelled"],
	}
	contracts = frappe.get_all(
		"Employment Contract",
		filters=filters,
		fields=[
			"name",
			"employee",
			"start_date",
			"end_date",
			"wage",
			"currency",
			"salary_structure",
			"department",
			"designation",
			"working_schedule",
			"payroll_frequency",
			"status",
			"is_active",
		],
		order_by="start_date desc",
	)
	for contract in contracts:
		if contract.end_date and getdate(contract.end_date) < on_date:
			continue
		if salary_structure and contract.salary_structure != salary_structure:
			continue
		return contract
	return None
