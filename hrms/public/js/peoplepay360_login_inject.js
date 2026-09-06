/**
 * Inject PeoplePay360 role picker into the stock Frappe /login page.
 * Choosing a role autofills email + password with demo passkeys.
 */
(function () {
	const PATH = (window.location.pathname || "").replace(/\/$/, "") || "/";
	if (PATH !== "/login" && PATH !== "") return;

	const ROLES = [
		{
			id: "employee",
			label: "Employee",
			description: "Own profile, attendance & time off",
			email: "alex.employee@example.com",
			password: "Emp@360!",
		},
		{
			id: "hr_manager",
			label: "HR Manager",
			description: "People, contracts, schedules, leave",
			email: "hr.manager@example.com",
			password: "HrMgr@360!",
		},
		{
			id: "payroll_user",
			label: "HR Payroll User",
			description: "HR + payruns & payslips",
			email: "payroll.user@example.com",
			password: "PayUser@360!",
		},
		{
			id: "payroll_manager",
			label: "HR Payroll Manager",
			description: "Full HR & payroll config",
			email: "payroll.manager@example.com",
			password: "PayMgr@360!",
		},
		{
			id: "admin",
			label: "Admin",
			description: "Full system administration",
			email: "admin.pp@example.com",
			password: "Admin@360!",
		},
	];

	function ensureStyles() {
		if (document.getElementById("pp-login-role-styles")) return;
		const style = document.createElement("style");
		style.id = "pp-login-role-styles";
		style.textContent = `
			.pp-role-wrap {
				margin: 0 0 1.1rem;
				padding: 0.85rem;
				border-radius: 1rem;
				border: 1px solid rgba(15, 118, 110, 0.18);
				background: linear-gradient(180deg, rgba(15,118,110,0.08), rgba(255,255,255,0.9));
				animation: ppRise .45s ease both;
			}
			.pp-role-wrap h3 {
				margin: 0 0 .15rem;
				font-size: .95rem;
				font-weight: 700;
				color: #0c1222;
			}
			.pp-role-wrap .pp-sub {
				margin: 0 0 .7rem;
				font-size: .75rem;
				color: #5b6b7c;
			}
			.pp-role-grid {
				display: grid;
				grid-template-columns: 1fr 1fr;
				gap: .45rem;
			}
			.pp-role-btn {
				appearance: none;
				border: 1px solid rgba(12,18,34,.12);
				background: #fff;
				border-radius: .8rem;
				padding: .65rem .7rem;
				text-align: left;
				cursor: pointer;
				transition: .15s ease;
			}
			.pp-role-btn:hover { transform: translateY(-1px); border-color: rgba(15,118,110,.45); }
			.pp-role-btn.active {
				background: linear-gradient(160deg, #0f766e, #0c1222 85%);
				color: #fff;
				border-color: transparent;
				box-shadow: 0 10px 20px rgba(15,118,110,.25);
			}
			.pp-role-btn .lbl { font-size: .8rem; font-weight: 700; display:block; }
			.pp-role-btn .dsc { font-size: .68rem; opacity: .8; margin-top: .2rem; line-height: 1.3; }
			.pp-pass-hint {
				margin-top: .65rem;
				font-size: .72rem;
				color: #334155;
				background: rgba(255,255,255,.85);
				border: 1px dashed rgba(15,118,110,.35);
				border-radius: .7rem;
				padding: .5rem .65rem;
			}
			.pp-pass-hint code {
				font-weight: 700;
				color: #0f766e;
			}
			@keyframes ppRise {
				from { opacity: 0; transform: translateY(8px); }
				to { opacity: 1; transform: none; }
			}
			@media (max-width: 420px) {
				.pp-role-grid { grid-template-columns: 1fr; }
			}
			.pp-flash {
				animation: ppFlash .55s ease;
			}
			@keyframes ppFlash {
				0% { box-shadow: 0 0 0 3px rgba(15,118,110,.35); background: #d1fae5; }
				100% { box-shadow: none; }
			}
		`;
		document.head.appendChild(style);
	}

	function findEmailInput() {
		return (
			document.querySelector("#login_email") ||
			document.querySelector('input[type="email"]') ||
			document.querySelector('input[name="usr"]') ||
			document.querySelector('input[autocomplete="username"]') ||
			document.querySelector(".login-content input[type=\"text\"]")
		);
	}

	function findPasswordInput() {
		return (
			document.querySelector("#login_password") ||
			document.querySelector('input[type="password"]') ||
			document.querySelector('input[name="pwd"]') ||
			document.querySelector('input[autocomplete="current-password"]')
		);
	}

	function findMountPoint() {
		const email = findEmailInput();
		if (!email) return null;
		const form = email.closest("form") || email.closest(".login-content") || email.parentElement;
		return form;
	}

	function setNativeValue(input, value) {
		if (!input) return;
		const proto = window.HTMLInputElement.prototype;
		const desc = Object.getOwnPropertyDescriptor(proto, "value");
		if (desc && desc.set) desc.set.call(input, value);
		else input.value = value;
		input.dispatchEvent(new Event("input", { bubbles: true }));
		input.dispatchEvent(new Event("change", { bubbles: true }));
		input.classList.add("pp-flash");
		setTimeout(() => input.classList.remove("pp-flash"), 600);
	}

	function applyRole(role) {
		setNativeValue(findEmailInput(), role.email);
		setNativeValue(findPasswordInput(), role.password);
		const hint = document.getElementById("pp-pass-hint");
		if (hint) {
			hint.innerHTML =
				'Autofilled <strong>' +
				role.label +
				'</strong> · passkey <code>' +
				role.password +
				"</code>";
		}
		document.querySelectorAll(".pp-role-btn").forEach((btn) => {
			btn.classList.toggle("active", btn.dataset.roleId === role.id);
		});
	}

	function mount() {
		if (document.getElementById("pp-role-wrap")) return true;
		const form = findMountPoint();
		if (!form) return false;

		ensureStyles();
		const wrap = document.createElement("div");
		wrap.id = "pp-role-wrap";
		wrap.className = "pp-role-wrap";
		wrap.innerHTML =
			"<h3>PeoplePay360 · Choose role</h3>" +
			'<p class="pp-sub">Tap a role — email &amp; passkey fill automatically</p>' +
			'<div class="pp-role-grid" id="pp-role-grid"></div>' +
			'<div class="pp-pass-hint" id="pp-pass-hint">Pick a role to autofill demo credentials</div>';

		// Insert above the first field / at top of form
		form.insertBefore(wrap, form.firstChild);

		const grid = wrap.querySelector("#pp-role-grid");
		ROLES.forEach((role) => {
			const btn = document.createElement("button");
			btn.type = "button";
			btn.className = "pp-role-btn";
			btn.dataset.roleId = role.id;
			btn.innerHTML =
				'<span class="lbl">' +
				role.label +
				'</span><span class="dsc">' +
				role.description +
				"</span>";
			btn.addEventListener("click", (e) => {
				e.preventDefault();
				e.stopPropagation();
				applyRole(role);
			});
			grid.appendChild(btn);
		});

		// Prefill Employee by default
		applyRole(ROLES[0]);

		// Try loading live credentials from API (keeps seed in sync)
		fetch("/api/method/hrms.peoplepay360.roles.get_demo_role_logins")
			.then((r) => r.json())
			.then((j) => {
				const roles = j.message && j.message.roles;
				if (!roles || !roles.length) return;
				ROLES.splice(0, ROLES.length, ...roles);
				grid.innerHTML = "";
				ROLES.forEach((role) => {
					const btn = document.createElement("button");
					btn.type = "button";
					btn.className = "pp-role-btn";
					btn.dataset.roleId = role.id;
					btn.innerHTML =
						'<span class="lbl">' +
						role.label +
						'</span><span class="dsc">' +
						(role.description || "") +
						"</span>";
					btn.addEventListener("click", (e) => {
						e.preventDefault();
						e.stopPropagation();
						applyRole(role);
					});
					grid.appendChild(btn);
				});
				applyRole(ROLES[0]);
			})
			.catch(() => {});

		return true;
	}

	function boot() {
		if (mount()) return;
		let tries = 0;
		const t = setInterval(() => {
			tries += 1;
			if (mount() || tries > 40) clearInterval(t);
		}, 150);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", boot);
	} else {
		boot();
	}
	window.addEventListener("load", boot);
})();
