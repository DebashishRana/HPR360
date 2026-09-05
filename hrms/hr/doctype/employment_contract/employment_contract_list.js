frappe.listview_settings["Employment Contract"] = {
	add_fields: ["status", "is_active", "wage", "start_date", "end_date", "employee_name"],
	get_indicator(doc) {
		const map = {
			Draft: ["Draft", "blue", "status,=,Draft"],
			Active: ["Active", "green", "status,=,Active"],
			Expired: ["Expired", "orange", "status,=,Expired"],
			Cancelled: ["Cancelled", "red", "status,=,Cancelled"],
		};
		return map[doc.status] || [__(doc.status), "gray", `status,=,${doc.status}`];
	},
	formatters: {
		is_active(value) {
			return value
				? `<span class="indicator-pill green">${__("Active")}</span>`
				: `<span class="indicator-pill gray">${__("Inactive")}</span>`;
		},
	},
};
