"""PeoplePay360 role matrix and DocType permission setup."""

from __future__ import annotations

import frappe
from frappe.permissions import add_permission, update_permission_property


ROLES = (
	"Employee",
	"HR Manager",
	"HR Payroll User",
	"HR Payroll Manager",
	"System Manager",
)

# DocTypes grouped by access intent for PeoplePay360 product roles.
HR_CORE = [
	"Employee",
	"Employment Contract",
	"Working Schedule",
	"Working Schedule Assignment",
	"Working Schedule Day",
	"Attendance",
	"Attendance Request",
	"Employee Checkin",
	"Leave Application",
	"Leave Allocation",
	"Leave Type",
	"Leave Period",
	"Leave Policy",
	"Leave Policy Assignment",
	"Holiday List",
	"Holiday List Assignment",
	"Department",
	"Designation",
	"Branch",
	"Employee Grade",
	"Employment Type",
	"Employee Onboarding",
	"Employee Separation",
	"Shift Type",
	"Shift Assignment",
	"Shift Request",
	"HR Settings",
]

PAYROLL_DOCS = [
	"Payroll Entry",
	"Salary Slip",
	"Salary Structure",
	"Salary Structure Assignment",
	"Salary Component",
	"Payroll Period",
	"Payroll Settings",
	"Additional Salary",
	"Employee Benefit Application",
	"Income Tax Slab",
]

# permission flags: read, write, create, delete, submit, cancel, amend, report, export, share, print, email
PERM = {
	"employee_self": {
		"read": 1,
		"write": 0,
		"create": 0,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 0,
		"share": 0,
		"print": 1,
		"email": 0,
	},
	"employee_create": {
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 0,
		"submit": 1,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 0,
		"share": 0,
		"print": 1,
		"email": 0,
	},
	"hr_full": {
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 1,
		"submit": 1,
		"cancel": 1,
		"amend": 1,
		"report": 1,
		"export": 1,
		"share": 1,
		"print": 1,
		"email": 1,
	},
	"payroll_cru": {
		"read": 1,
		"write": 1,
		"create": 1,
		"delete": 0,
		"submit": 1,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 1,
		"share": 1,
		"print": 1,
		"email": 1,
	},
	"payroll_read": {
		"read": 1,
		"write": 0,
		"create": 0,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 1,
		"share": 0,
		"print": 1,
		"email": 0,
	},
}


def ensure_roles() -> None:
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			doc = frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1})
			doc.insert(ignore_permissions=True)


def _set_perms(doctype: str, role: str, flags: dict) -> None:
	if not frappe.db.exists("DocType", doctype):
		return
	add_permission(doctype, role, 0)
	for ptype, value in flags.items():
		try:
			update_permission_property(doctype, role, 0, ptype, value)
		except Exception:
			# Some DocTypes do not support submit/cancel etc.
			pass


def fix_desk_shell_access() -> None:
	"""Fast fix: Page/Workspace/Report read + PeoplePay360 workspace roles for all product roles."""
	ensure_roles()
	desk_roles = ("Employee", "HR Manager", "HR User", "HR Payroll User", "HR Payroll Manager")
	for role in desk_roles:
		_set_perms("Page", role, PERM["employee_self"])
		_set_perms("Workspace", role, PERM["employee_self"])
		_set_perms("Report", role, PERM["employee_self"])

	_set_page_roles()
	# Update workspace roles without triggering a full export of sidebar from stale DB
	_set_workspace_roles_db_only()
	frappe.clear_cache()


def _set_workspace_roles_db_only() -> None:
	all_product = [
		"Employee",
		"HR Manager",
		"HR User",
		"HR Payroll User",
		"HR Payroll Manager",
		"System Manager",
	]
	mapping = {
		"PeoplePay360": all_product,
		"PeoplePay360 HR": ["HR Manager", "HR User", "HR Payroll User", "HR Payroll Manager", "System Manager"],
		"PeoplePay360 Payroll": ["HR Payroll User", "HR Payroll Manager", "System Manager"],
		"PeoplePay360 Employee": ["Employee"],
		"Payroll": ["HR Payroll User", "HR Payroll Manager", "System Manager"],
		"Leaves": all_product,
		"Time Off": all_product,
	}
	for name, roles in mapping.items():
		if not frappe.db.exists("Workspace", name):
			continue
		# Clear existing Has Role child rows
		frappe.db.delete("Has Role", {"parent": name, "parenttype": "Workspace"})
		for idx, role in enumerate(roles, start=1):
			frappe.get_doc(
				{
					"doctype": "Has Role",
					"parent": name,
					"parenttype": "Workspace",
					"parentfield": "roles",
					"role": role,
					"idx": idx,
				}
			).insert(ignore_permissions=True)
		if name == "PeoplePay360":
			frappe.db.set_value("Workspace", name, {"public": 1, "is_hidden": 0}, update_modified=False)
	frappe.db.commit()


def apply_peoplepay360_role_permissions() -> None:
	"""Apply product role matrix. Safe to re-run."""
	ensure_roles()

	# Employee: own HR self-service only (user permissions restrict to linked Employee)
	for doctype in (
		"Employee",
		"Attendance",
		"Leave Allocation",
		"Employment Contract",
		"Salary Slip",
		"Working Schedule Assignment",
	):
		_set_perms(doctype, "Employee", PERM["employee_self"])

	for doctype in ("Leave Application", "Attendance Request", "Employee Checkin", "Shift Request"):
		_set_perms(doctype, "Employee", PERM["employee_create"])

	# Explicitly no onboarding / payroll admin for Employee
	for doctype in (
		"Payroll Entry",
		"Salary Structure",
		"Salary Component",
		"Payroll Settings",
		"Employee Onboarding",
		"Employee Separation",
	):
		for perm_dt in ("DocPerm", "Custom DocPerm"):
			if frappe.db.exists("DocType", doctype) and frappe.db.exists(
				perm_dt, {"parent": doctype, "role": "Employee"}
			):
				frappe.db.delete(perm_dt, {"parent": doctype, "role": "Employee", "permlevel": 0})

	# Keep Salary Slip readable for employees (own slips via user permission)
	_set_perms("Salary Slip", "Employee", PERM["employee_self"])

	# HR Manager: full HR, no payroll write
	for doctype in HR_CORE:
		_set_perms(doctype, "HR Manager", PERM["hr_full"])
	for doctype in PAYROLL_DOCS:
		# Strip payroll admin access for HR Manager
		for perm_dt in ("DocPerm", "Custom DocPerm"):
			if frappe.db.exists("DocType", doctype) and frappe.db.exists(
				perm_dt, {"parent": doctype, "role": "HR Manager"}
			):
				frappe.db.delete(perm_dt, {"parent": doctype, "role": "HR Manager", "permlevel": 0})

	# HR Payroll User: HR full + payroll CRU (structures read-only)
	for doctype in HR_CORE:
		_set_perms(doctype, "HR Payroll User", PERM["hr_full"])
	for doctype in ("Payroll Entry", "Salary Slip", "Additional Salary", "Salary Structure Assignment"):
		_set_perms(doctype, "HR Payroll User", PERM["payroll_cru"])
	for doctype in ("Salary Structure", "Salary Component", "Payroll Period", "Payroll Settings", "Income Tax Slab"):
		_set_perms(doctype, "HR Payroll User", PERM["payroll_read"])

	# HR Payroll Manager: full HR + full payroll
	for doctype in HR_CORE + PAYROLL_DOCS:
		_set_perms(doctype, "HR Payroll Manager", PERM["hr_full"])

	# Desk shell access — every product role needs Page/Workspace read
	desk_roles = ("Employee", "HR Manager", "HR User", "HR Payroll User", "HR Payroll Manager")
	for role in desk_roles:
		_set_perms("Page", role, PERM["employee_self"])
		_set_perms("Workspace", role, PERM["employee_self"])
		_set_perms("Report", role, PERM["employee_self"])

	# Pages role access
	_set_page_roles()
	_set_workspace_roles()
	frappe.clear_cache()


def _set_page_roles() -> None:
	page_roles = {
		"payrun-wizard": ["HR Payroll User", "HR Payroll Manager", "System Manager"],
		"payrun-processing": ["HR Payroll User", "HR Payroll Manager", "System Manager"],
		"payroll-dashboard": ["HR Manager", "HR Payroll User", "HR Payroll Manager", "System Manager"],
		"working-schedule-setup": ["HR Manager", "HR Payroll User", "HR Payroll Manager", "System Manager"],
		"pp-assistant": [
			"Employee",
			"HR Manager",
			"HR User",
			"HR Payroll User",
			"HR Payroll Manager",
			"System Manager",
		],
	}
	for page, roles in page_roles.items():
		if not frappe.db.exists("Page", page):
			continue
		doc = frappe.get_doc("Page", page)
		doc.set("roles", [])
		for role in roles:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)


def _set_workspace_roles() -> None:
	# One primary PeoplePay360 shell for every product role; UI filters links.
	all_product = [
		"Employee",
		"HR Manager",
		"HR User",
		"HR Payroll User",
		"HR Payroll Manager",
		"System Manager",
	]
	mapping = {
		"PeoplePay360": all_product,
		"PeoplePay360 HR": ["HR Manager", "HR User", "HR Payroll User", "HR Payroll Manager", "System Manager"],
		"PeoplePay360 Payroll": ["HR Payroll User", "HR Payroll Manager", "System Manager"],
		"PeoplePay360 Employee": ["Employee"],
		"Payroll": ["HR Payroll User", "HR Payroll Manager", "System Manager"],
		"Leaves": all_product,
		"Time Off": all_product,
	}
	for name, roles in mapping.items():
		if not frappe.db.exists("Workspace", name):
			continue
		doc = frappe.get_doc("Workspace", name)
		doc.set("roles", [])
		for role in roles:
			doc.append("roles", {"role": role})
		if name == "PeoplePay360":
			doc.public = 1
			doc.is_hidden = 0
		if name == "PeoplePay360 Employee":
			doc.public = 0
		doc.save(ignore_permissions=True)


def get_home_route_for_user(user: str | None = None) -> str:
	"""Everyone lands in PeoplePay360; sidebar visibility is role-filtered."""
	return "/desk/peoplepay360"


# Distinct demo passkeys per product role (used by login role picker + seed).
DEMO_ROLE_LOGINS = [
	{
		"id": "employee",
		"label": "Employee",
		"description": "Own profile, attendance & time off",
		"email": "alex.employee@example.com",
		"password": "Emp@360!",
		"roles": ["Employee"],
	},
	{
		"id": "hr_manager",
		"label": "HR Manager",
		"description": "Employees, contracts, schedules, leave — no payroll",
		"email": "hr.manager@example.com",
		"password": "HrMgr@360!",
		"roles": ["HR Manager", "Leave Approver", "Employee"],
	},
	{
		"id": "payroll_user",
		"label": "HR Payroll User",
		"description": "HR + payruns & payslips (structures read-only)",
		"email": "payroll.user@example.com",
		"password": "PayUser@360!",
		"roles": ["HR Payroll User", "HR Manager", "Employee"],
	},
	{
		"id": "payroll_manager",
		"label": "HR Payroll Manager",
		"description": "Full HR & payroll configuration",
		"email": "payroll.manager@example.com",
		"password": "PayMgr@360!",
		"roles": ["HR Payroll Manager", "HR Manager", "Employee"],
	},
	{
		"id": "admin",
		"label": "Admin",
		"description": "Full system administration",
		"email": "admin.pp@example.com",
		"password": "Admin@360!",
		"roles": ["System Manager", "HR Payroll Manager", "HR Manager"],
	},
]


@frappe.whitelist(allow_guest=True)
def get_demo_role_logins() -> dict:
	"""Public role picker presets for PeoplePay360 login screens."""
	return {
		"roles": [
			{
				"id": r["id"],
				"label": r["label"],
				"description": r["description"],
				"email": r["email"],
				"password": r["password"],
			}
			for r in DEMO_ROLE_LOGINS
		],
		"desk_login": "/peoplepay360_login",
		"pwa_login": "/hrms/login",
	}


@frappe.whitelist()
def get_ui_capabilities() -> dict:
	"""Frontend feature flags used to hide buttons/menus by role."""
	roles = set(frappe.get_roles())
	is_admin = "System Manager" in roles
	is_payroll_manager = is_admin or "HR Payroll Manager" in roles
	is_payroll_user = is_payroll_manager or "HR Payroll User" in roles
	is_hr_manager = is_admin or is_payroll_user or "HR Manager" in roles or "HR User" in roles
	is_employee = "Employee" in roles

	return {
		"roles": sorted(roles),
		"home_route": get_home_route_for_user(),
		"can_manage_employees": is_hr_manager,
		"can_manage_contracts": is_hr_manager,
		"can_manage_schedules": is_hr_manager,
		"can_manage_time_off_types": is_hr_manager,
		"can_approve_time_off": is_hr_manager,
		"can_onboard_employees": is_hr_manager,
		"can_view_payroll": is_payroll_user,
		"can_create_payrun": is_payroll_user,
		"can_edit_salary_structures": is_payroll_manager,
		"can_edit_salary_rules": is_payroll_manager,
		"can_send_payslips": is_payroll_user,
		"is_employee_only": is_employee and not is_hr_manager and not is_admin,
		"is_hr_manager_only": ("HR Manager" in roles or "HR User" in roles)
		and not is_payroll_user
		and not is_admin,
		"is_admin": is_admin,
		"can_use_assistant": is_admin
		or is_payroll_user
		or is_hr_manager
		or (is_employee and not is_hr_manager),
	}
