frappe.ui.form.on("Employment Contract", {
	refresh(frm) {
		if (frm.doc.status === "Active") {
			frm.dashboard.set_headline_alert(
				__("This is the active contract for {0}", [frm.doc.employee_name || frm.doc.employee]),
				"green",
			);
		} else if (frm.doc.status === "Expired") {
			frm.dashboard.set_headline_alert(__("This contract has expired."), "orange");
		}

		if (!frm.is_new() && frm.doc.employee) {
			frm.add_custom_button(__("Open Employee"), () => {
				frappe.set_route("Form", "Employee", frm.doc.employee);
			});
			frm.add_custom_button(__("Attendance"), () => {
				frappe.route_options = { employee: frm.doc.employee };
				frappe.set_route("List", "Attendance");
			}, __("Related"));
			frm.add_custom_button(__("Time Off"), () => {
				frappe.route_options = { employee: frm.doc.employee };
				frappe.set_route("List", "Leave Application");
			}, __("Related"));
			frm.add_custom_button(__("Payslips"), () => {
				frappe.route_options = { employee: frm.doc.employee };
				frappe.set_route("List", "Salary Slip");
			}, __("Related"));
		}
	},

	employee(frm) {
		if (!frm.doc.employee) return;
		frappe.db.get_value("Employee", frm.doc.employee, ["department", "designation", "salary_currency"], (r) => {
			if (!r) return;
			if (!frm.doc.department && r.department) frm.set_value("department", r.department);
			if (!frm.doc.position && r.designation) frm.set_value("position", r.designation);
			if (!frm.doc.currency && r.salary_currency) frm.set_value("currency", r.salary_currency);
		});
	},
});
