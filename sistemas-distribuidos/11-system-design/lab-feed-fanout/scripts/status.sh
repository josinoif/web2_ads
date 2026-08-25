#!/usr/bin/env bash
set -euo pipefail
echo "=== write :8150/health ==="
curl -s http://127.0.0.1:8150/health | python3 -m json.tool || echo "(indisponível)"
echo "=== read :8151/health ==="
curl -s http://127.0.0.1:8151/health | python3 -m json.tool || echo "(indisponível)"
echo "=== celeb / u1 / leitor (write) ==="
for u in celeb u1 leitor; do
  echo "-- $u --"
  curl -s "http://127.0.0.1:8150/users/${u}" | python3 -m json.tool || true
done
