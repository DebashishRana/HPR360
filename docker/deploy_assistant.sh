#!/bin/bash
set -e
SRC=/workspace/hpr360
DST=/home/frappe/benches/frappe-bench/apps/hrms
ASSETS=/home/frappe/benches/frappe-bench/sites/assets/hrms

chown -R frappe:frappe "$DST/hrms" "$ASSETS" || true
mkdir -p "$DST/hrms/peoplepay360/chatbot" "$DST/hrms/hr/page/pp_assistant" "$DST/hrms/hr/workspace/peoplepay360" "$DST/hrms/public/js" "$DST/hrms/public/css" "$ASSETS/js" "$ASSETS/css"

cp -af "$SRC/hrms/peoplepay360/chatbot/." "$DST/hrms/peoplepay360/chatbot/"
cp -af "$SRC/hrms/hr/page/pp_assistant/." "$DST/hrms/hr/page/pp_assistant/"
cp -f "$SRC/hrms/public/js/peoplepay360_chat.js" "$DST/hrms/public/js/peoplepay360_chat.js"
cp -f "$SRC/hrms/public/css/peoplepay360_chat.css" "$DST/hrms/public/css/peoplepay360_chat.css"
cp -f "$SRC/hrms/public/js/peoplepay360_chat.js" "$ASSETS/js/peoplepay360_chat.js"
cp -f "$SRC/hrms/public/css/peoplepay360_chat.css" "$ASSETS/css/peoplepay360_chat.css"
cp -f "$SRC/hrms/public/js/peoplepay360_ui.js" "$DST/hrms/public/js/peoplepay360_ui.js"
cp -f "$SRC/hrms/public/js/peoplepay360_ui.js" "$ASSETS/js/peoplepay360_ui.js"
cp -f "$SRC/hrms/hooks.py" "$DST/hrms/hooks.py"
cp -f "$SRC/hrms/peoplepay360/roles.py" "$DST/hrms/peoplepay360/roles.py"
cp -f "$SRC/hrms/hr/workspace/peoplepay360/peoplepay360.json" "$DST/hrms/hr/workspace/peoplepay360/peoplepay360.json"
chown -R frappe:frappe "$DST/hrms" "$ASSETS"

cd /home/frappe/benches/frappe-bench
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost execute hrms.peoplepay360.chatbot.install.setup_assistant
runuser -u frappe -- env HOME=/home/frappe bench --site hrms.localhost clear-cache
echo ASSISTANT_OK
