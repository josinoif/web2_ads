#!/usr/bin/env bash
# Publica sem invalidar → leitura stale até TTL
set -euo pipefail
API="${API:-http://127.0.0.1:8095}"

./scripts/set-invalidate.sh 0
./scripts/set-ttl.sh 15
./scripts/flush.sh

echo "=== popula cache ==="
curl -s "${API}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print('cache=', d['cache'], 'total=', d['total'])"

echo "=== publica novo aviso (invalidate OFF) ==="
./scripts/publicar.sh "Aviso-stale-$(date +%s)" "deve aparecer so apos TTL ou flush"

echo "=== leitura imediata (stale esperado — total antigo) ==="
curl -s "${API}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print('cache=', d['cache'], 'total=', d['total'], 'titulo0=', (d['avisos'][0]['titulo'] if d['avisos'] else None))"

echo "=== flush e releitura (valor novo) ==="
./scripts/flush.sh
curl -s "${API}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print('cache=', d['cache'], 'total=', d['total'], 'titulo0=', (d['avisos'][0]['titulo'] if d['avisos'] else None))"
