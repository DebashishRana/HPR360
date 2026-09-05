frappe.listview_settings["Shift Schedule"] = {
	onload: (list_view) => {
		hrms.add_shift_tools_button_to_list(list_view, "Assign Shift Schedule");
		list_view.page.add_inner_button(__("Working Schedule Setup"), () => {
			frappe.set_route("working-schedule-setup");
		});
	},
};
