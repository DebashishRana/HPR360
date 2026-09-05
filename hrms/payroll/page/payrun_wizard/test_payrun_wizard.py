import json
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from hrms.payroll.page.payrun_wizard import payrun_wizard


class TestPayrunWizard(FrappeTestCase):
    def test_invalid_date_range(self):
        with self.assertRaises(frappe.ValidationError):
            payrun_wizard._validate_scope({
                "company": "Test Company", "start_date": "2026-02-01", "end_date": "2026-01-01",
                "payroll_frequency": "Monthly",
            })

    def test_scope_requires_company_and_dates(self):
        with self.assertRaises(frappe.ValidationError):
            payrun_wizard._validate_scope({"payroll_frequency": "Monthly"})

    @patch.object(payrun_wizard, "_require_create_permission")
    @patch.object(payrun_wizard, "_validate_scope")
    @patch.object(frappe, "get_all", return_value=[])
    def test_eligible_response_schema(self, get_all, validate_scope, require_permission):
        validate_scope.return_value = frappe._dict({
            "company": "Test Company", "start_date": "2026-01-01", "end_date": "2026-01-31",
            "payroll_frequency": "Monthly", "validate_attendance": 0,
        })
        result = payrun_wizard.get_eligible_employees({})
        self.assertEqual(set(result), {"filters", "employees", "summary", "warnings", "metadata"})
        self.assertEqual(result["summary"], {"total": 0, "eligible": 0, "review": 0, "blocked": 0, "selected": 0})

    @patch.object(payrun_wizard, "_require_create_permission")
    @patch.object(payrun_wizard, "_validate_scope")
    @patch.object(payrun_wizard, "get_eligible_employees", return_value={"employees": []})
    def test_empty_selection_is_rejected(self, get_eligible, validate_scope, require_permission):
        validate_scope.return_value = frappe._dict({
            "company": "Test Company", "start_date": "2026-01-01", "end_date": "2026-01-31",
            "payroll_frequency": "Monthly",
        })
        with self.assertRaises(frappe.ValidationError):
            payrun_wizard.validate_payrun_selection({}, json.dumps([]))

    @patch.object(payrun_wizard, "_require_create_permission")
    @patch.object(payrun_wizard, "_validate_scope")
    @patch.object(payrun_wizard, "get_eligible_employees")
    def test_blocked_employee_cannot_be_selected(self, get_eligible, validate_scope, require_permission):
        validate_scope.return_value = frappe._dict({
            "company": "Test Company", "start_date": "2026-01-01", "end_date": "2026-01-31",
            "payroll_frequency": "Monthly",
        })
        get_eligible.return_value = {"employees": [{"employee": "EMP-001", "eligibility_status": "Blocked"}]}
        with self.assertRaises(frappe.ValidationError):
            payrun_wizard.validate_payrun_selection({}, json.dumps(["EMP-001"]))
