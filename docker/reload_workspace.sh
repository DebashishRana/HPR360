#!/bin/bash
set -e
cd /home/frappe/benches/frappe-bench
ABS=/home/frappe/benches/frappe-bench/apps/hrms/hrms/hr/workspace/peoplepay360/peoplepay360.json
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost execute frappe.modules.import_file.import_file_by_path --kwargs "{'path': '$ABS', 'force': True}"
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost execute hrms.peoplepay360.roles.fix_desk_shell_access
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost clear-cache
echo ALL_OK
