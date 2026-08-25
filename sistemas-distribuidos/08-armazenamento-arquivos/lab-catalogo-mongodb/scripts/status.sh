#!/usr/bin/env bash
set -euo pipefail
curl -s http://127.0.0.1:8092/admin/config | python3 -m json.tool
echo "=== entregas ==="
curl -s http://127.0.0.1:8092/entregas | python3 -m json.tool
echo "=== objetos ==="
curl -s http://127.0.0.1:8092/admin/objetos | python3 -m json.tool
