#!/bin/bash
set -e
cd /home/frappe/benches/frappe-bench
mkdir -p logs
bench --site hrms.localhost execute hrms.peoplepay360.demo_seed.seed_peoplepay360_demo --kwargs '{"force": True}'
