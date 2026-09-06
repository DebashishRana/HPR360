# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

from __future__ import annotations

import frappe

from hrms.peoplepay360.chatbot.engine import answer


def smoke_assistant() -> str:
	"""bench --site hrms.localhost execute hrms.peoplepay360.chatbot.smoke.smoke_assistant"""
	cases = [
		("hr.manager@example.com", "How many active employees do we have?"),
		("hr.manager@example.com", "Which leave requests are pending approval?"),
		("payroll.manager@example.com", "Give me a payroll readiness summary"),
		("admin.pp@example.com", "Give me a full PeoplePay360 status briefing"),
		("alex.employee@example.com", "What is my leave balance?"),
	]
	lines = []
	ok = True
	for user, q in cases:
		frappe.set_user(user)
		try:
			res = answer(q, [])
			snippet = (res.get("answer") or "")[:200].replace("\n", " | ")
			lines.append(f"OK [{user}] intent={res.get('intent')} mode={res.get('mode')} :: {snippet}")
		except Exception as e:
			ok = False
			lines.append(f"FAIL [{user}] {q}: {e}")
	frappe.set_user("Administrator")
	lines.append(f"PAGE={bool(frappe.db.exists('Page', 'pp-assistant'))}")
	lines.append("BOOTSTRAP_OK" if ok else "BOOTSTRAP_FAIL")
	return "\n".join(lines)
