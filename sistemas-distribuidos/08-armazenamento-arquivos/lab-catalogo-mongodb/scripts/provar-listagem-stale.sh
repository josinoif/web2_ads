#!/usr/bin/env bash
# Listagem stale: snapshot → novo upload → GET ainda antigo → desliga sim.
set -euo pipefail

echo "=== snapshot + liga stale ==="
curl -s -X PUT http://127.0.0.1:8092/admin/config \
  -H 'Content-Type: application/json' \
  -d '{"read_from_secondary_sim": true}' | python3 -m json.tool

echo "=== novo upload (blob+meta ok) ==="
./scripts/enviar.sh aluno-stale

echo "=== listagem (espera leitura=stale_sim, sem o novo aluno) ==="
curl -s http://127.0.0.1:8092/entregas | python3 -m json.tool

echo "=== desliga stale ==="
curl -s -X PUT http://127.0.0.1:8092/admin/config \
  -H 'Content-Type: application/json' \
  -d '{"read_from_secondary_sim": false}' | python3 -m json.tool

echo "=== listagem fresh ==="
curl -s http://127.0.0.1:8092/entregas | python3 -m json.tool
