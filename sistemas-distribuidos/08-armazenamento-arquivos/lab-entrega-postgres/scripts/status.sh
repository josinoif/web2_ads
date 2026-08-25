#!/usr/bin/env bash
set -euo pipefail
echo "=== api1 ==="
curl -s http://127.0.0.1:8090/admin/config | python3 -m json.tool
echo "=== api2 ==="
curl -s http://127.0.0.1:8091/admin/config | python3 -m json.tool
echo "=== entregas ==="
curl -s http://127.0.0.1:8090/entregas | python3 -m json.tool
