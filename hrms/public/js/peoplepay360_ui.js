frappe.provide("hrms.peoplepay360");

hrms.peoplepay360.capabilities = null;

hrms.peoplepay360.load_capabilities = function () {
	return frappe
		.call({ method: "hrms.peoplepay360.roles.get_ui_capabilities" })
		.then((r) => {
			hrms.peoplepay360.capabilities = r.message || {};
			frappe.boot.peoplepay360 = hrms.peoplepay360.capabilities;
			return hrms.peoplepay360.capabilities;
		})
		.catch(() => {
			hrms.peoplepay360.capabilities = {};
			return {};
		});
};

hrms.peoplepay360.can = function (flag) {
	const caps = hrms.peoplepay360.capabilities || frappe.boot.peoplepay360 || {};
	return !!caps[flag];
};

/** Sidebar labels grouped by product capability */
hrms.peoplepay360.LINK_RULES = {
	payroll: [
		"Payroll",
		"Payrun Wizard",
		"Payruns",
		"Payrun Processing",
		"Payslips",
		"Salary Structures",
		"Salary Rules",
		"Payroll Dashboard",
		"Salary Register",
		"Payroll Settings",
	],
	hr_admin: [
		"Employee Onboarding",
		"Employee Separation",
		"Working Schedule Setup",
		"HR Settings",
		"Administration",
		"Time Off Types",
	],
	hr_ops: [
		"People",
		"Employees",
		"Contracts",
		"Attendance",
		"Working Schedules",
		"Schedule Assignments",
		"Time Off",
		"Requests",
		"Allocations",
		"Monthly Attendance Sheet",
	],
	employee_ok: ["Self Service", "Employee App", "Requests", "Attendance", "Payslips"],
};

hrms.peoplepay360.hide_workspace_links = function () {
	const caps = hrms.peoplepay360.capabilities || {};
	const rules = hrms.peoplepay360.LINK_RULES;

	const hide_set = new Set();

	if (!caps.can_view_payroll) {
		rules.payroll.forEach((l) => hide_set.add(l));
	}
	if (!caps.can_manage_employees) {
		rules.hr_admin.forEach((l) => hide_set.add(l));
	}
	if (caps.is_employee_only) {
		// Employee: only self-service-ish items + Assistant
		rules.payroll.forEach((l) => hide_set.add(l));
		rules.hr_admin.forEach((l) => hide_set.add(l));
		["People", "Employees", "Contracts", "Working Schedules", "Schedule Assignments", "Time Off Types", "Allocations", "Reports", "Administration"].forEach(
			(l) => hide_set.add(l)
		);
	}
	if (caps.is_hr_manager_only) {
		rules.payroll.forEach((l) => hide_set.add(l));
		hide_set.add("Payroll Settings");
	}
	if (!caps.can_edit_salary_structures) {
		// Payroll user can see structures but New is guarded elsewhere
	}
	if (!caps.is_admin && !caps.can_onboard_employees) {
		hide_set.add("Employee Onboarding");
		hide_set.add("Employee Separation");
	}

	const selectors = [
		".desk-sidebar .sidebar-item-label",
		".workspace-sidebar .item-anchor",
		".standard-sidebar-item",
		".sidebar-item-container .item-label",
		".desk-sidebar span",
	].join(", ");

	$(selectors).each(function () {
		const text = ($(this).text() || "").trim();
		if (!text) return;
		const match = [...hide_set].find((l) => text === l || text.includes(l));
		if (!match) return;
		const $item = $(this).closest(
			".sidebar-item-container, .standard-sidebar-item, li, .widget, .shortcut-widget-box, .desk-sidebar-item"
		);
		if ($item.length) $item.hide();
		else $(this).hide();
	});

	// Hide empty section headers that lost all children
	$(".sidebar-item-container").each(function () {
		const $section = $(this);
		if ($section.find(".sidebar-item-container:visible, .item-anchor:visible, a:visible").length === 0) {
			const label = ($section.find(".sidebar-item-label, .item-label").first().text() || "").trim();
			if (["People", "Time Off", "Payroll", "Reports", "Administration", "Self Service"].includes(label)) {
				// keep Self Service for employees
				if (caps.is_employee_only && label === "Self Service") return;
				if (!caps.can_view_payroll && label === "Payroll") $section.hide();
				if (!caps.can_manage_employees && label === "Administration") $section.hide();
			}
		}
	});
};

hrms.peoplepay360.apply_list_guards = function () {
	const caps = hrms.peoplepay360.capabilities || {};
	if (!cur_list) return;

	const clear_new = () => {
		try {
			cur_list.page.clear_primary_action();
		} catch (e) {
			/* ignore */
		}
	};

	if (!caps.can_create_payrun && cur_list.doctype === "Payroll Entry") clear_new();
	if (!caps.can_edit_salary_structures && cur_list.doctype === "Salary Structure") clear_new();
	if (!caps.can_edit_salary_rules && cur_list.doctype === "Salary Component") clear_new();
	if (!caps.can_onboard_employees && ["Employee Onboarding", "Employee Separation"].includes(cur_list.doctype))
		clear_new();
	if (
		!caps.can_manage_employees &&
		["Employee", "Employment Contract", "Working Schedule", "Leave Type"].includes(cur_list.doctype)
	)
		clear_new();
};

hrms.peoplepay360.apply_form_guards = function () {
	const caps = hrms.peoplepay360.capabilities || {};
	if (!cur_frm) return;

	const remove_btn = (label) => {
		try {
			cur_frm.page.remove_inner_button(label);
		} catch (e) {
			/* ignore */
		}
	};

	if (cur_frm.doctype === "Leave Application" && !caps.can_approve_time_off) {
		["Approve", "Refuse", "Reject"].forEach(remove_btn);
	}
	if (["Employee Onboarding", "Employee Separation"].includes(cur_frm.doctype) && !caps.can_onboard_employees) {
		cur_frm.disable_form();
	}
	if (["Payroll Entry", "Salary Slip"].includes(cur_frm.doctype) && !caps.can_view_payroll && !caps.is_employee_only) {
		cur_frm.disable_form();
	}
	if (cur_frm.doctype === "Salary Structure" && !caps.can_edit_salary_structures) {
		cur_frm.set_read_only();
	}
	if (cur_frm.doctype === "Salary Component" && !caps.can_edit_salary_rules) {
		cur_frm.set_read_only();
	}
};

$(document).on("app_ready", function () {
	hrms.peoplepay360.load_capabilities().then(() => {
		hrms.peoplepay360.hide_workspace_links();
	});
});

$(document).on("page-change", function () {
	setTimeout(() => {
		hrms.peoplepay360.hide_workspace_links();
		hrms.peoplepay360.apply_list_guards();
		hrms.peoplepay360.apply_form_guards();
	}, 250);
});

$(document).on("form-refresh", function () {
	setTimeout(() => hrms.peoplepay360.apply_form_guards(), 100);
});
