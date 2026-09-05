frappe.pages["payroll-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Payroll Dashboard"),
		single_column: true,
	});

	page.main.addClass("payroll-dashboard-page");
	page.add_field({
		fieldname: "company",
		fieldtype: "Link",
		label: __("Company"),
		options: "Company",
	});
	page.add_field({
		fieldname: "from_date",
		fieldtype: "Date",
		label: __("From Date"),
		default: frappe.datetime.month_start(),
	});
	page.add_field({
		fieldname: "to_date",
		fieldtype: "Date",
		label: __("To Date"),
		default: frappe.datetime.month_end(),
	});
	page.set_primary_action(__("Refresh"), () => load_dashboard(page));
	page.add_inner_button(__("New Payrun"), () => frappe.set_route("List", "Payroll Entry"));
	page.add_inner_button(__("Payrun Processing"), () => frappe.set_route("payrun-processing"));

	$(wrapper).on("show", () => load_dashboard(page));
};

function load_dashboard(page) {
	const from_date = page.fields_dict.from_date.get_value();
	const to_date = page.fields_dict.to_date.get_value();
	if (!from_date || !to_date) return;

	frappe.call({
		method: "hrms.payroll.page.payroll_dashboard.payroll_dashboard.get_payroll_dashboard_data",
		args: {
			from_date,
			to_date,
			company: page.fields_dict.company.get_value(),
		},
		freeze: true,
		freeze_message: __("Refreshing payroll dashboard..."),
	}).then((r) => {
		if (r.message) render_dashboard(page, r.message);
	});
}

function render_dashboard(page, data) {
	const kpis = data.kpis || {};
	const warnings = data.warnings || {};
	const currency = data.currency || "";
	const total_warnings = Object.values(warnings).reduce((total, value) => total + Number(value || 0), 0);

	page.clear_inner_toolbar();
	page.set_primary_action(__("Refresh"), () => load_dashboard(page));
	page.add_inner_button(__("New Payrun"), () => frappe.set_route("List", "Payroll Entry"));
	page.add_inner_button(__("Payrun Processing"), () => frappe.set_route("payrun-processing"));
	page.main.html(`
		<div class="payroll-dashboard-shell">
			<header class="payroll-dashboard-header">
				<div>
					<div class="payroll-dashboard-eyebrow">${__("PeoplePay360 Payroll")}</div>
					<h1 class="payroll-dashboard-title">${__("Payroll overview")}</h1>
					<p class="payroll-dashboard-subtitle">${__("A clear view of payroll cost, payrun progress, and operational readiness.")}</p>
				</div>
				<div class="payroll-dashboard-filter-note">${__("Period-filtered operational view")}</div>
			</header>

			<section class="payroll-dashboard-kpis">
				${render_kpi(__("Net salary paid"), format_money(kpis.total_net_salary, currency), "teal")}
				${render_kpi(__("Payslips generated"), kpis.payslips_generated, "navy")}
				${render_kpi(__("Average salary"), format_money(kpis.average_salary, currency), "navy")}
				${render_kpi(__("Approved time off"), kpis.approved_time_off, "amber")}
				${render_kpi(__("Attendance health"), `${Number(kpis.attendance_health || 0).toFixed(1)}%`, "teal")}
			</section>

			<section class="payroll-dashboard-grid">
				<div class="payroll-dashboard-card">
					<h4>${__("Salary cost trend")}</h4>
					<div class="payroll-dashboard-card-caption">${__("Net salary across the selected period")}</div>
					${render_trend(data.trend || [], currency)}
				</div>
				<div class="payroll-dashboard-card">
					<h4>${__("Payrun status")}</h4>
					<div class="payroll-dashboard-card-caption">${__("Batches requiring attention")}</div>
					${render_status(data.status_breakdown || {})}
				</div>
			</section>

			<section class="payroll-dashboard-card mt-4">
				<div class="d-flex justify-content-between align-items-start">
					<div><h4>${__("Operational alerts")}</h4><div class="payroll-dashboard-card-caption">${__("Resolve these items before finalizing payroll")}</div></div>
					<span class="payroll-dashboard-pill">${total_warnings} ${__("open")}</span>
				</div>
				${render_warning(__("Queued payruns"), warnings.queued_payruns, "payrun-processing")}
				${render_warning(__("Failed payruns"), warnings.failed_payruns, "Payroll Entry")}
				${render_warning(__("Unmarked attendance"), warnings.unmarked_attendance, "Attendance")}
			</section>
		</div>
	`);
	page.main.find("[data-route]").on("click", function (event) {
		event.preventDefault();
		const route = $(this).attr("data-route");
		if (route === "payrun-processing") {
			frappe.set_route(route);
		} else {
			frappe.set_route("List", route);
		}
	});
}

function render_kpi(label, value, accent) {
	return `<div class="payroll-dashboard-card payroll-dashboard-kpi payroll-dashboard-kpi-${accent}"><div class="payroll-dashboard-kpi-label">${label}</div><div class="payroll-dashboard-kpi-value">${value}</div></div>`;
}

function render_trend(trend, currency) {
	if (!trend.length) return `<div class="text-muted text-center p-5">${__("No posted salary slips for this period")}</div>`;
	const max = Math.max(...trend.map((row) => Number(row.value) || 0), 1);
	return `<div class="payroll-dashboard-chart">${trend.map((row) => `
		<div class="payroll-dashboard-bar-wrap" title="${format_money(row.value, currency)}">
			<div class="payroll-dashboard-bar" style="height: ${Math.max((Number(row.value) / max) * 100, 3)}%"></div>
			<div class="payroll-dashboard-bar-label">${frappe.utils.escape_html(row.month.slice(5))}</div>
		</div>`).join("")}</div>`;
}

function render_status(statuses) {
	const rows = Object.entries(statuses);
	if (!rows.length) return `<div class="text-muted p-3">${__("No payruns in this period")}</div>`;
	return rows.map(([status, count]) => `<div class="payroll-dashboard-status-row"><span>${frappe.utils.escape_html(status)}</span><span class="payroll-dashboard-pill">${Number(count) || 0}</span></div>`).join("");
}

function render_warning(label, count, route) {
	const value = Number(count) || 0;
	return `<div class="payroll-dashboard-warning-row"><span>${label}</span>${value ? `<a href="#" data-route="${route}">${value} ${__("review")}</a>` : `<span class="text-muted">${__("Clear")}</span>`}</div>`;
}

function format_money(value, currency) {
	const formatted = Number(value || 0).toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0});
	return currency ? `${frappe.utils.escape_html(currency)} ${formatted}` : formatted;
}
