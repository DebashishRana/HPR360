from collections import defaultdict
import frappe
from frappe import _
from frappe.utils import getdate


@frappe.whitelist()
def get_payroll_dashboard_data(from_date: str, to_date: str, company: str | None = None) -> dict:
	from_date = getdate(from_date)
	to_date = getdate(to_date)
	if from_date > to_date:
		frappe.throw(_("From Date cannot be after To Date."))

	company_filter = {"company": company} if company else {}
	slip_filters = {"docstatus": 1, "posting_date": ["between", [from_date, to_date]], **company_filter}
	slips = frappe.get_list(
		"Salary Slip",
		filters=slip_filters,
		fields=["name", "net_pay", "gross_pay", "total_deduction", "posting_date", "currency"],
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
	active_employees = frappe.db.count("Employee", employee_filters)

	attendance_filters = {"attendance_date": ["between", [from_date, to_date]], **company_filter}
	attendance = frappe.get_list("Attendance", filters=attendance_filters, fields=["status"], limit_page_length=0)
	approved_leave_filters = {
		"status": "Approved",
		"from_date": ["<=", to_date],
		"to_date": [">=", from_date],
		**company_filter,
	}
	approved_time_off = frappe.db.count("Leave Application", approved_leave_filters)

	trend = defaultdict(float)
	for slip in slips:
		month = getdate(slip.posting_date).strftime("%Y-%m")
		trend[month] += float(slip.net_pay or 0)

	status_breakdown = defaultdict(int)
	for entry in entries:
		status_breakdown[entry.status or "Draft"] += 1

	attendance_breakdown = defaultdict(int)
	for row in attendance:
		attendance_breakdown[row.status or "Unmarked"] += 1

	return {
		"currency": next((slip.currency for slip in slips if slip.currency), ""),
		"kpis": {
			"total_net_salary": sum(float(slip.net_pay or 0) for slip in slips),
			"payslips_generated": len(slips),
			"average_salary": (sum(float(slip.net_pay or 0) for slip in slips) / len(slips)) if slips else 0,
			"approved_time_off": approved_time_off,
			"active_employees": active_employees,
			"attendance_health": attendance_health(attendance_breakdown),
		},
		"status_breakdown": dict(status_breakdown),
		"attendance_breakdown": dict(attendance_breakdown),
		"trend": [{"month": month, "value": trend[month]} for month in sorted(trend)],
		"warnings": {
			"queued_payruns": status_breakdown.get("Queued", 0),
			"failed_payruns": status_breakdown.get("Failed", 0),
			"unmarked_attendance": attendance_breakdown.get("Unmarked", 0),
		},
	}


def attendance_health(breakdown: dict) -> float:
	total = sum(breakdown.values())
	if not total:
		return 100
	return round((breakdown.get("Present", 0) / total) * 100, 1)
