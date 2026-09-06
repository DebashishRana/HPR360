(function () {
	function resolve_home() {
		// Single product home for every role — sidebar filters by capability
		return "/desk/peoplepay360";
	}

	function redirect_by_role() {
		const launcher = new Set(["/apps", "/app", "/app/", "/desk", "/desk/"]);
		if (!launcher.has(window.location.pathname)) return false;
		window.location.replace(resolve_home());
		return true;
	}

	function hide_legacy_app_tiles() {
		const legacy_apps = new Set(["ERPNext", "Frappe HR", "Framework"]);
		document.querySelectorAll("a, button, [role='button']").forEach((element) => {
			const label = (element.textContent || "").trim();
			if (legacy_apps.has(label)) {
				element.closest(".app-card, .desk-app-item, .onboarding-app-item")?.remove();
			}
		});
	}

	if (redirect_by_role()) return;

	if (window.location.pathname === "/apps") {
		if (!document.body) return;
		hide_legacy_app_tiles();
		new MutationObserver(hide_legacy_app_tiles).observe(document.body, {
			childList: true,
			subtree: true,
		});
	}
})();
