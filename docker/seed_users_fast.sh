#!/bin/bash
set -e
cd /home/frappe/benches/frappe-bench
mkdir -p sites/hrms.localhost/logs logs
# Create a tiny whitelisted helper call via bench execute
bench --site hrms.localhost execute hrms.peoplepay360.demo_seed.ensure_demo_login_users
