frappe.listview_settings["Employee"] = {
	add_fields: ["status", "department", "designation", "branch", "image"],
	get_indicator(doc) {
		const colors = {
			Active: "green",
			Inactive: "red",
			Suspended: "orange",
			Left: "gray",
		};
		return [__(doc.status), colors[doc.status] || "blue", "status,=," + doc.status];
	},
	onload(listview) {
		// Encourage Kanban by status for PeoplePay360 demo
		if (!listview.page.fields_dict.status) {
			listview.page.add_inner_button(__("Kanban by Status"), () => {
				frappe.set_route("List", "Employee", "Kanban", "Employee Status");
			});
		}
		listview.page.add_inner_button(__("New Employment Contract"), () => {
			frappe.new_doc("Employment Contract");
		});
	},
};
