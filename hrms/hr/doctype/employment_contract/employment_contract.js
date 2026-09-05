# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Employment Contract", {
	employee(frm) {
		if (!frm.doc.employee) return;
		frappe.db.get_value(
			"Employee",
			frm.doc.employee,
			["company", "department", "designation", "payroll_cost_center"],
			(r) => {
				if (!r) return;
				frm.set_value("company", r.company);
				frm.set_value("department", r.department);
				frm.set_value("designation", r.designation);
			}
		);
	},
	start_date(frm) {
		set_active_preview(frm);
	},
	end_date(frm) {
		set_active_preview(frm);
	},
});

function set_active_preview(frm) {
	if (!frm.doc.start_date) return;
	const today = frappe.datetime.get_today();
	let active = frm.doc.start_date <= today;
	if (frm.doc.end_date && frm.doc.end_date < today) active = false;
	frm.set_value("is_active", active ? 1 : 0);
}
