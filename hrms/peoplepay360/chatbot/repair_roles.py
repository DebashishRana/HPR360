# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

from __future__ import annotations

import frappe


def repair_demo_roles() -> dict:
	"""Force-apply DEMO_ROLE_LOGINS roles via direct Has Role rows."""
	from hrms.peoplepay360.roles import DEMO_ROLE_LOGINS, ensure_roles

	ensure_roles()
	results = []
	for spec in DEMO_ROLE_LOGINS:
		email = spec["email"]
		if not frappe.db.exists("User", email):
			results.append({"email": email, "status": "missing"})
			continue
		wanted = list(spec.get("roles") or ["Employee"])
		if "Desk User" not in wanted:
			wanted.append("Desk User")
		# Wipe and rewrite product roles for this user (keep All/Guest implicit)
		frappe.db.sql("delete from `tabHas Role` where parent=%s and parenttype='User'", email)
		for role in wanted:
			if not frappe.db.exists("Role", role):
				continue
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
		results.append(
			{
				"email": email,
				"wanted": wanted,
				"db_roles": [r.role for r in frappe.get_all("Has Role", filters={"parent": email}, fields=["role"])],
				"get_roles": frappe.get_roles(email),
			}
		)
	return {"status": "ok", "users": results}


def list_demo_roles() -> dict:
	from hrms.peoplepay360.roles import DEMO_ROLE_LOGINS

	out = {}
	for spec in DEMO_ROLE_LOGINS:
		email = spec["email"]
		out[email] = frappe.get_roles(email) if frappe.db.exists("User", email) else []
	return out
