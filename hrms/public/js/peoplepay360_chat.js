/* PeoplePay360 Assistant — floating widget + embedded page */

frappe.provide("hrms.peoplepay360");

hrms.peoplepay360.assistant = {
	history: [],
	open: false,
	boot: null,
};

hrms.peoplepay360.can_use_assistant = function () {
	const caps = hrms.peoplepay360.capabilities || frappe.boot.peoplepay360 || {};
	if (caps.can_use_assistant === true) return true;
	if (caps.can_use_assistant === false) return false;
	return !!(
		caps.can_manage_employees ||
		caps.can_view_payroll ||
		caps.is_admin ||
		caps.is_employee_only
	);
};

hrms.peoplepay360.mount_assistant = function (root, opts) {
	opts = opts || {};
	const $root = $(root);
	$root.html(`
		<div class="pp-asst-shell ${opts.embedded ? "pp-asst-embedded" : ""}">
			<div class="pp-asst-header">
				<div>
					<div class="pp-asst-title">PeoplePay360 Assistant</div>
					<div class="pp-asst-sub">Live HR &amp; Payroll context</div>
				</div>
			</div>
			<div class="pp-asst-suggestions"></div>
			<div class="pp-asst-messages"></div>
			<form class="pp-asst-composer">
				<textarea rows="2" placeholder="Ask about headcount, leave, attendance, contracts, payroll…"></textarea>
				<button type="submit" class="pp-asst-send">Ask</button>
			</form>
		</div>
	`);

	const $msgs = $root.find(".pp-asst-messages");
	const $sugs = $root.find(".pp-asst-suggestions");
	const $form = $root.find(".pp-asst-composer");
	const $input = $form.find("textarea");

	function add_msg(role, html, meta) {
		const $m = $(`<div class="pp-asst-msg pp-asst-${role}"></div>`);
		if (role === "assistant") {
			const body = frappe.markdown ? frappe.markdown(html || "") : frappe.utils.escape_html(html || "").replace(/\n/g, "<br>");
			$m.html(`<div class="pp-asst-bubble">${body}</div>`);
			if (meta && meta.sources && meta.sources.length) {
				$m.append(
					`<div class="pp-asst-sources">Sources: ${frappe.utils.escape_html(meta.sources.join(", "))}</div>`
				);
			}
			if (meta && meta.mode) {
				$m.append(`<div class="pp-asst-mode">${frappe.utils.escape_html(meta.mode)}</div>`);
			}
		} else {
			$m.html(`<div class="pp-asst-bubble">${frappe.utils.escape_html(html || "")}</div>`);
		}
		$msgs.append($m);
		$msgs.scrollTop($msgs.prop("scrollHeight"));
	}

	function render_suggestions(list) {
		$sugs.empty();
		(list || []).forEach((s) => {
			const $b = $(`<button type="button" class="pp-asst-chip"></button>`).text(s);
			$b.on("click", () => {
				$input.val(s);
				$form.trigger("submit");
			});
			$sugs.append($b);
		});
	}

	function ask(text) {
		if (!text) return;
		add_msg("user", text);
		hrms.peoplepay360.assistant.history.push({ role: "user", content: text });
		const $thinking = $(`<div class="pp-asst-msg pp-asst-assistant"><div class="pp-asst-bubble pp-asst-thinking">Thinking with live PeoplePay360 data…</div></div>`);
		$msgs.append($thinking);
		$msgs.scrollTop($msgs.prop("scrollHeight"));

		frappe.call({
			method: "hrms.peoplepay360.chatbot.api.ask_assistant",
			args: {
				message: text,
				history: JSON.stringify(hrms.peoplepay360.assistant.history.slice(-10)),
			},
			callback(r) {
				$thinking.remove();
				const data = r.message || {};
				const ans = data.answer || "I could not build an answer from current data.";
				add_msg("assistant", ans, data);
				hrms.peoplepay360.assistant.history.push({ role: "assistant", content: ans });
				if (data.suggestions) render_suggestions(data.suggestions);
			},
			error() {
				$thinking.remove();
				add_msg("assistant", "Something went wrong contacting the assistant.");
			},
		});
	}

	$form.on("submit", (e) => {
		e.preventDefault();
		const text = ($input.val() || "").trim();
		$input.val("");
		ask(text);
	});

	$input.on("keydown", (e) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			$form.trigger("submit");
		}
	});

	frappe.call({
		method: "hrms.peoplepay360.chatbot.api.get_assistant_bootstrap",
		callback(r) {
			const boot = r.message || {};
			hrms.peoplepay360.assistant.boot = boot;
			add_msg("assistant", boot.welcome || "How can I help?");
			render_suggestions(boot.suggestions || []);
		},
	});
};

hrms.peoplepay360.ensure_assistant_launcher = function () {
	if (!hrms.peoplepay360.can_use_assistant()) return;
	if (document.getElementById("pp-asst-launcher")) return;

	const $launcher = $(`
		<button type="button" id="pp-asst-launcher" class="pp-asst-launcher" title="PeoplePay360 Assistant">
			<span>PP</span>
			<em>Ask</em>
		</button>
	`);
	const $panel = $(`
		<div id="pp-asst-panel" class="pp-asst-panel" style="display:none">
			<button type="button" class="pp-asst-close" aria-label="Close">×</button>
			<div class="pp-asst-panel-body"></div>
		</div>
	`);
	$("body").append($launcher).append($panel);

	const body = $panel.find(".pp-asst-panel-body")[0];
	hrms.peoplepay360.mount_assistant(body, { embedded: false });

	$launcher.on("click", () => {
		hrms.peoplepay360.assistant.open = !hrms.peoplepay360.assistant.open;
		$panel.toggle(hrms.peoplepay360.assistant.open);
	});
	$panel.find(".pp-asst-close").on("click", () => {
		hrms.peoplepay360.assistant.open = false;
		$panel.hide();
	});
};

$(document).on("app_ready", function () {
	const boot = () => {
		if (!hrms.peoplepay360.capabilities) {
			hrms.peoplepay360.load_capabilities().then(() => hrms.peoplepay360.ensure_assistant_launcher());
		} else {
			hrms.peoplepay360.ensure_assistant_launcher();
		}
	};
	setTimeout(boot, 400);
});
