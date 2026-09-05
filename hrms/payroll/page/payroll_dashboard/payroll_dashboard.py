from collections import Counter, defaultdict
from datetime import timedelta

import frappe
from frappe import _
from frappe.utils import getdate, today


@frappe.whitelist()
def get_payroll_dashboard_data(from_date: str, to_date: str, company: str | None = None, department: str | None = None, employee_type: str | None = None) -> dict:
	from_date, to_date = getdate(from_date), getdate(to_date)
	if not from_date or not to_date or from_date > to_date:
		frappe.throw(_("Select a valid date range."))
	company_filter = {"company": company} if company else {}
	employee_filter = {key: value for key, value in {"company": company, "department": department, "employee_type": employee_type}.items() if value}
	filtered_employee_names = frappe.get_list("Employee", filters={"status": "Active", **employee_filter}, pluck="name", limit_page_length=0)
	employee_scope_filter = {"employee": ["in", filtered_employee_names]} if employee_filter else {}
	slips = frappe.get_list("Salary Slip", filters={"docstatus": 1, "posting_date": ["between", [from_date, to_date]], **company_filter, **employee_scope_filter}, fields=["name", "employee", "employee_name", "net_pay", "posting_date", "currency", "status"], limit_page_length=0)
	entries = frappe.get_list("Payroll Entry", filters={"posting_date": ["between", [from_date, to_date]], **company_filter}, fields=["name", "status", "number_of_employees", "company"], limit_page_length=0)
	attendance = frappe.get_list("Attendance", filters={"attendance_date": ["between", [from_date, to_date]], **company_filter, **employee_scope_filter}, fields=["employee", "status", "working_hours", "late_entry", "early_exit"], limit_page_length=0)
	active_employees = frappe.get_list("Employee", filters={"status": "Active", **employee_filter}, fields=["name", "employee_name", "department", "designation", "bank_ac_no", "company_email"], limit_page_length=0)
	leaves = frappe.get_list("Leave Application", filters={"from_date": ["<=", to_date], "to_date": [">=", from_date], **company_filter}, fields=["employee", "employee_name", "leave_type", "total_leave_days", "status"], limit_page_length=0)
	trend = defaultdict(float)
	department_cost = defaultdict(float)
	employee_pay = {}
	for slip in slips:
		trend[getdate(slip.posting_date).strftime("%Y-%m")] += float(slip.net_pay or 0)
		employee_pay[slip.employee] = slip
		department = frappe.db.get_value("Employee", slip.employee, "department") or _("Unassigned")
		department_cost[department] += float(slip.net_pay or 0)
	status_breakdown = Counter(entry.status or "Draft" for entry in entries)
	attendance_breakdown = Counter(row.status or "Unmarked" for row in attendance)
	department_headcount = Counter(employee.department or _("Unassigned") for employee in active_employees)
	approved_leave_days = sum(float(row.total_leave_days or 0) for row in leaves if row.status == "Approved")
	pending_leave = sum(1 for row in leaves if row.status in ("Open", "Pending Approval"))
	duplicate_counts = Counter(slip.employee for slip in slips)
	return {
		"currency": next((slip.currency for slip in slips if slip.currency), ""),
		"kpis": {"total_net_salary": sum(float(slip.net_pay or 0) for slip in slips), "payslips_generated": len(slips), "average_salary": sum(float(slip.net_pay or 0) for slip in slips) / len(slips) if slips else 0, "approved_time_off": approved_leave_days, "active_employees": len(active_employees), "attendance_health": attendance_health(attendance_breakdown)},
		"trend": [{"month": month, "value": trend[month]} for month in sorted(trend)],
		"salary_by_department": [{"department": name, "value": value} for name, value in sorted(department_cost.items(), key=lambda item: item[1], reverse=True)],
		"department_breakdown": [{"department": name, "headcount": department_headcount[name], "salary": department_cost.get(name, 0)} for name in sorted(set(department_headcount) | set(department_cost))],
		"status_breakdown": dict(status_breakdown),
		"attendance": {"breakdown": dict(attendance_breakdown), "late": sum(1 for row in attendance if row.late_entry), "early_exit": sum(1 for row in attendance if row.early_exit), "overtime": sum(max(float(row.working_hours or 0) - 8, 0) for row in attendance), "coverage": round(len(attendance) / max(len(active_employees), 1) * 100, 1)},
		"time_off": {"approved_days": approved_leave_days, "pending_requests": pending_leave, "leave_balances": get_leave_balances(company_filter)},
		"employee_pay": [{"employee": employee, "employee_name": slip.employee_name, "department": frappe.db.get_value("Employee", employee, "department") or _("Unassigned"), "net_pay": slip.net_pay, "currency": slip.currency, "status": slip.status or "Paid"} for employee, slip in sorted(employee_pay.items(), key=lambda item: item[1].net_pay or 0, reverse=True)],
		"warnings": {"queued_payruns": status_breakdown.get("Queued", 0), "failed_payruns": status_breakdown.get("Failed", 0), "unmarked_attendance": attendance_breakdown.get("Unmarked", 0), "duplicate_payslips": sum(1 for count in duplicate_counts.values() if count > 1), "contract_attention": get_contract_attention(active_employees), "missing_employee_info": sum(1 for employee in active_employees if not employee.bank_ac_no or not employee.company_email)},
	}


def get_leave_balances(company_filter):
	allocations = frappe.get_list("Leave Allocation", filters={"docstatus": 1, "to_date": [">=", getdate(today())], **company_filter}, fields=["leave_type", "new_leaves_allocated", "total_leaves_allocated", "leaves_taken"], limit_page_length=0)
	result = defaultdict(lambda: {"allocated": 0, "taken": 0})
	for row in allocations:
		result[row.leave_type]["allocated"] += float(row.total_leaves_allocated or row.new_leaves_allocated or 0)
		result[row.leave_type]["taken"] += float(row.leaves_taken or 0)
	return [{"leave_type": name, "available": values["allocated"] - values["taken"]} for name, values in result.items()]


def get_contract_attention(employees):
	if not employees:
		return 0
	if not frappe.db.exists("DocType", "Employment Contract"):
		return 0
	threshold = getdate(today()) + timedelta(days=30)
	return len(frappe.get_list("Employment Contract", filters={"employee": ["in", [employee.name for employee in employees]], "status": "Active", "end_date": ["between", [getdate(today()), threshold]]}, pluck="name"))


def attendance_health(breakdown):
	total = sum(breakdown.values())
	return 100 if not total else round((breakdown.get("Present", 0) / total) * 100, 1)
