frappe.listview_settings["Leave Type"] = {
	add_fields: [
		"leave_type_name",
		"leave_unit",
		"requires_allocation",
		"is_lwp",
		"is_earned_leave",
		"is_carry_forward",
		"max_leaves_allowed",
		"allow_negative",
	],
	get_indicator(doc) {
		if (cint(doc.requires_allocation)) {
			return [__("Allocation Required"), "blue", "requires_allocation,=,1"];
		}
		return [__("Open"), "gray", "requires_allocation,=,0"];
	},
	onload(listview) {
		listview.page.add_inner_button(__("Requests"), () => {
			frappe.set_route("List", "Leave Application");
		});
		listview.page.add_inner_button(__("Allocations"), () => {
			frappe.set_route("List", "Leave Allocation");
		});
	},
};
