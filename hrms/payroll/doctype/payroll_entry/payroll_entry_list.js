// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.listview_settings["Payroll Entry"] = {
	has_indicator_for_draft: 1,
	onload(listview) {
		listview.page.set_primary_action(__("New"), () => {
			frappe.set_route("payrun-wizard");
		});
		listview.page.add_inner_button(__("Payrun Wizard"), () => {
			frappe.set_route("payrun-wizard");
		});
		listview.page.add_inner_button(__("Payrun Processing"), () => {
			frappe.set_route("payrun-processing");
		});
		listview.page.add_inner_button(__("Payroll Dashboard"), () => {
			frappe.set_route("payroll-dashboard");
		});
	},
	get_indicator(doc) {
		const status_color = {
			Draft: "red",
			Submitted: "blue",
			Queued: "orange",
			Failed: "red",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};
