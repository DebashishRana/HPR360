frappe.listview_settings["Employment Contract"] = {
	add_fields: ["employee_name", "status", "start_date", "end_date", "wage", "currency", "department", "position"],
	has_indicator_for_draft: 1,
	onload(listview) {
		document.body.classList.add("peoplepay360-contract-view");
		listview.page.add_inner_button(__("Active Contracts"), () => listview.filter_area.add([["Employment Contract", "status", "=", "Active"]]));
	},
	on_page_leave() { document.body.classList.remove("peoplepay360-contract-view"); },
	get_indicator(doc) {
		const colors = {Draft: "orange", Active: "green", Expired: "gray", Cancelled: "red"};
		return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
	},
};
