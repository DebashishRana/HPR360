#!/bin/bash
cd /home/frappe/frappe-bench
bench --site hrms.localhost execute hrms.patches.v17_0.setup_peoplepay360.execute
bench --site hrms.localhost mariadb -Ne "select name from \`tabDocType\` where name in ('Employment Contract','Working Schedule','Payroll Entry','Salary Slip');"
echo "---ROLES---"
bench --site hrms.localhost mariadb -Ne "select name from \`tabRole\` where name in ('HR Payroll User','HR Payroll Manager','HR Manager','Employee');"
echo "---FIELDS---"
bench --site hrms.localhost mariadb -Ne "select concat(dt,'.',fieldname) from \`tabCustom Field\` where fieldname in ('working_schedule','salary_structure','salary_rule_category','sequence_id');"
echo "---PAGES---"
bench --site hrms.localhost mariadb -Ne "select name from \`tabPage\` where name in ('payrun-processing','payroll-dashboard','working-schedule-setup');"
echo "---WORKSPACE---"
bench --site hrms.localhost mariadb -Ne "select name from \`tabWorkspace\` where name like 'PeoplePay%';"
bench --site hrms.localhost clear-cache
echo DONE
