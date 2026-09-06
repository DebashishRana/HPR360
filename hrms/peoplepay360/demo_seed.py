"""Seed realistic PeoplePay360 demo data for Desk + PWA demos."""

from __future__ import annotations

from datetime import timedelta

import frappe
from frappe.utils import add_days, flt, getdate, now_datetime, nowdate, today


PASSWORD_FALLBACK = "Emp@360!"


def ensure_demo_login_users() -> dict:
	"""Create/update only the role-picker demo users (fast, no masters)."""
	frappe.only_for(("System Manager", "Administrator"))
	from hrms.peoplepay360.roles import DEMO_ROLE_LOGINS, ensure_roles

	ensure_roles()
	if not frappe.db.exists("Role", "Leave Approver"):
		frappe.get_doc({"doctype": "Role", "role_name": "Leave Approver", "desk_access": 1}).insert(
			ignore_permissions=True
		)

	created = []
	for spec in DEMO_ROLE_LOGINS:
		email = spec["email"]
		password = spec["password"]
		roles = list(spec.get("roles") or ["Employee"])
		if "Desk User" not in roles:
			roles.append("Desk User")
		label = spec["label"]
		if frappe.db.exists("User", email):
			user = frappe.get_doc("User", email)
		else:
			parts = label.split()
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": parts[0],
					"last_name": " ".join(parts[1:]) or "User",
					"send_welcome_email": 0,
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)
		user.flags.ignore_permissions = True
		user.flags.ignore_password_policy = True
		user.new_password = password
		user.save(ignore_permissions=True)
		# User.save can drop some roles depending on Role Profile — write Has Role directly
		frappe.db.sql("delete from `tabHas Role` where parent=%s and parenttype='User'", email)
		for role in roles:
			if frappe.db.exists("Role", role):
				frappe.get_doc(
					{
						"doctype": "Has Role",
						"parent": email,
						"parenttype": "User",
						"parentfield": "roles",
						"role": role,
					}
				).insert(ignore_permissions=True)
		frappe.clear_cache(user=email)
		created.append({"email": email, "password": password, "roles": roles})

	# Extra employees share Employee passkey
	for email, name in (
		("blair.employee@example.com", "Blair Employee"),
		("casey.employee@example.com", "Casey Employee"),
	):
		if not frappe.db.exists("User", email):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": name.split()[0],
					"last_name": name.split()[-1],
					"send_welcome_email": 0,
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)
		else:
			user = frappe.get_doc("User", email)
		user.flags.ignore_permissions = True
		user.flags.ignore_password_policy = True
		user.new_password = PASSWORD_FALLBACK
		user.save(ignore_permissions=True)
		frappe.db.sql("delete from `tabHas Role` where parent=%s and parenttype='User'", email)
		for role in ("Employee", "Desk User"):
			frappe.get_doc(
				{
					"doctype": "Has Role",
					"parent": email,
					"parenttype": "User",
					"parentfield": "roles",
					"role": role,
				}
			).insert(ignore_permissions=True)
		frappe.clear_cache(user=email)

	frappe.db.commit()
	return {"status": "ok", "logins": created}


def seed_peoplepay360_demo(force: bool = False) -> dict:
	"""Create company, roles, users, employees, contracts, attendance, leave, payroll demo."""
	frappe.only_for(("System Manager",))
	from hrms.peoplepay360.roles import DEMO_ROLE_LOGINS, apply_peoplepay360_role_permissions

	apply_peoplepay360_role_permissions()

	if frappe.db.exists("Employee", {"user_id": "alex.employee@example.com"}) and not force:
		return {
			"status": "exists",
			"message": "Demo data already present. Pass force=1 to recreate users/links.",
			"logins": DEMO_ROLE_LOGINS,
			"tip": "Login: /hrms/login or /peoplepay360_login — pick a role card",
		}

	company = _ensure_company()
	_ensure_masters(company)
	users = _ensure_users()
	employees = _ensure_employees(company, users)
	_ensure_schedules(company, employees)
	_ensure_contracts(employees)
	_ensure_leave(company, employees)
	_ensure_attendance(company, employees)
	salary = _ensure_salary(company, employees)
	_ensure_demo_payslips(company, employees, salary)

	frappe.db.commit()
	return {
		"status": "ok",
		"company": company,
		"logins": DEMO_ROLE_LOGINS,
		"extra_employee_logins": [
			{"email": "blair.employee@example.com", "password": "Emp@360!", "role": "Employee"},
			{"email": "casey.employee@example.com", "password": "Emp@360!", "role": "Employee"},
		],
		"employees": list(employees.keys()),
		"tip": "Login: /hrms/login or /peoplepay360_login — each role has its own passkey",
	}


def _ensure_company() -> str:
	name = "PeoplePay360 Demo"
	if frappe.db.exists("Company", name):
		return name

	# Prefer cloning accounts from an existing company when available
	existing = frappe.db.get_value("Company", {}, "name")
	company = frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": name,
			"abbr": "PPD",
			"default_currency": frappe.db.get_value("Company", existing, "default_currency") if existing else "USD",
			"country": frappe.db.get_value("Company", existing, "country") if existing else "United States",
			"create_chart_of_accounts_based_on": "Existing Company" if existing else "Standard Template",
			"existing_company": existing,
		}
	)
	if not existing:
		company.create_chart_of_accounts_based_on = "Standard Template"
		company.chart_of_accounts = "Standard"
	company.insert(ignore_permissions=True)
	return company.name


def _ensure_masters(company: str) -> None:
	for dept in ("Engineering", "People Ops", "Finance"):
		if not frappe.db.exists("Department", {"department_name": dept, "company": company}):
			frappe.get_doc(
				{"doctype": "Department", "department_name": dept, "company": company}
			).insert(ignore_permissions=True)

	for desig in ("Software Engineer", "HR Business Partner", "Payroll Specialist", "Engineering Manager"):
		if not frappe.db.exists("Designation", desig):
			frappe.get_doc({"doctype": "Designation", "designation_name": desig}).insert(ignore_permissions=True)

	if frappe.db.exists("DocType", "Employee Type"):
		for et in ("Full-time", "Contract"):
			if not frappe.db.exists("Employee Type", et):
				frappe.get_doc({"doctype": "Employee Type", "employee_type_name": et}).insert(
					ignore_permissions=True
				)

	holiday = None
	try:
		holiday = frappe.db.get_value("Holiday List", {"company": company}, "name")
	except Exception:
		holiday = frappe.db.get_value("Holiday List", {}, "name")
	if not holiday:
		holiday_doc = frappe.get_doc(
			{
				"doctype": "Holiday List",
				"holiday_list_name": f"{company} Holidays",
				"from_date": f"{getdate(today()).year}-01-01",
				"to_date": f"{getdate(today()).year}-12-31",
			}
		)
		# older/newer schemas may or may not have company
		if frappe.get_meta("Holiday List").has_field("company"):
			holiday_doc.company = company
		holiday_doc.insert(ignore_permissions=True)


def _ensure_users() -> dict:
	from hrms.peoplepay360.roles import DEMO_ROLE_LOGINS

	# Map email -> (full_name, roles, password)
	specs = {
		r["email"]: (
			{
				"admin.pp@example.com": "PP Admin",
				"payroll.manager@example.com": "Pat Payroll Manager",
				"payroll.user@example.com": "Priya Payroll User",
				"hr.manager@example.com": "Harper HR Manager",
				"alex.employee@example.com": "Alex Employee",
			}[r["email"]],
			r["roles"],
			r["password"],
		)
		for r in DEMO_ROLE_LOGINS
	}
	# Extra employee accounts share the Employee passkey
	specs["blair.employee@example.com"] = ("Blair Employee", ["Employee"], "Emp@360!")
	specs["casey.employee@example.com"] = ("Casey Employee", ["Employee"], "Emp@360!")

	users = {}
	for email, (full_name, roles, password) in specs.items():
		if frappe.db.exists("User", email):
			user = frappe.get_doc("User", email)
			user.new_password = password
			user.save(ignore_permissions=True)
		else:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": full_name.split()[0],
					"last_name": " ".join(full_name.split()[1:]) or "User",
					"send_welcome_email": 0,
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)
			user.new_password = password
			user.save(ignore_permissions=True)
		user.flags.ignore_permissions = True
		user.add_roles(*roles)
		users[email] = email
	return users


def _ensure_employees(company: str, users: dict) -> dict:
	dept_eng = frappe.db.get_value("Department", {"department_name": "Engineering", "company": company})
	dept_hr = frappe.db.get_value("Department", {"department_name": "People Ops", "company": company})
	dept_fin = frappe.db.get_value("Department", {"department_name": "Finance", "company": company})

	# Use Employee Number naming for predictable demo IDs
	frappe.db.set_single_value("HR Settings", "emp_created_by", "Employee Number")

	rows = [
		("PP-EMP-001", "Alex Employee", "alex.employee@example.com", dept_eng, "Software Engineer", 52000),
		("PP-EMP-002", "Blair Employee", "blair.employee@example.com", dept_eng, "Software Engineer", 54000),
		("PP-EMP-003", "Casey Employee", "casey.employee@example.com", dept_fin, "Payroll Specialist", 48000),
		("PP-EMP-004", "Harper HR Manager", "hr.manager@example.com", dept_hr, "HR Business Partner", 62000),
		("PP-EMP-005", "Priya Payroll User", "payroll.user@example.com", dept_fin, "Payroll Specialist", 60000),
		("PP-EMP-006", "Pat Payroll Manager", "payroll.manager@example.com", dept_fin, "Engineering Manager", 75000),
	]
	employees = {}
	for name, employee_name, user_id, department, designation, wage in rows:
		existing = frappe.db.get_value("Employee", {"user_id": user_id}, "name") or (
			name if frappe.db.exists("Employee", name) else None
		)
		if existing:
			emp = frappe.get_doc("Employee", existing)
		else:
			parts = employee_name.split()
			emp = frappe.get_doc(
				{
					"doctype": "Employee",
					"employee_number": name,
					"first_name": parts[0],
					"last_name": " ".join(parts[1:]) or parts[0],
					"status": "Active",
					"company": company,
					"department": department,
					"designation": designation,
					"date_of_joining": add_days(today(), -400),
					"date_of_birth": "1994-05-12",
					"gender": "Other",
					"user_id": user_id,
					"company_email": user_id,
					"prefered_contact_email": "Company Email",
					"prefered_email": user_id,
					"cell_number": "9999999999",
					"bank_name": "Demo Bank",
					"bank_ac_no": f"AC{name[-3:]}001",
					"salary_currency": frappe.db.get_value("Company", company, "default_currency"),
				}
			)
			if frappe.db.exists("DocType", "Employee Type") and frappe.db.exists("Employee Type", "Full-time"):
				emp.employee_type = "Full-time"
			cost_center = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
			if cost_center:
				emp.payroll_cost_center = cost_center
			emp.insert(ignore_permissions=True)

		emp.db_set("user_id", user_id, update_modified=False)
		emp.db_set("status", "Active", update_modified=False)
		employees[emp.name] = {"doc": frappe.get_doc("Employee", emp.name), "wage": wage, "user": user_id}

	manager = next((k for k, v in employees.items() if v["user"] == "payroll.manager@example.com"), None)
	hr_manager = next((k for k, v in employees.items() if v["user"] == "hr.manager@example.com"), None)
	if manager:
		for emp_name, meta in employees.items():
			if meta["user"] in (
				"alex.employee@example.com",
				"blair.employee@example.com",
				"casey.employee@example.com",
				"hr.manager@example.com",
				"payroll.user@example.com",
			):
				frappe.db.set_value("Employee", emp_name, "reports_to", manager)

	for emp_name, meta in employees.items():
		_ensure_user_permission(meta["user"], emp_name)

	return employees


def _ensure_user_permission(user: str, employee: str) -> None:
	if frappe.db.exists("User Permission", {"user": user, "allow": "Employee", "for_value": employee}):
		return
	frappe.get_doc(
		{
			"doctype": "User Permission",
			"user": user,
			"allow": "Employee",
			"for_value": employee,
			"apply_to_all_doctypes": 1,
		}
	).insert(ignore_permissions=True)


def _ensure_contracts(employees: dict) -> None:
	if not frappe.db.exists("DocType", "Employment Contract"):
		return
	currency = frappe.db.get_single_value("System Settings", "currency") or "USD"
	schedule = (
		frappe.db.get_value("Working Schedule", {"is_active": 1}, "name")
		if frappe.db.exists("DocType", "Working Schedule")
		else None
	)
	structure = frappe.db.get_value("Salary Structure", {"is_active": "Yes"}, "name")
	for name, meta in employees.items():
		emp = meta["doc"]
		exists = frappe.db.exists("Employment Contract", {"employee": name, "status": "Active"})
		if exists:
			continue
		# historical + active
		old = frappe.get_doc(
			{
				"doctype": "Employment Contract",
				"employee": name,
				"status": "Expired",
				"contract_type": "Full-time",
				"start_date": add_days(today(), -400),
				"end_date": add_days(today(), -31),
				"department": emp.department,
				"position": emp.designation,
				"working_schedule": schedule,
				"wage": meta["wage"] - 2000,
				"currency": emp.salary_currency or currency,
				"terms": "Prior contract period",
			}
		)
		old.insert(ignore_permissions=True)
		active = frappe.get_doc(
			{
				"doctype": "Employment Contract",
				"employee": name,
				"status": "Active",
				"contract_type": "Full-time",
				"start_date": add_days(today(), -30),
				"end_date": None,
				"department": emp.department,
				"position": emp.designation,
				"working_schedule": schedule,
				"wage": meta["wage"],
				"currency": emp.salary_currency or currency,
				"salary_structure": structure,
				"terms": "Current active contract",
			}
		)
		active.insert(ignore_permissions=True)


def _ensure_schedules(company: str, employees: dict) -> None:
	if not frappe.db.exists("DocType", "Working Schedule"):
		return
	name = "Standard 40h Week"
	if not frappe.db.exists("Working Schedule", name):
		days = []
		for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
			days.append(
				{
					"day": day,
					"is_working_day": 1,
					"start_time": "09:00:00",
					"end_time": "18:00:00",
					"break_minutes": 60,
				}
			)
		for day in ("Saturday", "Sunday"):
			days.append({"day": day, "is_working_day": 0})
		frappe.get_doc(
			{
				"doctype": "Working Schedule",
				"schedule_name": name,
				"schedule_type": "Fixed Weekly",
				"company": company,
				"is_active": 1,
				"working_days": days,
			}
		).insert(ignore_permissions=True)

	for emp_name in employees:
		if frappe.db.exists(
			"Working Schedule Assignment", {"employee": emp_name, "working_schedule": name, "status": "Active"}
		):
			continue
		frappe.get_doc(
			{
				"doctype": "Working Schedule Assignment",
				"employee": emp_name,
				"company": company,
				"working_schedule": name,
				"start_date": add_days(today(), -30),
				"status": "Active",
			}
		).insert(ignore_permissions=True)


def _ensure_leave(company: str, employees: dict) -> None:
	leave_type = frappe.db.get_value("Leave Type", {"name": ("like", "%")}, "name")
	if not leave_type:
		lt = frappe.get_doc(
			{
				"doctype": "Leave Type",
				"leave_type_name": "Annual Leave",
				"max_leaves_allowed": 20,
				"is_carry_forward": 1,
			}
		)
		lt.insert(ignore_permissions=True)
		leave_type = lt.name

	year = getdate(today()).year
	for emp_name, meta in employees.items():
		if not frappe.db.exists(
			"Leave Allocation",
			{"employee": emp_name, "leave_type": leave_type, "from_date": f"{year}-01-01", "docstatus": 1},
		):
			alloc = frappe.get_doc(
				{
					"doctype": "Leave Allocation",
					"employee": emp_name,
					"leave_type": leave_type,
					"from_date": f"{year}-01-01",
					"to_date": f"{year}-12-31",
					"new_leaves_allocated": 20,
				}
			)
			alloc.insert(ignore_permissions=True)
			alloc.submit()

		# one approved leave for first two employees
		emp_list = list(employees.items())
		hr_approver = next((m["user"] for m in employees.values() if m["user"] == "hr.manager@example.com"), None)
		for emp_name, meta in emp_list[:2]:
			if frappe.db.exists("Leave Application", {"employee": emp_name, "from_date": add_days(today(), -3)}):
				continue
			app = frappe.get_doc(
				{
					"doctype": "Leave Application",
					"employee": emp_name,
					"leave_type": leave_type,
					"from_date": add_days(today(), -3),
					"to_date": add_days(today(), -2),
					"status": "Approved",
					"company": company,
					"leave_approver": hr_approver,
				}
			)
			app.insert(ignore_permissions=True)
			app.submit()


def _ensure_attendance(company: str, employees: dict) -> None:
	for emp_name, meta in employees.items():
		for offset in range(1, 8):
			day = add_days(today(), -offset)
			if getdate(day).weekday() >= 5:
				continue
			if frappe.db.exists("Attendance", {"employee": emp_name, "attendance_date": day}):
				continue
			status = "Present"
			if offset == 2 and meta["user"] == "alex.employee@example.com":
				status = "On Leave"
			att = frappe.get_doc(
				{
					"doctype": "Attendance",
					"employee": emp_name,
					"attendance_date": day,
					"status": status,
					"company": company,
					"working_hours": 8 if status == "Present" else 0,
				}
			)
			att.insert(ignore_permissions=True)
			att.submit()

			if status == "Present":
				for log_type, hour in (("IN", 9), ("OUT", 18)):
					frappe.get_doc(
						{
							"doctype": "Employee Checkin",
							"employee": emp_name,
							"log_type": log_type,
							"time": f"{day} {hour:02d}:00:00",
						}
					).insert(ignore_permissions=True)


def _ensure_salary(company: str, employees: dict) -> dict:
	currency = frappe.db.get_value("Company", company, "default_currency") or "USD"

	def ensure_component(name, abbr, type_, category, formula=None, amount=None):
		if frappe.db.exists("Salary Component", name):
			doc = frappe.get_doc("Salary Component", name)
			if hasattr(doc, "category") and not doc.category:
				doc.db_set("category", category)
			return name
		doc = frappe.get_doc(
			{
				"doctype": "Salary Component",
				"salary_component": name,
				"salary_component_abbr": abbr,
				"type": type_,
				"depends_on_payment_days": 1,
				"amount_based_on_formula": 1 if formula else 0,
				"formula": formula,
				"amount": amount or 0,
			}
		)
		if hasattr(frappe.get_meta("Salary Component"), "has_field") and frappe.get_meta("Salary Component").has_field(
			"category"
		):
			doc.category = category
		doc.insert(ignore_permissions=True)
		return doc.name

	basic = ensure_component("PP Basic", "PPB", "Earning", "Basic", formula="base")
	allowance = ensure_component("PP Allowance", "PPA", "Earning", "Allowance", formula="base * 0.10")
	deduction = ensure_component("PP Deduction", "PPD", "Deduction", "Deduction", formula="(PPB + PPA) * 0.05")

	structure_name = "Regular Salary"
	if not frappe.db.exists("Salary Structure", structure_name):
		ss = frappe.get_doc(
			{
				"doctype": "Salary Structure",
				"name": structure_name,
				"company": company,
				"currency": currency,
				"payroll_frequency": "Monthly",
				"is_active": "Yes",
				"earnings": [
					{"salary_component": basic, "abbr": "PPB", "amount_based_on_formula": 1, "formula": "base"},
					{
						"salary_component": allowance,
						"abbr": "PPA",
						"amount_based_on_formula": 1,
						"formula": "base * 0.10",
					},
				],
				"deductions": [
					{
						"salary_component": deduction,
						"abbr": "PPD",
						"amount_based_on_formula": 1,
						"formula": "(PPB + PPA) * 0.05",
					},
				],
			}
		)
		ss.insert(ignore_permissions=True)
		ss.submit()
	else:
		ss = frappe.get_doc("Salary Structure", structure_name)
		if ss.docstatus == 0:
			ss.submit()

	for emp_name, meta in employees.items():
		if frappe.db.exists(
			"Salary Structure Assignment",
			{"employee": emp_name, "salary_structure": structure_name, "docstatus": 1},
		):
			continue
		ssa = frappe.get_doc(
			{
				"doctype": "Salary Structure Assignment",
				"employee": emp_name,
				"salary_structure": structure_name,
				"company": company,
				"from_date": add_days(today(), -60),
				"base": meta["wage"],
				"currency": currency,
			}
		)
		ssa.insert(ignore_permissions=True)
		ssa.submit()

	# Link contracts to structure
	if frappe.db.exists("DocType", "Employment Contract"):
		frappe.db.sql(
			"""
			update `tabEmployment Contract`
			set salary_structure=%s
			where employee like 'PP-EMP-%%' and status='Active'
			""",
			structure_name,
		)

	return {"structure": structure_name, "currency": currency}


def _ensure_demo_payslips(company: str, employees: dict, salary: dict) -> None:
	"""Create a submitted payroll entry + slips for prior month so dashboard has data."""
	start = getdate(today()).replace(day=1)
	start = add_days(start, -1).replace(day=1)
	# month end
	if start.month == 12:
		end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
	else:
		end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)

	existing = frappe.db.exists(
		"Payroll Entry",
		{"company": company, "start_date": start, "end_date": end, "docstatus": ("!=", 2)},
	)
	if existing:
		return

	payable = frappe.db.get_value("Company", company, "default_payroll_payable_account")
	entry = frappe.get_doc(
		{
			"doctype": "Payroll Entry",
			"company": company,
			"posting_date": end,
			"payroll_frequency": "Monthly",
			"start_date": start,
			"end_date": end,
			"currency": salary["currency"],
			"payroll_payable_account": payable,
		}
	)
	for emp_name in employees:
		emp = employees[emp_name]["doc"]
		entry.append(
			"employees",
			{
				"employee": emp_name,
				"employee_name": emp.employee_name,
				"department": emp.department,
				"designation": emp.designation,
			},
		)
	entry.insert(ignore_permissions=True)
	try:
		entry.submit()
	except Exception as e:
		frappe.log_error("Demo payroll submit failed", str(e))
