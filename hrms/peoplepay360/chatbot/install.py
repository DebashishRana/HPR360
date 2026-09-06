# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

from __future__ import annotations

import frappe
from frappe.modules.import_file import import_file_by_path


def setup_assistant() -> str:
	page_path = frappe.get_app_path("hrms", "hr", "page", "pp_assistant", "pp_assistant.json")
	import_file_by_path(page_path, force=True)

	# Ensure page roles
	if frappe.db.exists("Page", "pp-assistant"):
		page = frappe.get_doc("Page", "pp-assistant")
		page.set("roles", [])
		for role in (
			"Employee",
			"HR Manager",
			"HR User",
			"HR Payroll User",
			"HR Payroll Manager",
			"System Manager",
		):
			page.append("roles", {"role": role})
		frappe.flags.in_import = True
		page.save(ignore_permissions=True)
		frappe.flags.in_import = False

	from hrms.peoplepay360.roles import fix_desk_shell_access

	fix_desk_shell_access()

	try:
		from hrms.peoplepay360.chatbot.repair_roles import repair_demo_roles
		from hrms.peoplepay360.chatbot.seed_data import seed_assistant_demo_data

		repair_demo_roles()
		seed_assistant_demo_data()
	except Exception as e:
		frappe.log_error(title="PeoplePay360 Assistant setup extras", message=str(e))

	frappe.db.commit()
	return "ok"
