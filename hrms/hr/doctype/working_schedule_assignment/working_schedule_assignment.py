import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class WorkingScheduleAssignment(Document):
	def validate(self):
		if self.end_date and getdate(self.end_date) < getdate(self.start_date):
			frappe.throw(_("Effective To cannot be before Effective From."))
		if not frappe.db.exists("Employee", self.employee):
			frappe.throw(_("The selected employee does not exist."))
		self.company = frappe.db.get_value("Employee", self.employee, "company")
		if self.status != "Active":
			return
		filters = {"employee": self.employee, "status": "Active", "name": ["!=", self.name]}
		for other in frappe.get_all("Working Schedule Assignment", filters=filters, fields=["name", "start_date", "end_date"]):
			other_end = getdate(other.end_date) if other.end_date else None
			this_end = getdate(self.end_date) if self.end_date else None
			if (not this_end or getdate(other.start_date) <= this_end) and (not other_end or getdate(self.start_date) <= other_end):
				frappe.throw(_("This assignment overlaps {0} for employee {1}.").format(other.name, self.employee))
