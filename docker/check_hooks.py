import frappe

frappe.connect(site="hrms.localhost")
print("APPS", frappe.get_installed_apps())
print("WEB_JS", frappe.get_hooks("web_include_js"))
print("REDIRECTS", frappe.get_hooks("website_redirects"))
