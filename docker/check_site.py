import frappe

frappe.connect(site="hrms.localhost")
print("companies", frappe.get_all("Company", pluck="name"))
print("employees", frappe.db.count("Employee"))
print(
	"roles",
	frappe.get_all(
		"Role",
		filters={
			"name": [
				"in",
				[
					"Employee",
					"HR Manager",
					"HR User",
					"HR Payroll User",
					"HR Payroll Manager",
					"System Manager",
				],
			]
		},
		pluck="name",
	),
)
print("currency", frappe.db.get_value("Company", {"name": ("!=", "")}, "default_currency"))
