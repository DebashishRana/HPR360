frappe.listview_settings["Leave Application"] = {
	add_fields: [
		"leave_type",
		"employee",
		"employee_name",
		"total_leave_days",
		"from_date",
		"to_date",
		"status",
	],
	has_indicator_for_draft: 1,
	get_indicator: function (doc) {
		const status_color = {
			Approved: "green",
			Rejected: "red",
			Open: "orange",
			Draft: "red",
			Cancelled: "red",
			Submitted: "blue",
		};
		const status =
			!doc.docstatus && ["Approved", "Rejected"].includes(doc.status) ? "Draft" : doc.status;
		return [__(status), status_color[status], "status,=," + doc.status];
	},
	onload(listview) {
		document.body.classList.add("peoplepay360-timeoff-view");
		listview.page.add_inner_button(__("Pending Approval"), () => {
			listview.filter_area.add([["Leave Application", "status", "=", "Open"]]);
		});
		listview.page.add_inner_button(__("Approved"), () => {
			listview.filter_area.add([["Leave Application", "status", "=", "Approved"]]);
		});
		listview.page.add_inner_button(__("Allocations"), () => {
			frappe.set_route("List", "Leave Allocation");
		});
		listview.page.add_inner_button(__("Time Off Types"), () => {
			frappe.set_route("List", "Leave Type");
		});
	},
	on_page_leave() {
		document.body.classList.remove("peoplepay360-timeoff-view");
	},
};
