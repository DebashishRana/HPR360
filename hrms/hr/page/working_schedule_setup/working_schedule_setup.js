const WORKING_SCHEDULE_DAYS = [
	"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
];

frappe.pages["working-schedule-setup"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Working Schedule Setup"),
		single_column: true,
	});

	page.set_primary_action(__("New Schedule"), () => open_schedule_dialog(page));
	$(wrapper).on("show", () => load_schedules(page));
};

function load_schedules(page) {
	frappe.db.get_list("Working Schedule", {
		fields: ["name", "schedule_name", "schedule_type", "company", "is_active", "weekly_hours", "modified"],
		order_by: "modified desc",
		limit_page_length: 100,
	}).then((schedules) => render_schedules(page, schedules));
}

function render_schedules(page, schedules) {
	if (!schedules.length) {
		page.main.html(`
			<div class="text-center text-muted" style="padding: 100px 20px;">
				<h3>${__("No working schedules yet")}</h3>
				<p>${__("Create a schedule with working days, hours, and breaks. Weekly hours are calculated automatically.")}</p>
				<button class="btn btn-primary create-working-schedule">${__("Create Schedule")}</button>
			</div>
		`);
		page.main.find(".create-working-schedule").on("click", () => open_schedule_dialog(page));
		return;
	}

	page.main.html(`
		<div class="mb-4">
			<h3>${__("Working Schedules")}</h3>
			<p class="text-muted">${__("Name, type, and weekly hours for attendance and payroll expectations.")}</p>
		</div>
		<div class="row schedule-list"></div>
	`);

	const $list = page.main.find(".schedule-list");
	schedules.forEach((schedule) => {
		const status = schedule.is_active ? __("Active") : __("Inactive");
		$list.append(`
			<div class="col-md-6 col-lg-4 mb-3">
				<div class="card h-100 working-schedule-card" data-name="${frappe.utils.escape_html(schedule.name)}" style="cursor: pointer;">
					<div class="card-body">
						<div class="d-flex justify-content-between align-items-start">
							<h4 class="mb-2">${frappe.utils.escape_html(schedule.schedule_name || schedule.name)}</h4>
							<span class="indicator-pill ${schedule.is_active ? "green" : "gray"}">${status}</span>
						</div>
						<div class="text-muted">${frappe.utils.escape_html(schedule.schedule_type || __("Standard"))}</div>
						<div class="mt-2"><strong>${Number(schedule.weekly_hours || 0).toFixed(1)}</strong> ${__("hrs / week")}</div>
						<div class="text-muted mt-1">${frappe.utils.escape_html(schedule.company || __("All companies"))}</div>
					</div>
				</div>
			</div>
		`);
	});
	$list.find(".working-schedule-card").on("click", function () {
		open_schedule_dialog(page, $(this).attr("data-name"));
	});
}

function open_schedule_dialog(page, schedule_name) {
	const dialog = new frappe.ui.Dialog({
		title: schedule_name ? __("Edit Working Schedule") : __("New Working Schedule"),
		size: "extra-large",
		fields: [
			{fieldname: "schedule_name", fieldtype: "Data", label: __("Schedule Name"), reqd: 1, read_only: Boolean(schedule_name)},
			{fieldname: "schedule_type", fieldtype: "Select", label: __("Type"), options: "Standard\nFlexible\nPart-time\nShift", default: "Standard"},
			{fieldname: "company", fieldtype: "Link", label: __("Company"), options: "Company"},
			{fieldname: "is_active", fieldtype: "Check", label: __("Active"), default: 1},
			{fieldname: "weekly_hours", fieldtype: "Float", label: __("Weekly Hours (auto)"), read_only: 1},
			{fieldname: "description", fieldtype: "Small Text", label: __("Description")},
			{fieldname: "working_days_html", fieldtype: "HTML"},
		],
		primary_action_label: __("Save Schedule"),
		primary_action(values) {
			const working_days = read_working_days(dialog);
			if (!working_days.length) {
				frappe.msgprint(__("Select at least one working day."));
				return;
			}

			const doc = {
				doctype: "Working Schedule",
				schedule_name: values.schedule_name,
				schedule_type: values.schedule_type,
				company: values.company,
				is_active: values.is_active ? 1 : 0,
				description: values.description,
				working_days,
			};
			if (schedule_name) doc.name = schedule_name;

			frappe.call({
				method: schedule_name ? "frappe.client.save" : "frappe.client.insert",
				args: { doc },
				freeze: true,
				freeze_message: __("Saving working schedule..."),
			}).then(() => {
				dialog.hide();
				load_schedules(page);
			});
		},
	});

	dialog.get_field("working_days_html").$wrapper.html(render_working_days());
	if (schedule_name) {
		frappe.db.get_doc("Working Schedule", schedule_name).then((doc) => {
			dialog.set_values({
				schedule_name: doc.schedule_name,
				schedule_type: doc.schedule_type,
				company: doc.company,
				is_active: doc.is_active,
				weekly_hours: doc.weekly_hours,
				description: doc.description,
			});
			set_working_days(dialog, doc.working_days || []);
		});
	}
	dialog.show();
}

function render_working_days() {
	return `
		<div class="form-group">
			<label class="control-label">${__("Working Days")}</label>
			<div class="table-responsive"><table class="table table-bordered working-days-table">
				<thead><tr><th>${__("Working")}</th><th>${__("Day")}</th><th>${__("Start")}</th><th>${__("End")}</th><th>${__("Break (minutes)")}</th></tr></thead>
				<tbody>${WORKING_SCHEDULE_DAYS.map((day) => `
					<tr data-day="${day}">
						<td><input type="checkbox" class="schedule-day-enabled" checked></td><td>${day}</td>
						<td><input type="time" class="form-control schedule-start" value="09:00"></td>
						<td><input type="time" class="form-control schedule-end" value="17:00"></td>
						<td><input type="number" min="0" class="form-control schedule-break" value="60"></td>
					</tr>`).join("")}</tbody>
			</table></div>
		</div>
	`;
}

function read_working_days(dialog) {
	return dialog.get_field("working_days_html").$wrapper.find("tbody tr").map((_, row) => {
		const $row = $(row);
		if (!$row.find(".schedule-day-enabled").prop("checked")) return null;
		return {
			doctype: "Working Schedule Day",
			name: $row.attr("data-row-name") || undefined,
			day: $row.attr("data-day"),
			is_working_day: 1,
			start_time: $row.find(".schedule-start").val(),
			end_time: $row.find(".schedule-end").val(),
			break_minutes: Number($row.find(".schedule-break").val()) || 0,
		};
	}).get();
}

function set_working_days(dialog, working_days) {
	const by_day = Object.fromEntries(working_days.map((row) => [row.day, row]));
	dialog.get_field("working_days_html").$wrapper.find("tbody tr").each((_, row) => {
		const $row = $(row);
		const data = by_day[$row.attr("data-day")];
		if (!data) {
			$row.find(".schedule-day-enabled").prop("checked", false);
			return;
		}
		$row.find(".schedule-day-enabled").prop("checked", Boolean(data.is_working_day));
		$row.attr("data-row-name", data.name || "");
		$row.find(".schedule-start").val(data.start_time || "09:00");
		$row.find(".schedule-end").val(data.end_time || "17:00");
		$row.find(".schedule-break").val(data.break_minutes || 0);
	});
}
