# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

"""Minimal live records so the Assistant has something to answer about."""

from __future__ import annotations

from datetime import timedelta

import frappe
from frappe.utils import add_days, nowdate, today


def seed_assistant_demo_data() -> dict:
	"""Create a handful of employees / leave / attendance if the site is empty."""
	company = frappe.db.get_value("Company", {}, "name") or "PeoplePay360 Demo"
	if not frappe.db.exists("Company", company):
		doc = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": company,
				"abbr": "PPD",
				"default_currency": "USD",
				"country": "United States",
			}
		)
		doc.insert(ignore_permissions=True)
		company = doc.name

	# Departments
	depts = {}
	for d in ("Engineering", "HR", "Finance"):
		name = frappe.db.get_value("Department", {"department_name": d, "company": company}, "name")
		if not name:
			dep = frappe.get_doc(
				{"doctype": "Department", "department_name": d, "company": company}
			).insert(ignore_permissions=True)
			name = dep.name
		depts[d] = name

	people = [
		("PP-EMP-001", "Alex Employee", "alex.employee@example.com", "Engineering", "Software Engineer"),
		("PP-EMP-002", "Blair Employee", "blair.employee@example.com", "Engineering", "QA Engineer"),
		("PP-EMP-003", "Casey Employee", "casey.employee@example.com", "HR", "HR Coordinator"),
		("PP-EMP-004", "Dana Manager", "hr.manager@example.com", "HR", "HR Manager"),
		("PP-EMP-005", "Evan Payroll", "payroll.user@example.com", "Finance", "Payroll Analyst"),
	]

	created = []
	for emp_id, full_name, user_id, dept, designation in people:
		if frappe.db.exists("Employee", emp_id):
			continue
		# designation
		if designation and not frappe.db.exists("Designation", designation):
			frappe.get_doc({"doctype": "Designation", "designation_name": designation}).insert(
				ignore_permissions=True
			)
		first, last = full_name.split(" ", 1)
		emp = frappe.get_doc(
			{
				"doctype": "Employee",
				"name": emp_id,
				"naming_series": "PP-EMP-",
				"first_name": first,
				"last_name": last,
				"employee_name": full_name,
				"status": "Active",
				"company": company,
				"department": depts.get(dept),
				"designation": designation,
				"date_of_joining": add_days(today(), -400),
				"date_of_birth": add_days(today(), -11000),
				"gender": "Other",
				"user_id": user_id if frappe.db.exists("User", user_id) else None,
				"create_user_permission": 0,
			}
		)
		try:
			emp.insert(ignore_permissions=True)
			created.append(emp.name)
		except Exception:
			# naming series may ignore explicit name — try without name
			emp = frappe.get_doc(
				{
					"doctype": "Employee",
					"first_name": first,
					"last_name": last,
					"status": "Active",
					"company": company,
					"department": depts.get(dept),
					"designation": designation,
					"date_of_joining": add_days(today(), -400),
					"date_of_birth": add_days(today(), -11000),
					"gender": "Other",
					"user_id": user_id if frappe.db.exists("User", user_id) else None,
					"create_user_permission": 0,
				}
			)
			emp.insert(ignore_permissions=True)
			created.append(emp.name)

	# Leave Type
	if not frappe.db.exists("Leave Type", "Annual Leave"):
		frappe.get_doc(
			{
				"doctype": "Leave Type",
				"leave_type_name": "Annual Leave",
				"max_leaves_allowed": 20,
				"is_carry_forward": 1,
			}
		).insert(ignore_permissions=True)

	emps = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "company"], limit=10)
	# Allocations + one open leave
	for e in emps[:3]:
		if not frappe.db.exists(
			"Leave Allocation", {"employee": e.name, "leave_type": "Annual Leave", "docstatus": 1}
		):
			alloc = frappe.get_doc(
				{
					"doctype": "Leave Allocation",
					"employee": e.name,
					"leave_type": "Annual Leave",
					"from_date": f"{frappe.utils.getdate().year}-01-01",
					"to_date": f"{frappe.utils.getdate().year}-12-31",
					"new_leaves_allocated": 20,
					"carry_forward": 0,
				}
			)
			alloc.insert(ignore_permissions=True)
			alloc.submit()

	# One pending leave from first employee
	if emps and not frappe.db.exists("Leave Application", {"employee": emps[0].name, "status": "Open"}):
		la = frappe.get_doc(
			{
				"doctype": "Leave Application",
				"employee": emps[0].name,
				"leave_type": "Annual Leave",
				"from_date": add_days(today(), 7),
				"to_date": add_days(today(), 8),
				"status": "Open",
				"company": emps[0].company or company,
				"description": "Demo leave for Assistant",
			}
		)
		try:
			la.insert(ignore_permissions=True)
		except Exception as exc:
			frappe.log_error(title="Assistant leave seed", message=str(exc))

	# Attendance last few days
	for e in emps[:3]:
		for offset in range(1, 6):
			d = add_days(today(), -offset)
			if frappe.db.exists("Attendance", {"employee": e.name, "attendance_date": d}):
				continue
			try:
				frappe.get_doc(
					{
						"doctype": "Attendance",
						"employee": e.name,
						"attendance_date": d,
						"status": "Present" if offset % 4 else "Absent",
						"company": e.company or company,
					}
				).insert(ignore_permissions=True)
			except Exception:
				pass

	frappe.db.commit()
	return {
		"status": "ok",
		"company": company,
		"employees_created": created,
		"active_employees": frappe.db.count("Employee", {"status": "Active"}),
		"pending_leave": frappe.db.count("Leave Application", {"status": "Open"}),
	}
