#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8086}"

echo "=== majority / primary ==="
curl -sS "${API}/avisos?dest=primary&readConcern=majority&limit=5" | python3 -m json.tool
echo
echo "=== local / secondary (pode divergir sob partição) ==="
curl -sS "${API}/avisos?dest=secondary&readConcern=local&limit=5" | python3 -m json.tool
