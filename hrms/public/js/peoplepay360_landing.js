(function () {
	const landing_route = "/desk/peoplepay360";
	const launcher_routes = new Set(["/apps", "/app", "/app/", "/desk", "/desk/"]);

	function redirect_to_peoplepay360() {
		if (launcher_routes.has(window.location.pathname)) {
			window.location.replace(landing_route);
			return true;
		}
		return false;
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

	if (redirect_to_peoplepay360()) return;

	// Keep the launcher clean if the route was rendered before this script ran.
	if (window.location.pathname === "/apps") {
		if (!document.body) return;
		hide_legacy_app_tiles();
		new MutationObserver(hide_legacy_app_tiles).observe(document.body, {
			childList: true,
			subtree: true,
		});
	}
})();
