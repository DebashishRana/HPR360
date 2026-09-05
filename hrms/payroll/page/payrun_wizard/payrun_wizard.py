import json
from collections import Counter

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate


EMPLOYEE_FIELDS = [
    "name", "employee_name", "employee_type", "department", "designation", "branch", "grade",
    "company", "status", "personal_email", "company_email", "bank_name", "bank_ac_no",
]


def _as_dict(value):
    if isinstance(value, str):
        value = json.loads(value or "{}")
    return frappe._dict(value or {})


def _require_create_permission():
    if not frappe.has_permission("Payroll Entry", ptype="create"):
        frappe.throw(_("You do not have permission to create Payroll Entries."), frappe.PermissionError)


def _validate_scope(filters):
    filters = _as_dict(filters)
    if not filters.company:
        frappe.throw(_("Company is required."))
    if not filters.start_date or not filters.end_date:
        frappe.throw(_("From Date and To Date are required."))
    if getdate(filters.start_date) > getdate(filters.end_date):
        frappe.throw(_("From Date cannot be after To Date."))
    if not cint(filters.salary_slip_based_on_timesheet) and not filters.payroll_frequency:
        frappe.throw(_("Payroll Frequency is required for period-based payroll."))
    if not frappe.db.exists("Company", filters.company):
        frappe.throw(_("The selected Company does not exist."))
    if filters.salary_structure:
        structure = frappe.db.get_value(
            "Salary Structure", filters.salary_structure, ["company", "is_active"], as_dict=True
        )
        if not structure or structure.company != filters.company:
            frappe.throw(_("Salary Structure must belong to the selected Company."))
        if structure.is_active in ("No", 0, "0"):
            frappe.throw(_("The selected Salary Structure is inactive."))
    return filters


def _warning(code, severity, employee, doctype, name, message, route, blocks=False):
    return {
        "code": code, "severity": severity, "employee": employee, "document_type": doctype,
        "document_name": name, "message": message, "link_route": route, "blocks_creation": bool(blocks),
    }


def _assignment(employee, filters):
    return frappe.get_all(
        "Salary Structure Assignment",
        filters={
            "employee": employee,
            "company": filters.company,
            "docstatus": 1,
            "from_date": ["<=", filters.end_date],
        },
        fields=["name", "salary_structure", "from_date", "base", "variable", "currency", "company"],
        order_by="from_date desc, creation desc",
        limit_page_length=1,
    )


def _duplicate_slip(employee, filters):
    return frappe.get_all(
        "Salary Slip",
        filters={
            "employee": employee, "start_date": filters.start_date, "end_date": filters.end_date,
            "docstatus": ["!=", 2],
        },
        fields=["name"], limit_page_length=1,
    )


def _existing_finalized_payrun(filters):
    return frappe.get_all(
        "Payroll Entry",
        filters={
            "company": filters.company, "docstatus": 1,
            "start_date": ["<=", filters.end_date], "end_date": [">=", filters.start_date],
        },
        fields=["name"], limit_page_length=1,
    )


def _check_employee(employee, filters):
    warnings = []
    assignment = _assignment(employee.name, filters)
    selected_assignment = assignment[0] if assignment else None

    if not selected_assignment:
        warnings.append(_warning("MISSING_SALARY_ASSIGNMENT", "Blocking", employee.name,
            "Salary Structure Assignment", "", _("No effective Salary Structure Assignment was found."),
            "List/Salary Structure Assignment", True))
    else:
        if filters.salary_structure and selected_assignment.salary_structure != filters.salary_structure:
            warnings.append(_warning("SALARY_STRUCTURE_FILTER_MISMATCH", "Blocking", employee.name,
                "Salary Structure Assignment", selected_assignment.name,
                _("The employee is assigned to a different Salary Structure."),
                "Form/Salary Structure Assignment/{0}".format(selected_assignment.name), True))
        structure = frappe.db.get_value("Salary Structure", selected_assignment.salary_structure,
            ["company", "is_active", "currency"], as_dict=True)
        if not structure or structure.company != filters.company:
            warnings.append(_warning("INVALID_SALARY_STRUCTURE", "Blocking", employee.name,
                "Salary Structure", selected_assignment.salary_structure, _("Salary Structure company is invalid."),
                "List/Salary Structure", True))
        elif structure.is_active in ("No", 0, "0"):
            warnings.append(_warning("INACTIVE_SALARY_STRUCTURE", "Blocking", employee.name,
                "Salary Structure", selected_assignment.salary_structure, _("Salary Structure is inactive."),
                "List/Salary Structure", True))
        if getdate(selected_assignment.from_date) > getdate(filters.end_date):
            warnings.append(_warning("ASSIGNMENT_OUTSIDE_PERIOD", "Blocking", employee.name,
                "Salary Structure Assignment", selected_assignment.name, _("Assignment starts after this payroll period."),
                "Form/Salary Structure Assignment/{0}".format(selected_assignment.name), True))

    duplicate = _duplicate_slip(employee.name, filters)
    if duplicate:
        warnings.append(_warning("DUPLICATE_SALARY_SLIP", "Blocking", employee.name, "Salary Slip",
            duplicate[0].name, _("A Salary Slip already exists for this period."),
            "Form/Salary Slip/{0}".format(duplicate[0].name), True))

    if not employee.bank_name and not employee.bank_ac_no:
        warnings.append(_warning("MISSING_BANK_DETAILS", "Review", employee.name, "Employee", employee.name,
            _("Bank details are missing."), "Form/Employee/{0}".format(employee.name)))
    if not (employee.company_email or employee.personal_email):
        warnings.append(_warning("MISSING_EMAIL", "Review", employee.name, "Employee", employee.name,
            _("No employee email address is configured."), "Form/Employee/{0}".format(employee.name)))

    if frappe.db.exists("DocType", "Employment Contract") and frappe.db.exists(
        "Employment Contract", {"employee": employee.name}
    ):
        contracts = frappe.get_all("Employment Contract", filters={"employee": employee.name},
            fields=["name", "status", "start_date", "end_date"], order_by="start_date asc")
        valid = [c for c in contracts if c.status == "Active" and getdate(c.start_date) <= getdate(filters.end_date)
            and (not c.end_date or getdate(c.end_date) >= getdate(filters.start_date))]
        if not valid:
            warnings.append(_warning("MISSING_ACTIVE_CONTRACT", "Blocking", employee.name, "Employment Contract", "",
                _("No active Employment Contract covers this payroll period."), "List/Employment Contract", True))
        for first, second in zip(contracts, contracts[1:]):
            if first.end_date and getdate(first.end_date) >= getdate(second.start_date):
                warnings.append(_warning("OVERLAPPING_CONTRACTS", "Review", employee.name, "Employment Contract",
                    second.name, _("Employment Contracts overlap."), "List/Employment Contract"))

    if cint(filters.validate_attendance):
        attendance = frappe.db.count("Attendance", {"employee": employee.name,
            "attendance_date": ["between", [filters.start_date, filters.end_date]], "docstatus": 1})
        if not attendance:
            warnings.append(_warning("MISSING_ATTENDANCE", "Blocking", employee.name, "Attendance", "",
                _("No submitted attendance was found for this period."), "List/Attendance", True))

    return selected_assignment, warnings


def _employee_filters(filters):
    result = {"company": filters.company, "status": "Active"}
    for key in ("department", "employee_type", "branch", "designation", "grade"):
        if filters.get(key):
            result[key] = filters[key]
    return result


@frappe.whitelist()
def get_payrun_scope_options():
    _require_create_permission()
    def names(doctype, filters=None):
        return frappe.get_all(doctype, filters=filters or {}, pluck="name", order_by="name asc", limit_page_length=0)
    companies = frappe.get_all("Company", fields=["name"], order_by="name asc", limit_page_length=0)
    return {"companies": companies, "payroll_frequencies": ["Monthly", "Fortnightly", "Bimonthly", "Weekly", "Daily"],
        "departments": names("Department"), "employee_types": names("Employee Type"), "branches": names("Branch"),
        "designations": names("Designation"), "grades": names("Employee Grade"),
        "salary_structures": names("Salary Structure", {"is_active": "Yes"}),
        "payroll_payable_accounts": names("Account", {"account_type": "Payable", "is_group": 0})}


@frappe.whitelist()
def get_eligible_employees(filters):
    _require_create_permission()
    filters = _validate_scope(filters)
    rows, all_warnings = [], []
    employees = frappe.get_all("Employee", filters=_employee_filters(filters), fields=EMPLOYEE_FIELDS,
        order_by="name asc", limit_page_length=0)
    for employee in employees:
        assignment, warnings = _check_employee(employee, filters)
        all_warnings.extend(warnings)
        status = "Blocked" if any(w["blocks_creation"] for w in warnings) else ("Review" if warnings else "Eligible")
        rows.append({"employee": employee.name, "employee_name": employee.employee_name,
            "employee_type": employee.employee_type, "department": employee.department,
            "designation": employee.designation, "branch": employee.branch, "grade": employee.grade,
            "active_contract": not any(w["code"] == "MISSING_ACTIVE_CONTRACT" for w in warnings),
            "salary_structure": assignment.salary_structure if assignment else "",
            "salary_structure_assignment": assignment.name if assignment else "",
            "assignment_effective_date": assignment.from_date if assignment else "",
            "base_salary": flt(assignment.base) if assignment else 0,
            "variable_salary": flt(assignment.variable) if assignment else 0,
            "attendance_status": "Review" if any(w["code"] == "MISSING_ATTENDANCE" for w in warnings) else "OK",
            "leave_status": "OK", "bank_details_status": "OK" if employee.bank_name or employee.bank_ac_no else "Missing",
            "email_status": "OK" if employee.company_email or employee.personal_email else "Missing",
            "eligibility_status": status, "warning_count": len(warnings)})
    if not filters.get("payroll_payable_account") and not frappe.db.get_value(
        "Company", filters.company, "default_payroll_payable_account"
    ):
        all_warnings.append(_warning("MISSING_PAYROLL_PAYABLE_ACCOUNT", "Blocking", "", "Company", filters.company,
            _("No payroll payable account is configured for this company."),
            "Form/Company/{0}".format(filters.company), True))
    counts = Counter(row["eligibility_status"] for row in rows)
    return {"filters": dict(filters), "employees": rows,
        "summary": {"total": len(rows), "eligible": counts["Eligible"], "review": counts["Review"],
            "blocked": counts["Blocked"], "selected": 0}, "warnings": all_warnings,
        "metadata": {"currency": frappe.db.get_value("Company", filters.company, "default_currency")}}


@frappe.whitelist()
def validate_payrun_selection(filters, selected_employees):
    _require_create_permission()
    filters = _validate_scope(filters)
    selected = _as_dict({"employees": selected_employees}).employees
    selected = json.loads(selected) if isinstance(selected, str) else selected
    selected = list(dict.fromkeys(selected or []))
    if not selected:
        frappe.throw(_("Select at least one employee."))
    allowed = {row["employee"] for row in get_eligible_employees(filters)["employees"]
        if row["eligibility_status"] != "Blocked"}
    blocked = sorted(set(selected) - allowed)
    if blocked:
        frappe.throw(_("These employees are not eligible: {0}").format(", ".join(blocked)))
    return {"filters": dict(filters), "selected_employees": selected}


@frappe.whitelist()
def create_payrun(filters, selected_employees):
    _require_create_permission()
    filters = _validate_scope(filters)
    validation = validate_payrun_selection(filters, selected_employees)
    selected = validation["selected_employees"]
    if _existing_finalized_payrun(filters) and not frappe.has_permission("Payroll Entry", ptype="submit"):
        frappe.throw(_("A finalized Payroll Entry overlaps this period."), frappe.PermissionError)
    company = frappe.db.get_value("Company", filters.company,
        ["default_currency", "default_payroll_payable_account"], as_dict=True)
    entry = frappe.new_doc("Payroll Entry")
    entry.update({"company": filters.company, "posting_date": filters.get("posting_date") or filters.end_date,
        "start_date": filters.start_date, "end_date": filters.end_date,
        "payroll_frequency": filters.get("payroll_frequency"),
        "salary_slip_based_on_timesheet": cint(filters.get("salary_slip_based_on_timesheet")),
        "validate_attendance": cint(filters.get("validate_attendance")), "branch": filters.get("branch"),
        "department": filters.get("department"), "designation": filters.get("designation"),
        "grade": filters.get("grade"), "currency": filters.get("currency") or company.default_currency,
        "payroll_payable_account": filters.get("payroll_payable_account") or company.default_payroll_payable_account})
    if not entry.payroll_payable_account:
        frappe.throw(_("Payroll Payable Account is required before creating a payrun."))
    for employee in selected:
        details = frappe.db.get_value("Employee", employee, ["employee_name", "department", "designation"], as_dict=True)
        entry.append("employees", {"employee": employee, "employee_name": details.employee_name,
            "department": details.department, "designation": details.designation})
    entry.insert()
    frappe.db.commit()
    return {"name": entry.name, "route": "payrun-processing/{0}".format(entry.name)}
