frappe.listview_settings["Working Schedule"] = {
	add_fields: ["schedule_name", "schedule_type", "weekly_hours", "working_day_count", "is_active"],
	get_indicator(doc) {
		if (cint(doc.is_active)) {
			return [__("Active"), "green", "is_active,=,1"];
		}
		return [__("Inactive"), "gray", "is_active,=,0"];
	},
	onload(listview) {
		listview.page.add_inner_button(__("Setup Page"), () => {
			frappe.set_route("working-schedule-setup");
		});
		listview.page.add_inner_button(__("Assignments"), () => {
			frappe.set_route("List", "Working Schedule Assignment");
		});
	},
};
