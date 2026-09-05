from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import getdate


@frappe.whitelist()
def get_payroll_dashboard_data(
	from_date: str,
	to_date: str,
	company: str | None = None,
	department: str | None = None,
	employment_type: str | None = None,
) -> dict:
	from_date = getdate(from_date)
	to_date = getdate(to_date)
	if from_date > to_date:
		frappe.throw(_("From Date cannot be after To Date."))

	company_filter = {"company": company} if company else {}
	employee_name_filter = {}
	if department or employment_type:
		emp_filters = {**company_filter}
		if department:
			emp_filters["department"] = department
		if employment_type:
			emp_filters["employment_type"] = employment_type
		employee_names = frappe.get_all("Employee", filters=emp_filters, pluck="name")
		if not employee_names:
			return empty_dashboard()
		employee_name_filter = {"employee": ["in", employee_names]}

	slip_filters = {
		"docstatus": 1,
		"posting_date": ["between", [from_date, to_date]],
		**company_filter,
		**employee_name_filter,
	}
	slips = frappe.get_list(
		"Salary Slip",
		filters=slip_filters,
		fields=["name", "net_pay", "gross_pay", "total_deduction", "posting_date", "currency", "employee", "department"],
		limit_page_length=0,
	)

	entry_filters = {"posting_date": ["between", [from_date, to_date]], **company_filter}
	entries = frappe.get_list(
		"Payroll Entry",
		filters=entry_filters,
		fields=["name", "status", "number_of_employees", "company"],
		limit_page_length=0,
	)

	employee_filters = {"status": "Active", **company_filter}
	if department:
		employee_filters["department"] = department
	if employment_type:
		employee_filters["employment_type"] = employment_type
	active_employees = frappe.db.count("Employee", employee_filters)

	attendance_filters = {
		"attendance_date": ["between", [from_date, to_date]],
		**company_filter,
		**employee_name_filter,
	}
	attendance = frappe.get_list(
		"Attendance",
		filters=attendance_filters,
		fields=["status", "late_entry", "early_exit", "in_time", "out_time", "modified_by", "owner"],
		limit_page_length=0,
	)

	approved_leave_filters = {
		"status": "Approved",
		"from_date": ["<=", to_date],
		"to_date": [">=", from_date],
		**company_filter,
		**employee_name_filter,
	}
	approved_time_off = frappe.db.count("Leave Application", approved_leave_filters)
	pending_time_off = frappe.db.count(
		"Leave Application",
		{
			"status": "Open",
			"from_date": ["<=", to_date],
			"to_date": [">=", from_date],
			**company_filter,
			**employee_name_filter,
		},
	)

	trend = defaultdict(float)
	dept_cost = defaultdict(float)
	dept_headcount = defaultdict(set)
	for slip in slips:
		month = getdate(slip.posting_date).strftime("%Y-%m")
		trend[month] += float(slip.net_pay or 0)
		dept = slip.department or _("Unassigned")
		dept_cost[dept] += float(slip.net_pay or 0)
		dept_headcount[dept].add(slip.employee)

	status_breakdown = defaultdict(int)
	for entry in entries:
		status_breakdown[entry.status or "Draft"] += 1

	attendance_breakdown = defaultdict(int)
	late = missing_checkout = manual_edits = overtime = 0
	for row in attendance:
		attendance_breakdown[row.status or "Unmarked"] += 1
		if row.late_entry:
			late += 1
		if row.in_time and not row.out_time:
			missing_checkout += 1
		if row.modified_by and row.owner and row.modified_by != row.owner:
			manual_edits += 1

	# Overtime slips in period
	overtime = frappe.db.count(
		"Overtime Slip",
		{
			"docstatus": 1,
			"posting_date": ["between", [from_date, to_date]],
			**company_filter,
			**employee_name_filter,
		},
	) if frappe.db.exists("DocType", "Overtime Slip") else 0

	# Contract attention: active employees without applicable contract
	contract_attention = 0
	if frappe.db.exists("DocType", "Employment Contract"):
		from hrms.hr.doctype.employment_contract.employment_contract import get_applicable_contract

		for emp in frappe.get_all("Employee", filters=employee_filters, pluck="name"):
			if not get_applicable_contract(emp, on_date=to_date):
				contract_attention += 1

	# Duplicate payslips warning
	duplicate_payslips = frappe.db.sql(
		"""
		select count(*) from (
			select employee from `tabSalary Slip`
			where docstatus=1 and posting_date between %s and %s
			group by employee, start_date, end_date
			having count(*) > 1
		) t
		""",
		(from_date, to_date),
	)[0][0]

	missing_bank = frappe.db.sql(
		"""
		select count(distinct ss.employee)
		from `tabSalary Slip` ss
		inner join `tabEmployee` e on e.name = ss.employee
		where ss.docstatus = 1 and ss.posting_date between %s and %s
			and (ifnull(e.bank_name,'')='' or ifnull(e.bank_ac_no,'')='')
		""",
		(from_date, to_date),
	)[0][0]

	return {
		"currency": next((slip.currency for slip in slips if slip.currency), ""),
		"kpis": {
			"total_net_salary": sum(float(slip.net_pay or 0) for slip in slips),
			"payslips_generated": len(slips),
			"average_salary": (sum(float(slip.net_pay or 0) for slip in slips) / len(slips)) if slips else 0,
			"approved_time_off": approved_time_off,
			"pending_time_off": pending_time_off,
			"active_employees": active_employees,
			"attendance_health": attendance_health(attendance_breakdown),
		},
		"status_breakdown": dict(status_breakdown),
		"attendance_breakdown": dict(attendance_breakdown),
		"attendance_overview": {
			"Present": attendance_breakdown.get("Present", 0),
			"Absent": attendance_breakdown.get("Absent", 0),
			"On Leave": attendance_breakdown.get("On Leave", 0),
			"Half Day": attendance_breakdown.get("Half Day", 0),
			"Late": late,
			"Overtime": overtime,
			"Missing Check-outs": missing_checkout,
			"Manual Edits": manual_edits,
		},
		"department_breakdown": [
			{
				"department": dept,
				"salary": dept_cost[dept],
				"headcount": len(dept_headcount[dept]),
			}
			for dept in sorted(dept_cost.keys())
		],
		"trend": [{"month": month, "value": trend[month]} for month in sorted(trend)],
		"warnings": {
			"queued_payruns": status_breakdown.get("Queued", 0),
			"failed_payruns": status_breakdown.get("Failed", 0),
			"unmarked_attendance": attendance_breakdown.get("Unmarked", 0),
			"missing_bank_details": missing_bank,
			"duplicate_payslips": duplicate_payslips,
			"contract_attention": contract_attention,
		},
	}


def empty_dashboard():
	return {
		"currency": "",
		"kpis": {
			"total_net_salary": 0,
			"payslips_generated": 0,
			"average_salary": 0,
			"approved_time_off": 0,
			"pending_time_off": 0,
			"active_employees": 0,
			"attendance_health": 100,
		},
		"status_breakdown": {},
		"attendance_breakdown": {},
		"attendance_overview": {},
		"department_breakdown": [],
		"trend": [],
		"warnings": {},
	}


def attendance_health(breakdown: dict) -> float:
	total = sum(breakdown.values())
	if not total:
		return 100
	return round((breakdown.get("Present", 0) / total) * 100, 1)
