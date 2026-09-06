import frappe

frappe.init(site="hrms.localhost", sites_path="sites")
frappe.connect()
meta = frappe.get_meta("Workspace")
print("fields", [f.fieldname for f in meta.fields if "side" in (f.fieldname or "") or f.fieldname in ("content", "links", "roles")])
print("page", frappe.db.exists("Page", "pp-assistant"))
print("ws", frappe.db.exists("Workspace", "PeoplePay360"))
# child tables
print("table fields", [(f.fieldname, f.options) for f in meta.fields if f.fieldtype == "Table"])
