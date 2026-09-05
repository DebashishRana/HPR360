frappe.pages["payrun-wizard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Payrun Wizard"), single_column: true });
	page.main.addClass("payrun-wizard-page");
	const state = { step: 1, filters: {}, employees: [], warnings: [], selected: new Set(), options: {} };

	page.set_primary_action(__("Continue"), () => state.step === 1 ? continue_to_employees() : create_payrun());
	page.add_inner_button(__("Cancel"), () => frappe.set_route("payroll-dashboard"));
	page.add_inner_button(__("Refresh"), () => state.step === 1 ? load_options() : load_employees());

	function load_options() {
		frappe.call({
			method: "hrms.payroll.page.payrun_wizard.payrun_wizard.get_payrun_scope_options",
			freeze: true, freeze_message: __("Loading payroll options...")
		}).then((r) => { state.options = r.message || {}; render_scope(); }).catch(() => render_error(__("Unable to load payroll options.")));
	}

	function render_scope() {
		page.set_primary_action(__("Continue"), continue_to_employees);
		page.main.html(`<div class="payrun-step active">${__("1. Scope")} <span class="text-muted"> -> 2. Employees -> 3. Created</span></div>
			<div class="card mt-4"><div class="card-body"><div class="row">
			${field("company", __("Company"), "select", state.options.companies || [], true)}
			${field("payroll_frequency", __("Payroll Frequency"), "select", state.options.payroll_frequencies || [], true)}
			${field("start_date", __("From Date"), "date", [], true)}${field("end_date", __("To Date"), "date", [], true)}
			${field("salary_structure", __("Salary Structure"), "select", state.options.salary_structures || [])}
			${field("payroll_payable_account", __("Payroll Payable Account"), "select", state.options.payroll_payable_accounts || [])}
			${field("department", __("Department"), "select", state.options.departments || [])}
			${field("employee_type", __("Employee Type"), "select", state.options.employee_types || [])}
			${field("branch", __("Branch"), "select", state.options.branches || [])}
			${field("designation", __("Designation"), "select", state.options.designations || [])}
			${field("grade", __("Grade"), "select", state.options.grades || [])}
			<div class="col-sm-4 form-group"><label><input type="checkbox" id="validate_attendance"> ${__("Validate Attendance")}</label></div>
			</div></div></div>`);
		Object.entries(state.filters).forEach(([key, value]) => page.main.find(`#payrun-${key}`).val(value));
	}

	function field(name, label, type, options, required) {
		if (type === "date") {
			return `<div class="col-sm-4 form-group"><label>${escape_html(label)}${required ? " *" : ""}</label><input id="payrun-${name}" type="date" class="form-control" ${required ? "required" : ""}></div>`;
		}
		const list = options.map((option) => {
			const value = typeof option === "object" ? option.name : option;
			return `<option value="${escape_html(value)}">${escape_html(value)}</option>`;
		}).join("");
		return `<div class="col-sm-4 form-group"><label>${escape_html(label)}${required ? " *" : ""}</label><select id="payrun-${name}" class="form-control" ${required ? "required" : ""}><option value="">${__("Select")}</option>${list}</select></div>`;
	}

	function read_scope() {
		const filters = {};
		["company", "payroll_frequency", "start_date", "end_date", "salary_structure", "payroll_payable_account", "department", "employee_type", "branch", "designation", "grade"].forEach((key) => {
			const value = page.main.find(`#payrun-${key}`).val(); if (value) filters[key] = value;
		});
		filters.validate_attendance = page.main.find("#validate_attendance").is(":checked") ? 1 : 0;
		filters.salary_slip_based_on_timesheet = 0;
		return filters;
	}

	function continue_to_employees() {
		state.filters = read_scope();
		if (!state.filters.company || !state.filters.start_date || !state.filters.end_date) return frappe.msgprint(__("Company, From Date, and To Date are required."));
		if (state.filters.start_date > state.filters.end_date) return frappe.msgprint(__("From Date cannot be after To Date."));
		if (!state.filters.payroll_frequency) return frappe.msgprint(__("Payroll Frequency is required."));
		load_employees();
	}

	function load_employees() {
		frappe.call({ method: "hrms.payroll.page.payrun_wizard.payrun_wizard.get_eligible_employees", args: { filters: state.filters }, freeze: true, freeze_message: __("Checking payroll eligibility...") })
			.then((r) => { const data = r.message || {}; state.employees = data.employees || []; state.warnings = data.warnings || []; state.selected = new Set(state.employees.filter((e) => e.eligibility_status !== "Blocked").map((e) => e.employee)); state.step = 2; render_employees(data.summary || {}); })
			.catch(() => render_error(__("Unable to check employee eligibility.")));
	}

	function render_employees(summary) {
		page.set_primary_action(__("Create Payrun"), create_payrun);
		const cards = [[__("Total"), summary.total], [__("Eligible"), summary.eligible], [__("Review"), summary.review], [__("Blocked"), summary.blocked], [__("Selected"), state.selected.size]];
		const rows = state.employees.map((employee) => `<tr><td><input type="checkbox" class="payrun-select" data-id="${escape_html(employee.employee)}" ${state.selected.has(employee.employee) ? "checked" : ""} ${employee.eligibility_status === "Blocked" ? "disabled" : ""}></td><td>${escape_html(employee.employee)}</td><td>${escape_html(employee.employee_name)}</td><td>${escape_html(employee.employee_type)}</td><td>${escape_html(employee.department)}</td><td>${escape_html(employee.designation)}</td><td>${escape_html(employee.salary_structure)}</td><td>${escape_html(employee.salary_structure_assignment)}</td><td>${escape_html(employee.assignment_effective_date)}</td><td>${Number(employee.base_salary) || 0}</td><td>${Number(employee.variable_salary) || 0}</td><td>${escape_html(employee.attendance_status)}</td><td>${escape_html(employee.bank_details_status)}</td><td>${escape_html(employee.email_status)}</td><td><span class="indicator-pill ${employee.eligibility_status === "Blocked" ? "red" : employee.eligibility_status === "Review" ? "orange" : "green"}">${escape_html(employee.eligibility_status)}</span></td><td>${Number(employee.warning_count) || 0}</td></tr>`).join("");
		page.main.html(`<div class="payrun-step active">1. ${__("Scope")} <span class="text-muted"> -> 2. ${__("Employees")} -> 3. ${__("Created")}</span></div><div class="row payrun-summary mt-4">${cards.map((c) => `<div class="col-sm-2"><div class="card"><div class="card-body"><div class="text-muted">${c[0]}</div><h3>${Number(c[1]) || 0}</h3></div></div></div>`).join("")}</div><div class="card mt-4"><div class="card-body"><div class="mb-3"><button class="btn btn-secondary btn-sm" id="payrun-select-all">${__("Select All Eligible")}</button> <button class="btn btn-secondary btn-sm" id="payrun-clear">${__("Clear Selection")}</button> <button class="btn btn-secondary btn-sm" id="payrun-back">${__("Back")}</button></div><div class="table-responsive"><table class="table table-bordered payrun-table"><thead><tr><th></th><th>${__("Employee ID")}</th><th>${__("Name")}</th><th>${__("Type")}</th><th>${__("Department")}</th><th>${__("Designation")}</th><th>${__("Salary Structure")}</th><th>${__("Assignment")}</th><th>${__("Effective")}</th><th>${__("Base")}</th><th>${__("Variable")}</th><th>${__("Attendance")}</th><th>${__("Bank")}</th><th>${__("Email")}</th><th>${__("Status")}</th><th>${__("Warnings")}</th></tr></thead><tbody>${rows || `<tr><td colspan="16" class="text-center text-muted">${__("No employees found")}</td></tr>`}</tbody></table></div></div></div>`);
		page.main.find(".payrun-select").on("change", function () { this.checked ? state.selected.add(this.dataset.id) : state.selected.delete(this.dataset.id); });
		page.main.find("#payrun-select-all").on("click", () => { state.selected = new Set(state.employees.filter((e) => e.eligibility_status !== "Blocked").map((e) => e.employee)); render_employees(summary); });
		page.main.find("#payrun-clear").on("click", () => { state.selected.clear(); render_employees(summary); });
		page.main.find("#payrun-back").on("click", () => { state.step = 1; render_scope(); });
	}

	function create_payrun() {
		if (!state.selected.size) return frappe.msgprint(__("Select at least one eligible employee."));
		frappe.call({ method: "hrms.payroll.page.payrun_wizard.payrun_wizard.create_payrun", args: { filters: state.filters, selected_employees: JSON.stringify([...state.selected]) }, freeze: true, freeze_message: __("Creating payrun...") })
			.then((r) => { const result = r.message; if (result?.route) frappe.set_route(result.route); }).catch(() => frappe.msgprint(__("Payrun creation failed. Refresh the employee list and try again.")));
	}

	function render_error(message) { page.main.html(`<div class="alert alert-danger mt-4">${escape_html(message)}</div>`); }
	function escape_html(value) { return frappe.utils.escape_html(String(value ?? "")); }
	load_options();
};
