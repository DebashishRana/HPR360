import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate


@frappe.whitelist()
def get_employee_profile(employee: str) -> dict:
	doc = frappe.get_doc("Employee", employee)
	doc.check_permission("read")

	period_start = add_months(getdate(nowdate()), -12)
	slips = frappe.get_list("Salary Slip", filters={"employee": employee, "docstatus": 1, "posting_date": [">=", period_start]}, fields=["net_pay", "currency", "posting_date"], limit_page_length=0)
	attendance = frappe.get_list("Attendance", filters={"employee": employee, "attendance_date": [">=", period_start]}, fields=["working_hours", "attendance_date", "status"], limit_page_length=0)
	expenses = frappe.get_list("Expense Claim", filters={"employee": employee, "docstatus": 1, "approval_status": "Approved", "posting_date": [">=", period_start]}, fields=["total_claimed_amount", "currency", "posting_date"], limit_page_length=0)
	contracts = frappe.get_list("Employment Contract", filters={"employee": employee}, fields=["name", "contract_type", "start_date", "end_date", "wage", "currency", "status", "position", "salary_structure"], order_by="start_date desc", limit_page_length=8) if frappe.db.exists("DocType", "Employment Contract") else []
	schedule = get_schedule(employee)
	activity = frappe.get_list("Employee Checkin", filters={"employee": employee}, fields=["time", "log_type", "device_id", "shift"], order_by="time desc", limit_page_length=6)

	return {
		"employee": {field: doc.get(field) for field in ["name", "employee_name", "company", "department", "designation", "status", "date_of_joining", "company_email", "cell_number", "image"]},
		"stats": {
			"total_payout": sum(float(row.net_pay or 0) for row in slips),
			"currency": next((row.currency for row in slips if row.currency), doc.salary_currency or ""),
			"time_worked": round(sum(float(row.working_hours or 0) for row in attendance), 2),
			"reimbursement": sum(float(row.total_claimed_amount or 0) for row in expenses),
			"attendance_count": len(attendance),
		},
		"contracts": contracts,
		"schedule": schedule,
		"activity": activity,
	}


def get_schedule(employee):
	if not frappe.db.exists("DocType", "Working Schedule Assignment"):
		return None
	from hrms.hr.doctype.working_schedule.working_schedule import get_working_schedule_for_employee
	schedule = get_working_schedule_for_employee(employee, nowdate())
	if not schedule:
		return None
	return {"name": schedule.name, "schedule_name": schedule.schedule_name, "schedule_type": schedule.schedule_type, "weekly_hours": schedule.weekly_hours, "working_day_count": schedule.working_day_count}


def publish_employee_profile_update(doc, event=None):
	employee = doc.get("name") if doc.doctype == "Employee" else doc.get("employee")
	if employee:
		frappe.publish_realtime("employee_profile_updated", {"employee": employee}, user=frappe.session.user)
