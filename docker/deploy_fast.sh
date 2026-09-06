#!/bin/bash
set -e
SRC=/workspace/hpr360
DST=/home/frappe/benches/frappe-bench/apps/hrms

cp -f "$SRC/hrms/www/peoplepay360_login.html" "$DST/hrms/www/peoplepay360_login.html"
cp -f "$SRC/hrms/peoplepay360/roles.py" "$DST/hrms/peoplepay360/roles.py"
cp -f "$SRC/hrms/hr/workspace/peoplepay360/peoplepay360.json" "$DST/hrms/hr/workspace/peoplepay360/peoplepay360.json"
cp -f "$SRC/hrms/public/js/peoplepay360_ui.js" "$DST/hrms/public/js/peoplepay360_ui.js"
cp -f "$SRC/hrms/public/js/peoplepay360_landing.js" "$DST/hrms/public/js/peoplepay360_landing.js"
mkdir -p /home/frappe/benches/frappe-bench/sites/assets/hrms/js
cp -f "$SRC/hrms/public/js/peoplepay360_ui.js" /home/frappe/benches/frappe-bench/sites/assets/hrms/js/peoplepay360_ui.js
cp -f "$SRC/hrms/public/js/peoplepay360_landing.js" /home/frappe/benches/frappe-bench/sites/assets/hrms/js/peoplepay360_landing.js

cd /home/frappe/benches/frappe-bench
# Fast: only Page/Workspace/Report read + workspace role list update
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost execute hrms.peoplepay360.roles.fix_desk_shell_access
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost clear-cache
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost clear-website-cache
echo DONE
