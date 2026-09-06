frappe.listview_settings["Working Schedule Assignment"] = {
	add_fields: ["employee_name", "working_schedule", "status", "start_date", "end_date", "company"],
	has_indicator_for_draft: 1,
	get_indicator(doc) {
		return [__(doc.status), doc.status === "Active" ? "green" : "gray", `status,=,${doc.status}`];
	},
};
