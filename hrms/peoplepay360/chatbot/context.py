# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

"""Live PeoplePay360 context snapshots for the HR assistant."""

from __future__ import annotations

from collections import defaultdict

import frappe
from frappe.utils import add_days, cint, flt, formatdate, getdate, today


def _count(doctype: str, filters: dict | None = None) -> int:
	try:
		return cint(frappe.db.count(doctype, filters or {}))
	except Exception:
		return 0


def build_org_snapshot(capabilities: dict) -> dict:
	"""Aggregate live HR/Payroll metrics the assistant can ground answers on."""
	snap: dict = {
		"as_of": today(),
		"company": frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name"),
	}

	# Headcount
	snap["employees"] = {
		"active": _count("Employee", {"status": "Active"}),
		"left": _count("Employee", {"status": "Left"}),
		"total": _count("Employee"),
	}

	# By department
	dept_rows = frappe.db.sql(
		"""
		select ifnull(department, 'Unassigned') as department, count(*) as cnt
		from `tabEmployee`
		where status = 'Active'
		group by ifnull(department, 'Unassigned')
		order by cnt desc
		limit 12
		""",
		as_dict=True,
	)
	snap["headcount_by_department"] = {r.department: cint(r.cnt) for r in dept_rows}

	# Contracts
	if frappe.db.exists("DocType", "Employment Contract"):
		snap["contracts"] = {
			"active": _count("Employment Contract", {"status": "Active"}),
			"expired": _count("Employment Contract", {"status": "Expired"}),
			"draft": _count("Employment Contract", {"status": "Draft"}),
		}
		# Overlap risk: employees with >1 Active
		overlaps = frappe.db.sql(
			"""
			select employee, count(*) as cnt
			from `tabEmployment Contract`
			where status = 'Active'
			group by employee
			having count(*) > 1
			limit 20
			""",
			as_dict=True,
		)
		snap["contracts"]["overlap_warnings"] = [
			{"employee": r.employee, "active_contracts": cint(r.cnt)} for r in overlaps
		]

	# Attendance (last 7 / 30 days)
	since7 = add_days(today(), -7)
	since30 = add_days(today(), -30)
	att = {}
	for label, since in (("last_7_days", since7), ("last_30_days", since30)):
		rows = frappe.db.sql(
			"""
			select status, count(*) as cnt
			from `tabAttendance`
			where attendance_date >= %s and docstatus < 2
			group by status
			""",
			since,
			as_dict=True,
		)
		att[label] = {r.status: cint(r.cnt) for r in rows}
	snap["attendance"] = att

	# Time off
	snap["time_off"] = {
		"pending_requests": _count("Leave Application", {"status": "Open"}),
		"approved_requests": _count("Leave Application", {"status": "Approved"}),
		"rejected_requests": _count("Leave Application", {"status": "Rejected"}),
		"active_allocations": _count("Leave Allocation", {"docstatus": 1}),
	}
	pending = frappe.get_all(
		"Leave Application",
		filters={"status": "Open"},
		fields=["name", "employee", "employee_name", "leave_type", "from_date", "to_date", "total_leave_days"],
		order_by="modified desc",
		limit_page_length=8,
	)
	snap["time_off"]["pending_sample"] = pending

	# Payroll (only if role can view)
	if capabilities.get("can_view_payroll"):
		snap["payroll"] = {
			"salary_structures": _count("Salary Structure", {"is_active": "Yes"}),
			"salary_components": _count("Salary Component"),
			"payslips_draft": _count("Salary Slip", {"docstatus": 0}),
			"payslips_submitted": _count("Salary Slip", {"docstatus": 1}),
			"payroll_entries": _count("Payroll Entry"),
		}
		# Recent net pay
		nets = frappe.db.sql(
			"""
			select sum(net_pay) as total_net, count(*) as slips, avg(net_pay) as avg_net
			from `tabSalary Slip`
			where docstatus = 1 and start_date >= %s
			""",
			add_days(today(), -90),
			as_dict=True,
		)
		if nets:
			snap["payroll"]["last_90_days"] = {
				"total_net": flt(nets[0].total_net),
				"payslips": cint(nets[0].slips),
				"average_net": flt(nets[0].avg_net),
			}
		missing_bank = frappe.db.sql(
			"""
			select count(*) from `tabEmployee`
			where status='Active' and ifnull(bank_ac_no,'')=''
			"""
		)[0][0]
		snap["payroll"]["employees_missing_bank"] = cint(missing_bank)

	# Schedules
	if frappe.db.exists("DocType", "Working Schedule"):
		snap["schedules"] = {
			"active": _count("Working Schedule", {"is_active": 1}),
			"assignments": _count("Working Schedule Assignment", {"status": "Active"})
			if frappe.db.exists("DocType", "Working Schedule Assignment")
			else 0,
		}

	# Recent employees
	snap["recent_employees"] = frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "employee_name", "department", "designation", "date_of_joining"],
		order_by="modified desc",
		limit_page_length=8,
	)

	return snap


def find_employees(query: str, limit: int = 8) -> list[dict]:
	q = f"%{(query or '').strip()}%"
	if len(q) < 3:
		return []
	return frappe.db.sql(
		"""
		select name, employee_name, status, department, designation, user_id, reports_to, company
		from `tabEmployee`
		where employee_name like %(q)s or name like %(q)s or user_id like %(q)s
		order by status = 'Active' desc, modified desc
		limit %(limit)s
		""",
		{"q": q, "limit": limit},
		as_dict=True,
	)


def employee_dossier(employee: str, capabilities: dict) -> dict:
	"""Deep context for one employee (permission-filtered)."""
	if not employee or not frappe.db.exists("Employee", employee):
		return {}
	emp = frappe.get_doc("Employee", employee)
	data = {
		"name": emp.name,
		"employee_name": emp.employee_name,
		"status": emp.status,
		"department": emp.department,
		"designation": emp.designation,
		"reports_to": emp.reports_to,
		"date_of_joining": str(emp.date_of_joining) if emp.date_of_joining else None,
		"company": emp.company,
		"user_id": emp.user_id,
	}

	if frappe.db.exists("DocType", "Employment Contract"):
		data["contracts"] = frappe.get_all(
			"Employment Contract",
			filters={"employee": employee},
			fields=["name", "status", "start_date", "end_date", "wage", "position", "salary_structure"],
			order_by="start_date desc",
			limit_page_length=6,
		)

	data["leave_applications"] = frappe.get_all(
		"Leave Application",
		filters={"employee": employee},
		fields=["name", "leave_type", "from_date", "to_date", "total_leave_days", "status"],
		order_by="from_date desc",
		limit_page_length=8,
	)
	data["leave_allocations"] = frappe.get_all(
		"Leave Allocation",
		filters={"employee": employee, "docstatus": 1},
		fields=["name", "leave_type", "from_date", "to_date", "total_leaves_allocated", "unused_leaves"],
		limit_page_length=8,
	)

	since = add_days(today(), -30)
	att_rows = frappe.db.sql(
		"""
		select status, count(*) as cnt
		from `tabAttendance`
		where employee=%s and attendance_date >= %s and docstatus < 2
		group by status
		""",
		(employee, since),
		as_dict=True,
	)
	data["attendance_30d"] = {r.status: cint(r.cnt) for r in att_rows}

	if capabilities.get("can_view_payroll") or capabilities.get("is_employee_only"):
		data["recent_payslips"] = frappe.get_all(
			"Salary Slip",
			filters={"employee": employee, "docstatus": ["<", 2]},
			fields=["name", "start_date", "end_date", "net_pay", "gross_pay", "docstatus", "status"],
			order_by="start_date desc",
			limit_page_length=5,
		)

	return data


def snapshot_as_text(snap: dict, capabilities: dict) -> str:
	"""Compact text block for LLM / deterministic answers."""
	lines = [
		f"PeoplePay360 live context as of {snap.get('as_of')} (company: {snap.get('company')}).",
		f"Active employees: {snap.get('employees', {}).get('active', 0)} / total {snap.get('employees', {}).get('total', 0)}.",
	]
	if snap.get("headcount_by_department"):
		top = ", ".join(f"{k} ({v})" for k, v in list(snap["headcount_by_department"].items())[:6])
		lines.append(f"Headcount by department: {top}.")
	if snap.get("contracts"):
		c = snap["contracts"]
		lines.append(
			f"Contracts — active: {c.get('active', 0)}, expired: {c.get('expired', 0)}, draft: {c.get('draft', 0)}."
		)
		if c.get("overlap_warnings"):
			lines.append(f"Contract overlap warnings: {len(c['overlap_warnings'])} employee(s).")
	if snap.get("attendance"):
		a7 = snap["attendance"].get("last_7_days") or {}
		lines.append(
			"Attendance last 7 days: "
			+ ", ".join(f"{k}={v}" for k, v in a7.items())
			+ ("." if a7 else "no rows.")
		)
	if snap.get("time_off"):
		t = snap["time_off"]
		lines.append(
			f"Time off — pending: {t.get('pending_requests', 0)}, approved: {t.get('approved_requests', 0)}, "
			f"allocations: {t.get('active_allocations', 0)}."
		)
	if snap.get("payroll") and capabilities.get("can_view_payroll"):
		p = snap["payroll"]
		lines.append(
			f"Payroll — active structures: {p.get('salary_structures', 0)}, submitted slips: {p.get('payslips_submitted', 0)}, "
			f"draft slips: {p.get('payslips_draft', 0)}, missing bank: {p.get('employees_missing_bank', 0)}."
		)
		if p.get("last_90_days"):
			l = p["last_90_days"]
			lines.append(
				f"Last 90 days net pay total: {l.get('total_net', 0):,.2f} across {l.get('payslips', 0)} slips "
				f"(avg {l.get('average_net', 0):,.2f})."
			)
	return "\n".join(lines)
