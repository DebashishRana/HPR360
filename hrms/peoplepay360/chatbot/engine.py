# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

"""PeoplePay360 assistant answer engine — grounded on live HR context."""

from __future__ import annotations

import json
import re
from typing import Any

import frappe
import requests
from frappe.utils import cint, flt

from hrms.peoplepay360.chatbot.context import (
	build_org_snapshot,
	employee_dossier,
	find_employees,
	snapshot_as_text,
)
from hrms.peoplepay360.roles import get_ui_capabilities


SUGGESTIONS = {
	"hr": [
		"How many active employees do we have?",
		"Which leave requests are pending approval?",
		"Show attendance health for the last 7 days",
		"Any employees with overlapping active contracts?",
		"Summarize headcount by department",
	],
	"payroll": [
		"What is total net pay in the last 90 days?",
		"How many payslips are still in draft?",
		"Who is missing bank account details?",
		"How many active salary structures are configured?",
		"Give me a payroll readiness summary",
	],
	"admin": [
		"Give me a full PeoplePay360 status briefing",
		"What needs attention across HR and payroll?",
		"List top departments by headcount",
		"Pending leave + payroll warnings overview",
	],
	"employee": [
		"What is my leave balance?",
		"Show my recent attendance",
		"Do I have any pending leave requests?",
	],
}


def assert_chat_access() -> dict:
	caps = get_ui_capabilities()
	# Employees can use limited self-assistant; HR/Payroll/Admin get full org brain
	if caps.get("can_use_assistant") or caps.get("is_employee_only") or caps.get("can_manage_employees") or caps.get("can_view_payroll") or caps.get("is_admin"):
		return caps
	# Fallback: any logged-in desk user with Employee role
	roles = set(frappe.get_roles())
	if "Employee" in roles or "System Manager" in roles or "HR Manager" in roles:
		caps["can_use_assistant"] = True
		return caps
	frappe.throw("You do not have access to the PeoplePay360 Assistant", frappe.PermissionError)


def suggestions_for(caps: dict) -> list[str]:
	if caps.get("is_admin"):
		return SUGGESTIONS["admin"] + SUGGESTIONS["payroll"][:2]
	if caps.get("can_view_payroll"):
		return SUGGESTIONS["payroll"] + SUGGESTIONS["hr"][:2]
	if caps.get("can_manage_employees"):
		return SUGGESTIONS["hr"]
	return SUGGESTIONS["employee"]


def _detect_employee_query(message: str) -> str | None:
	"""Try to resolve an employee id/name mentioned in the question."""
	# Explicit patterns: employee EMP-0001 / for John
	m = re.search(r"\b(HR-EMP-\d+|EMP-\d+|PP-EMP-\d+)\b", message, re.I)
	if m and frappe.db.exists("Employee", m.group(1)):
		return m.group(1)

	# "for <Name>" / "about <Name>"
	m = re.search(r"\b(?:for|about|regarding|employee)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", message)
	if m:
		hits = find_employees(m.group(1), limit=1)
		if hits:
			return hits[0].name

	# Fuzzy: any active employee name contained in message
	names = frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "employee_name"],
		limit_page_length=200,
	)
	msg_l = message.lower()
	for row in names:
		if row.employee_name and len(row.employee_name) > 3 and row.employee_name.lower() in msg_l:
			return row.name
	return None


def _intent(message: str) -> str:
	m = message.lower()
	# Specific domains first so "payroll readiness summary" stays payroll, etc.
	if any(k in m for k in ("leave", "time off", "pto", "vacation", "allocation", "pending request", "leave balance")):
		return "leave"
	if any(k in m for k in ("attendance", "present", "absent", "late", "check-in", "checkin")):
		return "attendance"
	if any(k in m for k in ("payroll", "payslip", "salary", "net pay", "payrun", "bank", "readiness")):
		return "payroll"
	if any(k in m for k in ("contract", "wage", "overlap")):
		return "contracts"
	if any(k in m for k in ("department", "headcount", "staffing")) or (
		("how many" in m or "number of" in m or "count" in m) and ("employee" in m or "staff" in m or "headcount" in m)
	):
		return "headcount"
	if any(k in m for k in ("schedule", "shift", "working hour")):
		return "schedule"
	if any(k in m for k in ("brief", "overview", "summary", "status", "dashboard", "health", "attention")):
		return "briefing"
	return "general"


def _fmt_money(n) -> str:
	try:
		return f"{flt(n):,.2f}"
	except Exception:
		return str(n)


def _answer_deterministic(message: str, caps: dict, snap: dict, dossier: dict | None) -> dict:
	intent = _intent(message)
	sources: list[str] = ["Employee", "Attendance", "Leave Application"]
	parts: list[str] = []

	if dossier:
		parts.append(
			f"**{dossier.get('employee_name')}** (`{dossier.get('name')}`) — "
			f"{dossier.get('status')}, {dossier.get('designation') or '—'} in {dossier.get('department') or '—'}."
		)
		if dossier.get("contracts"):
			active = [c for c in dossier["contracts"] if c.get("status") == "Active"]
			parts.append(
				f"Contracts on file: {len(dossier['contracts'])} "
				f"({len(active)} active). "
				+ (
					f"Active wage: {_fmt_money(active[0].get('wage'))}."
					if active
					else "No active contract."
				)
			)
			sources.append("Employment Contract")
		if dossier.get("leave_allocations") or intent == "leave":
			if dossier.get("leave_allocations"):
				bal = ", ".join(
					f"{a.leave_type}: {flt(a.unused_leaves):.1f} remaining "
					f"(of {flt(a.total_leaves_allocated):.1f})"
					for a in dossier["leave_allocations"][:5]
				)
				parts.append(f"Leave balances — {bal}.")
			else:
				parts.append("No active leave allocations on file for this employee.")
			apps = dossier.get("leave_applications") or []
			open_apps = [a for a in apps if a.get("status") == "Open"]
			if open_apps:
				parts.append(
					"Pending leave requests: "
					+ "; ".join(
						f"{a.leave_type} {a.from_date}→{a.to_date} ({a.name})" for a in open_apps[:4]
					)
					+ "."
				)
			elif intent == "leave":
				parts.append("No pending leave requests.")
			sources.append("Leave Allocation")
		if dossier.get("attendance_30d") or intent == "attendance":
			att = ", ".join(f"{k}: {v}" for k, v in (dossier.get("attendance_30d") or {}).items()) or "no rows"
			parts.append(f"Attendance (30 days) — {att}.")
		if dossier.get("recent_payslips") and (caps.get("can_view_payroll") or caps.get("is_employee_only")):
			slip = dossier["recent_payslips"][0]
			parts.append(
				f"Latest payslip `{slip.name}` net {_fmt_money(slip.net_pay)} "
				f"({slip.start_date} → {slip.end_date})."
			)
			sources.append("Salary Slip")

		# Self / named-employee answers: prefer dossier over org rollups
		if caps.get("is_employee_only") or intent in ("leave", "attendance", "contracts", "general", "payroll"):
			if intent != "headcount" and intent != "briefing":
				return {
					"answer": "\n\n".join(parts),
					"intent": "employee" if intent == "general" else intent,
					"sources": list(dict.fromkeys(sources)),
					"mode": "context",
				}
			if intent == "general" and parts:
				return {
					"answer": "\n\n".join(parts),
					"intent": "employee",
					"sources": list(dict.fromkeys(sources)),
					"mode": "context",
				}

	# Org-level intents
	if caps.get("is_employee_only") and not dossier:
		# Bind to linked employee
		emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
		if emp:
			dossier = employee_dossier(emp, caps)
			return _answer_deterministic(message + f" for {dossier.get('employee_name')}", caps, snap, dossier)
		return {
			"answer": "I can help with your own PeoplePay360 records once your User is linked to an Employee.",
			"intent": intent,
			"sources": [],
			"mode": "context",
		}

	if intent == "briefing" or intent == "general":
		parts = [
			"### PeoplePay360 briefing",
			snapshot_as_text(snap, caps),
		]
		if snap.get("time_off", {}).get("pending_sample"):
			parts.append("**Pending leave approvals:**")
			for r in snap["time_off"]["pending_sample"][:5]:
				parts.append(
					f"- {r.employee_name or r.employee}: {r.leave_type} "
					f"{r.from_date} → {r.to_date} ({flt(r.total_leave_days)} days)"
				)
		if caps.get("can_view_payroll") and snap.get("payroll"):
			p = snap["payroll"]
			parts.append(
				f"**Payroll watchouts:** {p.get('employees_missing_bank', 0)} active employees missing bank details; "
				f"{p.get('payslips_draft', 0)} draft payslips."
			)
			sources.extend(["Salary Slip", "Payroll Entry", "Salary Structure"])
		if snap.get("contracts", {}).get("overlap_warnings"):
			parts.append(
				f"**Contract attention:** {len(snap['contracts']['overlap_warnings'])} employee(s) have multiple Active contracts."
			)
			sources.append("Employment Contract")
		return {
			"answer": "\n\n".join(parts),
			"intent": "briefing",
			"sources": list(dict.fromkeys(sources)),
			"mode": "context",
		}

	if intent == "headcount":
		emp = snap.get("employees") or {}
		depts = snap.get("headcount_by_department") or {}
		lines = [
			f"There are **{emp.get('active', 0)} active employees** "
			f"(total records: {emp.get('total', 0)}; left: {emp.get('left', 0)}).",
			"**By department:**",
		]
		for d, c in depts.items():
			lines.append(f"- {d}: {c}")
		return {"answer": "\n".join(lines), "intent": intent, "sources": ["Employee"], "mode": "context"}

	if intent == "leave":
		t = snap.get("time_off") or {}
		lines = [
			f"Pending leave requests: **{t.get('pending_requests', 0)}**. "
			f"Approved: {t.get('approved_requests', 0)}. Active allocations: {t.get('active_allocations', 0)}.",
		]
		for r in (t.get("pending_sample") or [])[:6]:
			lines.append(
				f"- `{r.name}` — {r.employee_name or r.employee}, {r.leave_type}, "
				f"{r.from_date} → {r.to_date}"
			)
		if not t.get("pending_sample"):
			lines.append("No open leave requests right now.")
		return {
			"answer": "\n".join(lines),
			"intent": intent,
			"sources": ["Leave Application", "Leave Allocation"],
			"mode": "context",
		}

	if intent == "attendance":
		a7 = (snap.get("attendance") or {}).get("last_7_days") or {}
		a30 = (snap.get("attendance") or {}).get("last_30_days") or {}
		lines = [
			"**Attendance last 7 days:** " + (", ".join(f"{k}={v}" for k, v in a7.items()) or "no data"),
			"**Attendance last 30 days:** " + (", ".join(f"{k}={v}" for k, v in a30.items()) or "no data"),
		]
		present = cint(a7.get("Present", 0))
		absent = cint(a7.get("Absent", 0))
		if present + absent:
			health = present / max(present + absent, 1)
			lines.append(f"Rough presence ratio (7d Present/(Present+Absent)): **{health:.0%}**.")
		return {"answer": "\n".join(lines), "intent": intent, "sources": ["Attendance"], "mode": "context"}

	if intent == "contracts":
		c = snap.get("contracts") or {}
		lines = [
			f"Active contracts: **{c.get('active', 0)}**, expired: {c.get('expired', 0)}, draft: {c.get('draft', 0)}.",
		]
		for o in c.get("overlap_warnings") or []:
			lines.append(f"- Overlap risk: employee `{o['employee']}` has {o['active_contracts']} Active contracts")
		if not c.get("overlap_warnings"):
			lines.append("No concurrent Active contract overlaps detected.")
		return {
			"answer": "\n".join(lines),
			"intent": intent,
			"sources": ["Employment Contract"],
			"mode": "context",
		}

	if intent == "payroll":
		if not caps.get("can_view_payroll"):
			return {
				"answer": "Payroll details are restricted for your role. Ask an HR Payroll User or Admin.",
				"intent": intent,
				"sources": [],
				"mode": "context",
			}
		p = snap.get("payroll") or {}
		lines = [
			f"Active salary structures: **{p.get('salary_structures', 0)}**, salary rules/components: {p.get('salary_components', 0)}.",
			f"Payslips — submitted: {p.get('payslips_submitted', 0)}, draft: {p.get('payslips_draft', 0)}.",
			f"Employees missing bank account: **{p.get('employees_missing_bank', 0)}**.",
		]
		if p.get("last_90_days"):
			l = p["last_90_days"]
			lines.append(
				f"Last 90 days: total net **{_fmt_money(l.get('total_net'))}** "
				f"across {l.get('payslips')} payslips (avg {_fmt_money(l.get('average_net'))})."
			)
		return {
			"answer": "\n".join(lines),
			"intent": intent,
			"sources": ["Salary Slip", "Salary Structure", "Employee"],
			"mode": "context",
		}

	if intent == "schedule":
		s = snap.get("schedules") or {}
		return {
			"answer": f"Active working schedules: **{s.get('active', 0)}**. Active assignments: {s.get('assignments', 0)}.",
			"intent": intent,
			"sources": ["Working Schedule", "Working Schedule Assignment"],
			"mode": "context",
		}

	# Fallback briefing
	return _answer_deterministic("status briefing", caps, snap, dossier)


def _openai_answer(message: str, history: list, context_text: str, caps: dict) -> str | None:
	key = frappe.conf.get("peoplepay360_openai_key") or frappe.conf.get("openai_api_key")
	if not key:
		return None

	role_line = "Admin" if caps.get("is_admin") else (
		"Payroll" if caps.get("can_view_payroll") else ("HR Manager" if caps.get("can_manage_employees") else "Employee")
	)
	system = (
		"You are PeoplePay360 Assistant, an internal HR & Payroll copilot. "
		f"The signed-in user role context is: {role_line}. "
		"Answer ONLY using the provided live system context. "
		"If data is missing, say what is missing. Be concise, structured, and accurate. "
		"Never invent employee names, amounts, or statuses. Use markdown."
	)
	messages = [{"role": "system", "content": system + "\n\nLIVE CONTEXT:\n" + context_text}]
	for h in (history or [])[-8:]:
		role = "assistant" if h.get("role") == "assistant" else "user"
		messages.append({"role": role, "content": h.get("content") or ""})
	messages.append({"role": "user", "content": message})

	try:
		resp = requests.post(
			"https://api.openai.com/v1/chat/completions",
			headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
			json={"model": frappe.conf.get("peoplepay360_openai_model") or "gpt-4o-mini", "messages": messages, "temperature": 0.2},
			timeout=40,
		)
		resp.raise_for_status()
		data = resp.json()
		return data["choices"][0]["message"]["content"]
	except Exception as e:
		frappe.log_error(title="PeoplePay360 Assistant LLM", message=str(e))
		return None


def answer(message: str, history: list | None = None) -> dict[str, Any]:
	caps = assert_chat_access()
	message = (message or "").strip()
	if not message:
		frappe.throw("Please enter a question")

	# Employee-only: force self dossier when possible
	dossier = None
	emp_id = None
	if caps.get("is_employee_only"):
		emp_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	elif caps.get("can_manage_employees") or caps.get("can_view_payroll") or caps.get("is_admin"):
		emp_id = _detect_employee_query(message)

	if emp_id:
		# Employees may only open their own dossier
		if caps.get("is_employee_only"):
			own = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
			if emp_id != own:
				frappe.throw("You can only ask about your own employee record", frappe.PermissionError)
		dossier = employee_dossier(emp_id, caps)

	snap = build_org_snapshot(caps) if not caps.get("is_employee_only") else {
		"as_of": frappe.utils.today(),
		"employees": {},
	}
	# Always allow self snapshot pieces for employees via dossier

	context_text = snapshot_as_text(snap, caps) if not caps.get("is_employee_only") else ""
	if dossier:
		context_text += "\n\nEMPLOYEE DOSSIER:\n" + json.dumps(dossier, default=str)[:6000]

	llm = _openai_answer(message, history or [], context_text, caps)
	base = _answer_deterministic(message, caps, snap, dossier)

	if llm:
		return {
			"answer": llm,
			"intent": base.get("intent"),
			"sources": base.get("sources") or [],
			"mode": "llm+context",
			"suggestions": suggestions_for(caps),
			"snapshot_digest": snapshot_as_text(snap, caps) if not caps.get("is_employee_only") else None,
		}

	base["suggestions"] = suggestions_for(caps)
	base["snapshot_digest"] = snapshot_as_text(snap, caps) if not caps.get("is_employee_only") else None
	return base
