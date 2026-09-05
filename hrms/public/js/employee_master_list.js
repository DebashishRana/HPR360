const PEOPLEPAY360_EMPLOYEE_VIEW_CLASS = "peoplepay360-employee-view";

frappe.listview_settings["Employee"] = {
	onload(listview) {
		document.body.classList.add(PEOPLEPAY360_EMPLOYEE_VIEW_CLASS);

		listview.page.add_inner_button(__("Kanban View"), () => {
			frappe.set_route("List", "Employee", "Kanban");
		});

		listview.page.add_inner_button(__("Employee Form"), () => {
			frappe.new_doc("Employee");
		});
	},
	on_page_leave() {
		document.body.classList.remove(PEOPLEPAY360_EMPLOYEE_VIEW_CLASS);
	},
};
