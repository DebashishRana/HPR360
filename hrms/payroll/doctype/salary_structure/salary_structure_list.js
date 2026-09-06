frappe.listview_settings["Salary Structure"] = {
	add_fields: ["is_active", "payroll_frequency", "company"],
	get_indicator(doc) {
		if (doc.is_active === "Yes" || cint(doc.is_active) === 1) {
			return [__("Active"), "green", "is_active,=,Yes"];
		}
		return [__("Inactive"), "gray", "is_active,=,No"];
	},
	onload(list_view) {
		list_view.page.add_inner_button(__("Bulk Salary Structure Assignment"), () => {
			frappe.set_route("Form", "Bulk Salary Structure Assignment");
		});
		list_view.page.add_inner_button(__("Salary Rules"), () => {
			frappe.set_route("List", "Salary Component");
		});
		list_view.page.add_inner_button(__("Payrun Wizard"), () => {
			frappe.set_route("payrun-wizard");
		});

		// Enrich rows with rule + assigned employee counts
		frappe.call({
			method: "hrms.payroll.doctype.salary_structure.salary_structure.get_structure_list_stats",
			callback(r) {
				const stats = r.message || {};
				list_view.structure_stats = stats;
				list_view.refresh();
			},
		});
	},
	formatters: {
		name(value, _df, doc) {
			const stats = cur_list?.structure_stats?.[doc.name] || {};
			const rules = stats.rules ?? "—";
			const emps = stats.employees ?? "—";
			return `${value}<br><span class="text-muted" style="font-size:11px">${__("Rules")}: ${rules} · ${__("Employees")}: ${emps}</span>`;
		},
	},
};
