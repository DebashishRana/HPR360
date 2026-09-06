import frappe

USERS = [
	("hr.manager@example.com", "How many active employees do we have?"),
	("hr.manager@example.com", "Which leave requests are pending approval?"),
	("payroll.manager@example.com", "Give me a payroll readiness summary"),
	("admin.pp@example.com", "Give me a full PeoplePay360 status briefing"),
	("alex.employee@example.com", "What is my leave balance?"),
]


def run():
	from hrms.peoplepay360.chatbot.engine import answer

	ok = True
	out = []
	for user, q in USERS:
		frappe.set_user(user)
		try:
			res = answer(q, [])
			ans = (res.get("answer") or "")[:220].replace("\n", " | ")
			out.append(f"OK [{user}] intent={res.get('intent')} mode={res.get('mode')} :: {ans}")
		except Exception as e:
			ok = False
			out.append(f"FAIL [{user}] {q}: {e}")
	frappe.set_user("Administrator")
	out.append(f"PAGE={bool(frappe.db.exists('Page', 'pp-assistant'))}")
	out.append("BOOTSTRAP_OK" if ok else "BOOTSTRAP_FAIL")
	return "\n".join(out)
