import frappe
from frappe.tests.utils import FrappeTestCase


class TestWorkingSchedule(FrappeTestCase):
	def test_weekly_hours_include_breaks(self):
		doc = frappe.get_doc({
			"doctype": "Working Schedule",
			"schedule_name": "Test Weekly Hours",
			"schedule_type": "Fixed Weekly",
			"working_days": [
				{"day": "Monday", "is_working_day": 1, "start_time": "09:00:00", "end_time": "17:00:00", "break_minutes": 60},
				{"day": "Tuesday", "is_working_day": 1, "start_time": "22:00:00", "end_time": "06:00:00", "break_minutes": 30},
			],
		})
		doc.validate()
		self.assertEqual(doc.weekly_hours, 14.5)
		self.assertEqual(doc.working_day_count, 2)

	def test_break_cannot_equal_shift_duration(self):
		doc = frappe.get_doc({"doctype": "Working Schedule", "working_days": [{"day": "Monday", "is_working_day": 1, "start_time": "09:00:00", "end_time": "17:00:00", "break_minutes": 480}]})
		self.assertRaises(frappe.ValidationError, doc.validate)

	def test_assignment_rejects_invalid_period(self):
		doc = frappe.get_doc({"doctype": "Working Schedule Assignment", "employee": "missing", "working_schedule": "missing", "start_date": "2026-06-10", "end_date": "2026-06-01"})
		self.assertRaises(frappe.ValidationError, doc.validate)
