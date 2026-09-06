frappe.pages["pp-assistant"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("PeoplePay360 Assistant"),
		single_column: true,
	});
	wrapper.page = page;
	$(wrapper).find(".layout-main-section").html('<div class="pp-assistant-page"></div>');
	hrms.peoplepay360.mount_assistant($(wrapper).find(".pp-assistant-page")[0], { embedded: true });
};
