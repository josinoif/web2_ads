#!/usr/bin/env bash
set -euo pipefail
curl -s http://127.0.0.1:8093/admin/config | python3 -m json.tool
echo "---"
curl -s http://127.0.0.1:8093/avisos | python3 -m json.tool
