// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings["Payroll Entry"] = {
	has_indicator_for_draft: 1,
	onload(listview) {
		listview.page.set_primary_action(__("New"), () => {
			open_payrun_wizard();
		});
		listview.page.add_inner_button(__("Payrun Processing"), () => {
			frappe.set_route("payrun-processing");
		});
	},
	get_indicator: function (doc) {
		var status_color = {
			Draft: "red",
			Submitted: "blue",
			Queued: "orange",
			Failed: "red",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};

function open_payrun_wizard() {
	const state = {
		scope: {},
		employees: [],
	};

	const step1 = new frappe.ui.Dialog({
		title: __("New Payroll Entry"),
		size: "large",
		fields: [
			{
				fieldname: "company",
				fieldtype: "Link",
				label: __("Company"),
				options: "Company",
				reqd: 1,
				default: frappe.defaults.get_default("Company"),
				change() {
					set_company_defaults(step1);
				},
			},
			{
				fieldname: "posting_date",
				fieldtype: "Date",
				label: __("Posting Date"),
				reqd: 1,
				default: frappe.datetime.nowdate(),
			},
			{
				fieldname: "salary_slip_based_on_timesheet",
				fieldtype: "Check",
				label: __("Salary Slip Based on Timesheet"),
				default: 0,
			},
			{
				fieldname: "payroll_frequency",
				fieldtype: "Select",
				label: __("Payroll Frequency"),
				options: "\nMonthly\nFortnightly\nBimonthly\nWeekly\nDaily",
				change() {
					set_end_date(step1);
				},
			},
			{
				fieldname: "start_date",
				fieldtype: "Date",
				label: __("Start Date"),
				reqd: 1,
				change() {
					set_end_date(step1);
				},
			},
			{
				fieldname: "end_date",
				fieldtype: "Date",
				label: __("End Date"),
				reqd: 1,
			},
			{
				fieldname: "branch",
				fieldtype: "Link",
				label: __("Branch"),
				options: "Branch",
			},
			{
				fieldname: "department",
				fieldtype: "Link",
				label: __("Department"),
				options: "Department",
			},
			{
				fieldname: "designation",
				fieldtype: "Link",
				label: __("Designation"),
				options: "Designation",
			},
			{
				fieldname: "grade",
				fieldtype: "Link",
				label: __("Grade"),
				options: "Employee Grade",
			},
			{
				fieldname: "currency",
				fieldtype: "Link",
				label: __("Currency"),
				options: "Currency",
				reqd: 1,
			},
			{
				fieldname: "payroll_payable_account",
				fieldtype: "Link",
				label: __("Payroll Payable Account"),
				options: "Account",
				reqd: 1,
			},
		],
		primary_action_label: __("Continue"),
		primary_action(values) {
			if (!values.salary_slip_based_on_timesheet && !values.payroll_frequency) {
				frappe.throw(__("Payroll Frequency is required for period-based payruns."));
			}

			if (!values.start_date || !values.end_date) {
				frappe.throw(__("Select both Start Date and End Date."));
			}

			state.scope = values;
			load_payrun_employees(state, step1);
		},
	});

	if (step1.get_field("company")?.value) {
		set_company_defaults(step1);
	}

	step1.show();

	function set_company_defaults(dialog) {
		const company = dialog.get_value("company");
		if (!company) return;

		frappe.db.get_value(
			"Company",
			company,
			["default_currency", "default_payroll_payable_account"],
			(r) => {
				if (!r?.message) return;
				dialog.set_value("currency", r.message.default_currency);
				dialog.set_value("payroll_payable_account", r.message.default_payroll_payable_account);
			},
		);
	}

	function set_end_date(dialog) {
		const payroll_frequency = dialog.get_value("payroll_frequency");
		const start_date = dialog.get_value("start_date");
		if (!payroll_frequency || !start_date) return;

		frappe.call({
			method: "hrms.payroll.doctype.payroll_entry.payroll_entry.get_start_end_dates",
			args: {
				payroll_frequency,
				start_date,
			},
		}).then((r) => {
			if (r.message?.end_date) {
				dialog.set_value("end_date", r.message.end_date);
			}
		});
	}

	function load_payrun_employees(state, step1_dialog) {
		frappe.call({
			method: "hrms.payroll.doctype.payroll_entry.payroll_entry.get_payrun_wizard_employees",
			args: {
				filters: state.scope,
			},
			freeze: true,
			freeze_message: __("Fetching eligible employees..."),
		}).then((r) => {
			state.employees = r.message?.employees || [];

			if (!state.employees.length) {
				frappe.msgprint({
					title: __("No Employees Found"),
					message: __(
						"No eligible employees were found for the selected payroll scope and period."
					),
					indicator: "orange",
				});
				return;
			}

			step1_dialog.hide();
			render_employee_step(state);
		});
	}

	function render_employee_step(state) {
		const step2 = new frappe.ui.Dialog({
			title: __("Select Employees"),
			size: "extra-large",
			fields: [
				{
					fieldname: "employee_html",
					fieldtype: "HTML",
				},
			],
			primary_action_label: __("Create Payrun"),
			primary_action() {
				const selected = get_selected_employees(step2);
				if (!selected.length) {
					frappe.throw(__("Select at least one employee to create the payrun."));
				}
				create_payrun(state, selected);
			},
		});

		step2.get_field("employee_html").$wrapper.html(render_employee_table(state.employees));
		bind_employee_table_events(step2);
		step2.show();
	}

	function render_employee_table(employees) {
		const rows = employees
			.map((employee) => {
				const employee_name = frappe.utils.escape_html(employee.employee_name || "");
				const employee_id = frappe.utils.escape_html(employee.employee || "");
				const department = frappe.utils.escape_html(employee.department || "");
				const designation = frappe.utils.escape_html(employee.designation || "");
				return `
					<tr>
						<td class="text-center">
							<input type="checkbox" class="payrun-employee-select" checked data-employee="${employee_id}">
						</td>
						<td>${employee_id}</td>
						<td>${employee_name}</td>
						<td>${department}</td>
						<td>${designation}</td>
						<td>${employee.is_salary_withheld ? __("Yes") : __("No")}</td>
					</tr>
				`;
			})
			.join("");

		return `
			<div class="d-flex flex-wrap align-items-center justify-content-between mb-3">
				<div class="d-flex align-items-center gap-2">
					<button type="button" class="btn btn-xs btn-secondary payrun-select-all">
						${__("Select All")}
					</button>
					<button type="button" class="btn btn-xs btn-secondary payrun-deselect-all">
						${__("Deselect All")}
					</button>
				</div>
				<strong class="payrun-selection-summary" aria-live="polite"></strong>
			</div>
			<div class="table-responsive">
				<table class="table table-bordered">
					<thead>
						<tr>
							<th style="width: 48px;">${__("Select")}</th>
							<th>${__("Employee")}</th>
							<th>${__("Employee Name")}</th>
							<th>${__("Department")}</th>
							<th>${__("Designation")}</th>
							<th>${__("Withheld")}</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`;
	}

	function bind_employee_table_events(dialog) {
		const $wrapper = dialog.get_field("employee_html").$wrapper;
		const update_summary = () => {
			const total = $wrapper.find(".payrun-employee-select").length;
			const selected = $wrapper.find(".payrun-employee-select:checked").length;
			$wrapper.find(".payrun-selection-summary").text(
				__("{0} of {1} employees selected", [selected, total]),
			);
		};

		$wrapper.on("click", ".payrun-select-all", () => {
			$wrapper.find(".payrun-employee-select").prop("checked", true);
			update_summary();
		});
		$wrapper.on("click", ".payrun-deselect-all", () => {
			$wrapper.find(".payrun-employee-select").prop("checked", false);
			update_summary();
		});
		$wrapper.on("change", ".payrun-employee-select", update_summary);
		update_summary();
	}

	function get_selected_employees(dialog) {
		return dialog
			.get_field("employee_html")
			.$wrapper.find(".payrun-employee-select:checked")
			.map((_, el) => $(el).attr("data-employee"))
			.get();
	}

	function create_payrun(state, selected_employee_ids) {
		const employees = state.employees
			.filter((employee) => selected_employee_ids.includes(employee.employee))
			.map((employee) => ({
				doctype: "Payroll Employee Detail",
				employee: employee.employee,
				employee_name: employee.employee_name,
				department: employee.department,
				designation: employee.designation,
				is_salary_withheld: employee.is_salary_withheld ? 1 : 0,
			}));

		const doc = {
			doctype: "Payroll Entry",
			company: state.scope.company,
			posting_date: state.scope.posting_date,
			salary_slip_based_on_timesheet: state.scope.salary_slip_based_on_timesheet ? 1 : 0,
			payroll_frequency: state.scope.payroll_frequency,
			start_date: state.scope.start_date,
			end_date: state.scope.end_date,
			branch: state.scope.branch,
			department: state.scope.department,
			designation: state.scope.designation,
			grade: state.scope.grade,
			currency: state.scope.currency,
			payroll_payable_account: state.scope.payroll_payable_account,
			employees,
		};

		frappe.call({
			method: "frappe.client.insert",
			args: {
				doc,
			},
			freeze: true,
			freeze_message: __("Creating Payrun..."),
		}).then((r) => {
			if (r.message?.name) {
				frappe.set_route("Form", "Payroll Entry", r.message.name);
			}
		});
	}
}
