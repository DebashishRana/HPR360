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
		</div>
	`);
}

function render_payrun(page, data) {
	const entry = data.payroll_entry;
	const counts = data.counts;
	const warnings = data.warnings || {};
	const status = entry.status || __("Draft");
	const status_class = {
		Draft: "red",
		Queued: "orange",
		Submitted: "green",
		Failed: "red",
		Cancelled: "red",
	}[status] || "blue";

	const missing_bank = warnings.missing_bank_details || [];
	const duplicates = warnings.duplicate_payslips || [];

	page.clear_inner_toolbar();
	page.main.html(`
		<div class="payrun-processing-header mb-4 d-flex justify-content-between align-items-start">
			<div>
				<h2 class="mb-1">${frappe.utils.escape_html(entry.name)}</h2>
				<div class="text-muted">
					${frappe.utils.escape_html(entry.company || "")}
					· ${frappe.utils.escape_html(entry.start_date || "")} → ${frappe.utils.escape_html(entry.end_date || "")}
					${entry.salary_structure ? ` · ${frappe.utils.escape_html(entry.salary_structure)}` : ""}
				</div>
			</div>
			<span class="indicator-pill ${status_class}">${frappe.utils.escape_html(status)}</span>
		</div>
		<div class="row">
			${render_stat(__("Employees"), counts.employees)}
			${render_stat(__("Payslips"), counts.salary_slips)}
			${render_stat(__("Validated"), counts.submitted_salary_slips)}
			${render_stat(__("Paid / Bank"), counts.bank_entries)}
		</div>
		${render_warnings(missing_bank, duplicates)}
		<div class="card mt-4">
			<div class="card-body">
				<h4>${__("Processing Checklist")}</h4>
				${render_check("Employees selected", counts.employees > 0)}
				${render_check("Payslips computed", counts.salary_slips >= counts.employees && counts.employees > 0)}
				${render_check("Payslips validated", counts.submitted_salary_slips >= counts.employees && counts.employees > 0)}
				${render_check("Marked paid", counts.bank_entries > 0)}
				${entry.error_message ? `<div class="alert alert-danger mt-3">${frappe.utils.escape_html(entry.error_message)}</div>` : ""}
			</div>
		</div>
		${render_slip_table(data.salary_slips || [])}
	`);

	page.add_inner_button(__("Open Payrun"), () => {
		frappe.set_route("Form", "Payroll Entry", entry.name);
	}).addClass("btn-secondary");

	if (!entry.salary_slips_created && entry.docstatus !== 2) {
		page.add_inner_button(__("Compute"), () => compute_salary_slips(page, entry));
	}
	if (entry.salary_slips_created && !entry.salary_slips_submitted && entry.docstatus !== 2) {
		page.add_inner_button(__("Validate"), () => {
			frappe.confirm(
				__("Submit payslips and create the accrual journal entry?"),
				() => run_doc_method(page, entry, "submit_salary_slips"),
			);
		});
	}
	if (entry.salary_slips_submitted && !counts.bank_entries && entry.docstatus !== 2) {
		page.add_inner_button(__("Mark Paid"), () => make_bank_entry(page, entry));
	}
	if (counts.submitted_salary_slips > 0 && entry.docstatus !== 2) {
		page.add_inner_button(__("Send Payslips"), () => send_payslips(page, entry));
	}
}

function render_warnings(missing_bank, duplicates) {
	if (!missing_bank.length && !duplicates.length) {
		return `<div class="alert alert-success mt-3">${__("No payroll warnings detected.")}</div>`;
	}
	let html = `<div class="alert alert-warning mt-3"><strong>${__("Warnings before finalization")}</strong><ul class="mb-0 mt-2">`;
	if (missing_bank.length) {
		html += `<li>${__("Missing bank details")}: ${frappe.utils.escape_html(missing_bank.slice(0, 8).join(", "))}${missing_bank.length > 8 ? "…" : ""}</li>`;
	}
	if (duplicates.length) {
		html += `<li>${__("Duplicate payslips")}: ${frappe.utils.escape_html(duplicates.map((d) => d.employee).join(", "))}</li>`;
	}
	html += `</ul></div>`;
	return html;
}

function render_slip_table(slips) {
	if (!slips.length) return "";
	const rows = slips
		.map(
			(s) => `<tr>
			<td><a href="/app/salary-slip/${encodeURIComponent(s.name)}">${frappe.utils.escape_html(s.name)}</a></td>
			<td>${frappe.utils.escape_html(s.employee_name || s.employee || "")}</td>
			<td>${s.docstatus === 1 ? __("Submitted") : s.docstatus === 2 ? __("Cancelled") : __("Draft")}</td>
			<td class="text-right">${frappe.format(s.net_pay || 0, { fieldtype: "Currency" })}</td>
		</tr>`
		)
		.join("");
	return `<div class="card mt-4"><div class="card-body">
		<h4>${__("Payslips")}</h4>
		<table class="table table-bordered"><thead><tr>
			<th>${__("Payslip")}</th><th>${__("Employee")}</th><th>${__("Status")}</th><th>${__("Net")}</th>
		</tr></thead><tbody>${rows}</tbody></table>
	</div></div>`;
}

function render_stat(label, value) {
	return `<div class="col-sm-3 mb-3"><div class="card"><div class="card-body"><div class="text-muted">${label}</div><div class="h2 mb-0">${Number(value) || 0}</div></div></div></div>`;
}

function render_check(label, complete) {
	return `<div class="d-flex align-items-center py-2"><span class="indicator ${complete ? "green" : "orange"} mr-2"></span>${__(label)}</div>`;
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
			freeze_message: __("Computing payslips..."),
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
	frappe.confirm(__("Email all submitted payslips for this payrun?"), () => {
		frappe.call({
			method: "hrms.payroll.doctype.payroll_entry.payroll_entry.send_payrun_payslips",
			args: { payroll_entry: entry.name },
			freeze: true,
			freeze_message: __("Sending payslips..."),
		}).then((r) => {
			frappe.show_alert({
				message: __("Sent {0} of {1} payslips", [r.message.sent, r.message.total]),
				indicator: "green",
			});
		});
	});
}
