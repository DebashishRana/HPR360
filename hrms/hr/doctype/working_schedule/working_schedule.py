from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_time, getdate


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
		self.weekly_hours = round(sum(self.get_day_hours(row) for row in working_days), 2)
		self.working_day_count = len(working_days)

	def get_day_hours(self, row):
		start = get_time(row.start_time)
		end = get_time(row.end_time)
		start_dt = datetime.combine(datetime.today(), start)
		end_dt = datetime.combine(datetime.today(), end)
		if end_dt <= start_dt:
			end_dt += timedelta(days=1)
		return max(0, (end_dt - start_dt).total_seconds() / 3600 - (row.break_minutes or 0) / 60)

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


@frappe.whitelist()
def get_working_schedule_list():
	schedules = frappe.get_all("Working Schedule", fields=["name", "schedule_name", "schedule_type", "company", "is_active", "weekly_hours", "working_day_count", "modified"], order_by="modified desc", limit_page_length=100)
	for schedule in schedules:
		schedule.assigned_employee_count = frappe.db.count("Working Schedule Assignment", {"working_schedule": schedule.name, "status": "Active"}) if frappe.db.exists("DocType", "Working Schedule Assignment") else 0
	return schedules


def get_working_schedule_for_employee(employee, date):
	if not frappe.db.exists("DocType", "Working Schedule Assignment"):
		return None
	date = getdate(date)
	assignments = frappe.get_all("Working Schedule Assignment", filters={"employee": employee, "status": "Active", "start_date": ["<=", date]}, fields=["working_schedule", "end_date"], order_by="start_date desc")
	for assignment in assignments:
		if not assignment.end_date or getdate(assignment.end_date) >= date:
			return frappe.get_cached_doc("Working Schedule", assignment.working_schedule)
	return None


def apply_working_schedule_to_attendance(doc, event=None):
	if not doc.employee or not doc.attendance_date or doc.shift:
		return
	schedule = get_working_schedule_for_employee(doc.employee, doc.attendance_date)
	if not schedule:
		return
	day = getdate(doc.attendance_date).strftime("%A")
	row = next((row for row in schedule.working_days if row.day == day and row.is_working_day), None)
	if row:
		doc.standard_working_hours = schedule.get_day_hours(row)
