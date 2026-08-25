#!/usr/bin/env bash
# REJECT_ON_INTEGRITY_FAIL: 0 = soft verify; 1 = HTTP 409 no GET com hash divergente.
set -euo pipefail
VAL="${1:-0}"
curl -s -X PUT "http://127.0.0.1:8092/admin/config" \
  -H "Content-Type: application/json" \
  -d "{\"reject_on_integrity_fail\": ${VAL}}" | python3 -m json.tool
