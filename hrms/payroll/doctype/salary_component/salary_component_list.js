frappe.listview_settings["Salary Component"] = {
	add_fields: ["salary_component", "salary_component_abbr", "type", "category", "disabled"],
	get_indicator(doc) {
		if (cint(doc.disabled)) {
			return [__("Disabled"), "gray", "disabled,=,1"];
		}
		const colors = {
			Basic: "blue",
			Allowance: "green",
			Gross: "teal",
			Deduction: "red",
			Net: "purple",
			"Employer Contribution": "orange",
			Other: "gray",
			Earning: "green",
		};
		const label = doc.category || doc.type || "Component";
		return [
			__(label),
			colors[label] || "blue",
			doc.category ? `category,=,${doc.category}` : `type,=,${doc.type}`,
		];
	},
	onload(listview) {
		listview.page.add_inner_button(__("Earnings"), () => {
			listview.filter_area.add([["Salary Component", "type", "=", "Earning"]]);
		});
		listview.page.add_inner_button(__("Deductions"), () => {
			listview.filter_area.add([["Salary Component", "type", "=", "Deduction"]]);
		});
		listview.page.add_inner_button(__("Basic / Allowances"), () => {
			listview.filter_area.add([["Salary Component", "category", "in", ["Basic", "Allowance"]]]);
		});
		listview.page.add_inner_button(__("Salary Structures"), () => {
			frappe.set_route("List", "Salary Structure");
		});
	},
};
