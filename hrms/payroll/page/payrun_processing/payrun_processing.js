frappe.pages["payrun-processing"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Payrun Processing"),
		single_column: true,
	});

	page.add_field({
		fieldname: "payroll_entry",
		label: __("Payrun"),
		fieldtype: "Link",
		options: "Payroll Entry",
		change() {
			load_payrun(page, page.fields_dict.payroll_entry.get_value());
		},
	});
	page.set_primary_action(__("Refresh"), () => {
		load_payrun(page, page.fields_dict.payroll_entry.get_value());
	});

	$(wrapper).on("show", () => {
		const route = frappe.get_route();
		const payroll_entry = route[1] || frappe.route_options?.payroll_entry;
		if (payroll_entry) {
			page.fields_dict.payroll_entry.set_value(payroll_entry);
		} else {
			render_empty_state(page);
		}
	});
};

function load_payrun(page, payroll_entry) {
	if (!payroll_entry) {
		render_empty_state(page);
		return;
	}

	frappe.call({
		method: "hrms.payroll.doctype.payroll_entry.payroll_entry.get_payrun_processing_data",
		args: { payroll_entry },
		freeze: true,
		freeze_message: __("Loading payrun status..."),
	}).then((r) => {
		if (r.message) render_payrun(page, r.message);
	});
}

function render_empty_state(page) {
	page.main.html(`
		<div class="text-center text-muted" style="padding: 100px 20px;">
			<h3>${__("Select a payrun to begin processing")}</h3>
			<p>${__("Choose a Payroll Entry above to see its progress and available actions.")}</p>
			<button class="btn btn-primary mt-3" id="pp360-open-wizard">${__("Start Payrun Wizard")}</button>
		</div>
	`);
	page.main.find("#pp360-open-wizard").on("click", () => frappe.set_route("payrun-wizard"));
}

function render_payrun(page, data) {
	const entry = data.payroll_entry;
	const counts = data.counts;
	const slips = data.salary_slips || [];
	const warnings = data.warnings || [];
	const status = entry.status || __("Draft");
	const status_class = {
		Draft: "red",
		Queued: "orange",
		Submitted: "green",
		Failed: "red",
		Cancelled: "red",
	}[status] || "blue";

	page.clear_inner_toolbar();
	page.main.html(`
		<div class="payrun-processing-header mb-4 d-flex justify-content-between align-items-start">
			<div>
				<h2 class="mb-1">${frappe.utils.escape_html(entry.name)}</h2>
				<div class="text-muted">${frappe.utils.escape_html(entry.company || "")} · ${frappe.utils.escape_html(entry.start_date || "")} → ${frappe.utils.escape_html(entry.end_date || "")}</div>
				<div class="text-muted mt-1">${__("Structure filter / frequency")}: ${frappe.utils.escape_html(entry.payroll_frequency || __("Timesheet"))}</div>
			</div>
			<span class="indicator-pill ${status_class}">${frappe.utils.escape_html(status)}</span>
		</div>
		<div class="row">
			${render_stat(__("Employees"), counts.employees)}
			${render_stat(__("Salary Slips"), counts.salary_slips)}
			${render_stat(__("Submitted Slips"), counts.submitted_salary_slips)}
			${render_stat(__("Warnings"), counts.warnings || warnings.length)}
		</div>
		<div class="card mt-4">
			<div class="card-body">
				<h4>${__("Processing Checklist")}</h4>
				${render_check("Employees selected", counts.employees > 0)}
				${render_check("Salary slips computed", counts.salary_slips >= counts.employees && counts.employees > 0)}
				${render_check("Salary slips validated and submitted", counts.submitted_salary_slips >= counts.employees && counts.employees > 0)}
				${render_check("Payment entry created", counts.bank_entries > 0)}
				${entry.error_message ? `<div class="alert alert-danger mt-3">${frappe.utils.escape_html(entry.error_message)}</div>` : ""}
			</div>
		</div>
		${render_warnings(warnings)}
		${render_payslip_table(slips)}
	`);

	page.main.find("[data-slip]").on("click", function (e) {
		e.preventDefault();
		frappe.set_route("Form", "Salary Slip", $(this).data("slip"));
	});

	page.add_inner_button(__("Open Payroll Entry"), () => {
		frappe.set_route("Form", "Payroll Entry", entry.name);
	});

	if (!entry.salary_slips_created && entry.docstatus !== 2) {
		page.add_inner_button(__("Compute"), () => compute_salary_slips(page, entry));
	}
	if (entry.salary_slips_created && !entry.salary_slips_submitted && entry.docstatus !== 2) {
		page.add_inner_button(__("Validate"), () => {
			frappe.confirm(
				__("Submit salary slips and create the accrual journal entry?"),
				() => run_doc_method(page, entry, "submit_salary_slips"),
			);
		});
	}
	if (entry.salary_slips_submitted && !counts.bank_entries && entry.docstatus !== 2) {
		page.add_inner_button(__("Mark Paid"), () => make_bank_entry(page, entry));
	}
	if (entry.salary_slips_submitted && entry.docstatus !== 2) {
		page.add_inner_button(__("Send Payslips"), () => send_payslips(page, entry));
	}
}

function render_stat(label, value) {
	return `<div class="col-sm-3 mb-3"><div class="card"><div class="card-body"><div class="text-muted">${label}</div><div class="h2 mb-0">${Number(value) || 0}</div></div></div></div>`;
}

function render_check(label, complete) {
	return `<div class="d-flex align-items-center py-2"><span class="indicator ${complete ? "green" : "orange"} mr-2"></span>${__(label)}</div>`;
}

function render_warnings(warnings) {
	if (!warnings.length) {
		return `<div class="card mt-4"><div class="card-body"><h4>${__("Warnings")}</h4><div class="text-muted">${__("No payroll warnings for this batch.")}</div></div></div>`;
	}
	const rows = warnings
		.map(
			(w) =>
				`<div class="d-flex justify-content-between border-bottom py-2"><span><span class="indicator-pill ${w.severity === "Blocking" ? "red" : "orange"} mr-2">${frappe.utils.escape_html(w.severity || "Review")}</span>${frappe.utils.escape_html(w.message || "")}</span><code>${frappe.utils.escape_html(w.employee || "")}</code></div>`,
		)
		.join("");
	return `<div class="card mt-4"><div class="card-body"><h4>${__("Warnings")}</h4>${rows}</div></div>`;
}

function render_payslip_table(slips) {
	if (!slips.length) {
		return `<div class="card mt-4"><div class="card-body"><h4>${__("Payslips")}</h4><div class="text-muted">${__("No payslips generated yet. Use Compute to create them.")}</div></div></div>`;
	}
	const rows = slips
		.map((slip) => {
			const status = slip.docstatus === 1 ? __("Submitted") : slip.docstatus === 2 ? __("Cancelled") : __("Draft");
			return `<tr>
				<td><a href="#" data-slip="${frappe.utils.escape_html(slip.name)}">${frappe.utils.escape_html(slip.name)}</a></td>
				<td>${frappe.utils.escape_html(slip.employee_name || slip.employee)}</td>
				<td>${frappe.utils.escape_html(slip.salary_structure || "—")}</td>
				<td>${Number(slip.payment_days || 0)}</td>
				<td>${format_currency(slip.gross_pay || 0, slip.currency)}</td>
				<td>${format_currency(slip.total_deduction || 0, slip.currency)}</td>
				<td>${format_currency(slip.net_pay || 0, slip.currency)}</td>
				<td>${status}</td>
			</tr>`;
		})
		.join("");
	return `<div class="card mt-4"><div class="card-body"><h4>${__("Payslips")}</h4>
		<div class="table-responsive"><table class="table table-bordered">
			<thead><tr><th>${__("Payslip")}</th><th>${__("Employee")}</th><th>${__("Structure")}</th><th>${__("Days")}</th><th>${__("Gross")}</th><th>${__("Deductions")}</th><th>${__("Net")}</th><th>${__("Status")}</th></tr></thead>
			<tbody>${rows}</tbody>
		</table></div></div></div>`;
}

function run_doc_method(page, entry, method) {
	frappe.call({
		method: "run_doc_method",
		args: { method, dt: "Payroll Entry", dn: entry.name },
		freeze: true,
		freeze_message: __("Processing payrun..."),
	}).then(() => load_payrun(page, entry.name));
}

function compute_salary_slips(page, entry) {
	if (entry.docstatus === 0) {
		frappe.call({
			method: "frappe.client.submit",
			args: { doc: { doctype: "Payroll Entry", name: entry.name } },
			freeze: true,
			freeze_message: __("Computing salary slips..."),
		}).then(() => load_payrun(page, entry.name));
	} else {
		run_doc_method(page, entry, "create_salary_slips");
	}
}

function make_bank_entry(page, entry) {
	if (!entry.payment_account) {
		frappe.msgprint(__("Payment Account is mandatory. Set it on the Payroll Entry first."));
		return;
	}

	frappe.call({
		method: "run_doc_method",
		args: {
			method: "make_bank_entry",
			dt: "Payroll Entry",
			dn: entry.name,
			args: { for_withheld_salaries: 0 },
		},
		freeze: true,
		freeze_message: __("Creating payment entry..."),
	}).then(() => load_payrun(page, entry.name));
}

function send_payslips(page, entry) {
	frappe.confirm(__("Queue submitted payslips for email delivery?"), () => {
		frappe.call({
			method: "hrms.payroll.doctype.payroll_entry.payroll_entry.send_payrun_payslips",
			args: { payroll_entry: entry.name },
			freeze: true,
			freeze_message: __("Queueing payslips..."),
		}).then((r) => {
			if (r.message) frappe.msgprint(__("{0} payslips queued for delivery.", [r.message.queued]));
		});
	});
}
