# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.permissions import add_permission, update_permission_property

from hrms.setup import get_custom_fields


def execute():
	"""PeoplePay360: roles, custom fields, and permission matrix."""
	create_peoplepay_roles()
	create_custom_fields(get_custom_fields(), update=True)
	setup_peoplepay_permissions()
	ensure_employee_kanban_board()


def create_peoplepay_roles():
	for role in ("HR Payroll User", "HR Payroll Manager", "HR Manager", "HR User", "Employee"):
		if not frappe.db.exists("Role", role):
			frappe.get_doc(
				{"doctype": "Role", "role_name": role, "desk_access": 1, "is_custom": 1}
			).insert(ignore_permissions=True)


def setup_peoplepay_permissions():
	# Employment Contract already has DocType permissions; ensure payroll roles exist on key docs
	matrix = {
		"HR Payroll User": {
			"Payroll Entry": {"read": 1, "write": 1, "create": 1, "submit": 1},
			"Salary Slip": {"read": 1, "write": 1, "create": 1, "submit": 1},
			"Salary Structure": {"read": 1},
			"Salary Component": {"read": 1},
			"Employment Contract": {"read": 1, "write": 1, "create": 1},
			"Employee": {"read": 1},
			"Attendance": {"read": 1, "write": 1, "create": 1},
			"Leave Application": {"read": 1, "write": 1, "create": 1},
			"Leave Allocation": {"read": 1},
			"Leave Type": {"read": 1},
			"Working Schedule": {"read": 1},
		},
		"HR Payroll Manager": {
			"Payroll Entry": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1},
			"Salary Slip": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1},
			"Salary Structure": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
			"Salary Component": {"read": 1, "write": 1, "create": 1, "delete": 1},
			"Employment Contract": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
			"Employee": {"read": 1, "write": 1, "create": 1},
			"Working Schedule": {"read": 1, "write": 1, "create": 1},
		},
		"HR Manager": {
			"Employment Contract": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
			"Working Schedule": {"read": 1, "write": 1, "create": 1, "delete": 1},
			"Employee": {"read": 1, "write": 1, "create": 1, "delete": 1},
			"Attendance": {"read": 1, "write": 1, "create": 1, "delete": 1},
			"Leave Application": {"read": 1, "write": 1, "create": 1, "submit": 1},
			"Leave Allocation": {"read": 1, "write": 1, "create": 1, "submit": 1},
			"Leave Type": {"read": 1, "write": 1, "create": 1},
		},
		"Employee": {
			"Employment Contract": {"read": 1},
			"Working Schedule": {"read": 1},
			"Attendance": {"read": 1, "write": 1, "create": 1},
			"Leave Application": {"read": 1, "write": 1, "create": 1},
			"Leave Allocation": {"read": 1},
			"Leave Type": {"read": 1},
			"Employee": {"read": 1},
		},
	}

	for role, doctypes in matrix.items():
		for doctype, perms in doctypes.items():
			if not frappe.db.exists("DocType", doctype):
				continue
			try:
				add_permission(doctype, role, 0)
			except Exception:
				pass
			for ptype, value in perms.items():
				try:
					update_permission_property(doctype, role, 0, ptype, value)
				except Exception:
					pass


def ensure_employee_kanban_board():
	"""Create a Status Kanban board for Employee if missing."""
	if frappe.db.exists("Kanban Board", "Employee Status"):
		return
	if not frappe.db.exists("DocType", "Kanban Board"):
		return
	try:
		frappe.get_doc(
			{
				"doctype": "Kanban Board",
				"kanban_board_name": "Employee Status",
				"reference_doctype": "Employee",
				"field_name": "status",
				"private": 0,
				"columns": [
					{"column_name": "Active", "status": "Active"},
					{"column_name": "Inactive", "status": "Inactive"},
					{"column_name": "Suspended", "status": "Suspended"},
					{"column_name": "Left", "status": "Left"},
				],
			}
		).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="PeoplePay360 Employee Kanban setup")
