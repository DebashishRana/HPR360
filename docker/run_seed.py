#!/usr/bin/env python3
import os
import frappe

os.chdir("/home/frappe/benches/frappe-bench")
frappe.init(site="hrms.localhost", sites_path="sites")
frappe.connect()
frappe.set_user("Administrator")
from hrms.peoplepay360.demo_seed import seed_peoplepay360_demo

result = seed_peoplepay360_demo(force=True)
frappe.db.commit()
print(result)
