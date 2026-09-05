import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class EmploymentContract(Document):
	def validate(self):
		self.validate_dates()
		self.validate_employee()
		self.validate_no_overlap()
		self.set_status_from_dates()

	def validate_dates(self):
		if self.end_date and getdate(self.end_date) < getdate(self.start_date):
			frappe.throw(_("End Date cannot be before Start Date."))

	def validate_employee(self):
		if not frappe.db.exists("Employee", self.employee):
			frappe.throw(_("The selected employee does not exist."))

	def validate_no_overlap(self):
		if self.status in ("Cancelled", "Expired"):
			return
		filters = {"employee": self.employee, "name": ["!=", self.name], "status": ["in", ["Draft", "Active"]]}
		for contract in frappe.get_all("Employment Contract", filters=filters, fields=["name", "start_date", "end_date"]):
			other_end = getdate(contract.end_date) if contract.end_date else None
			this_end = getdate(self.end_date) if self.end_date else None
			if (not this_end or getdate(contract.start_date) <= this_end) and (not other_end or getdate(self.start_date) <= other_end):
				frappe.throw(_("Contract {0} overlaps this contract for the selected employee.").format(contract.name))

	def set_status_from_dates(self):
		if self.status != "Cancelled" and self.end_date and getdate(self.end_date) < getdate(today()):
			self.status = "Expired"


@frappe.whitelist()
def get_contract_for_period(employee: str, start_date: str, end_date: str):
		start_date = getdate(start_date)
		end_date = getdate(end_date)
		if start_date > end_date:
			frappe.throw(_("Contract period start cannot be after the end date."))
		contracts = frappe.get_all("Employment Contract", filters={"employee": employee, "status": ["in", ["Draft", "Active"]]}, fields=["name", "start_date", "end_date", "wage", "currency", "salary_structure"])
		applicable = [c for c in contracts if getdate(c.start_date) <= end_date and (not c.end_date or getdate(c.end_date) >= start_date)]
		if len(applicable) > 1:
			frappe.throw(_("More than one contract applies to employee {0} in this period.").format(employee))
		return applicable[0] if applicable else None
