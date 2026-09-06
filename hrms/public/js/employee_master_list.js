const PEOPLEPAY360_EMPLOYEE_VIEW_CLASS = "peoplepay360-employee-view";

frappe.listview_settings["Employee"] = {
	add_fields: ["status", "department", "designation", "reports_to", "company", "image"],
	get_indicator(doc) {
		const colors = {
			Active: "green",
			Inactive: "gray",
			Suspended: "orange",
			Left: "red",
		};
		return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
	},
	onload(listview) {
		document.body.classList.add(PEOPLEPAY360_EMPLOYEE_VIEW_CLASS);
		patch_employee_kanban_dialog();

		listview.page.add_inner_button(__("Kanban View"), () => {
			frappe
				.xcall("hrms.overrides.employee_master.create_employee_kanban_board", {
					board_name: "Employee Status",
				})
				.then((board) => {
					frappe.set_route("List", "Employee", "Kanban", board.kanban_board_name);
				});
		});

		listview.page.add_inner_button(__("List View"), () => {
			frappe.set_route("List", "Employee", "List");
		});

		listview.page.add_inner_button(__("New Employee"), () => {
			frappe.new_doc("Employee");
		});
	},
	on_page_leave() {
		document.body.classList.remove(PEOPLEPAY360_EMPLOYEE_VIEW_CLASS);
	},
};

function patch_employee_kanban_dialog() {
	if (frappe.views.KanbanView._employee_kanban_patched) return;

	const original = frappe.views.KanbanView.show_kanban_dialog;
	frappe.views.KanbanView.show_kanban_dialog = function (doctype) {
		if (doctype !== "Employee") {
			return original.call(this, doctype);
		}
		frappe
			.xcall("hrms.overrides.employee_master.create_employee_kanban_board", {
				board_name: "Employee Status",
			})
			.then((board) => {
				frappe.set_route("List", "Employee", "Kanban", board.kanban_board_name);
			});
	};

	frappe.views.KanbanView._employee_kanban_patched = true;
}
