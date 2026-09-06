frappe.listview_settings["Leave Allocation"] = {
	add_fields: [
		"employee",
		"employee_name",
		"leave_type",
		"from_date",
		"to_date",
		"new_leaves_allocated",
		"total_leaves_allocated",
		"leaves_taken",
		"docstatus",
	],
	get_indicator(doc) {
		if (doc.docstatus === 1) {
			return [__("Approved"), "green", "docstatus,=,1"];
		}
		if (doc.docstatus === 2) {
			return [__("Cancelled"), "red", "docstatus,=,2"];
		}
		return [__("Draft"), "orange", "docstatus,=,0"];
	},
	onload(listview) {
		listview.page.add_inner_button(__("Requests"), () => {
			frappe.set_route("List", "Leave Application");
		});
		listview.page.add_inner_button(__("Time Off Types"), () => {
			frappe.set_route("List", "Leave Type");
		});
	},
	formatters: {
		leaves_taken(value, df, doc) {
			const allocated = Number(doc.total_leaves_allocated || doc.new_leaves_allocated || 0);
			const taken = Number(value || 0);
			const remaining = allocated - taken;
			return `${taken} ${__("taken")} · <strong>${remaining}</strong> ${__("left")}`;
		},
	},
};
