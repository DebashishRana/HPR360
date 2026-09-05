from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_time


class WorkingSchedule(Document):
	def validate(self):
		working_days = [row for row in self.working_days if row.is_working_day]
		if not working_days:
			frappe.throw(_("Add at least one working day."))

		seen_days = set()
		for row in working_days:
			if row.day in seen_days:
				frappe.throw(_("{0} can only appear once in a schedule.").format(row.day))
			seen_days.add(row.day)
			self.validate_day(row)

	def validate_day(self, row):
		if not row.start_time or not row.end_time:
			frappe.throw(_("Start Time and End Time are required for {0}.").format(row.day))

		start = get_time(row.start_time)
		end = get_time(row.end_time)
		if start == end:
			frappe.throw(_("Start Time and End Time cannot be the same for {0}.").format(row.day))

		start_dt = datetime.combine(datetime.today(), start)
		end_dt = datetime.combine(datetime.today(), end)
		if end_dt <= start_dt:
			end_dt += timedelta(days=1)

		duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
		if row.break_minutes and row.break_minutes >= duration_minutes:
			frappe.throw(_("Break must be shorter than the shift duration for {0}.").format(row.day))
		if row.break_minutes and row.break_minutes < 0:
			frappe.throw(_("Break cannot be negative for {0}.").format(row.day))
