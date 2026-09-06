# Copyright (c) 2026, PeoplePay360
# License: GNU General Public License v3

"""Whitelisted API for PeoplePay360 Assistant."""

from __future__ import annotations

import frappe

from hrms.peoplepay360.chatbot.engine import answer, assert_chat_access, suggestions_for


@frappe.whitelist()
def get_assistant_bootstrap() -> dict:
	caps = assert_chat_access()
	return {
		"title": "PeoplePay360 Assistant",
		"subtitle": "Ask anything about employees, time off, attendance, contracts, or payroll — answers use live system data.",
		"suggestions": suggestions_for(caps),
		"capabilities": caps,
		"welcome": (
			"Hi — I'm your PeoplePay360 Assistant. I answer from live HR & Payroll records "
			"for your role. Try a suggested question or ask about a specific employee."
		),
	}


@frappe.whitelist()
def ask_assistant(message: str, history: str | list | None = None) -> dict:
	"""Main chat endpoint. `history` may be JSON string of [{role, content}, ...]."""
	if isinstance(history, str):
		import json

		try:
			history = json.loads(history) if history else []
		except Exception:
			history = []
	return answer(message, history or [])
