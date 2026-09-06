#!/bin/bash
set -e
cd /home/frappe/benches/frappe-bench
# Minimal: ensure demo role users + passkeys exist even if full seed fails later
bench --site hrms.localhost execute hrms.peoplepay360.roles.apply_peoplepay360_role_permissions
python3 - <<'PY'
import frappe
frappe.init(site="hrms.localhost", sites_path="sites")
frappe.connect()
frappe.set_user("Administrator")
from hrms.peoplepay360.roles import DEMO_ROLE_LOGINS
from hrms.peoplepay360.demo_seed import _ensure_users
_ensure_users()
frappe.db.commit()
print("Users ready:")
for r in DEMO_ROLE_LOGINS:
    print(f"  {r['label']}: {r['email']} / {r['password']}")
PY
