#!/usr/bin/env bash
# Compara tempo até push: fila única (e-mail atrasa) vs filas por canal.
set -euo pipefail

compare() {
  local nome="$1"
  local base="$2"
  local id="cmp-${nome}-$(date +%s%N)"
  echo "=== $nome ($base) ==="
  curl -s -X POST "$base/admin/reset" >/dev/null
  sleep 0.4
  local t0 t1 now before
  before="$(curl -s "$base/status" | python3 -c "import json,sys; print(json.load(sys.stdin)['enviados'].get('push',0))")"
  t0="$(date +%s%N)"
  # email primeiro na lista → no modo unico processa email (2s) antes do push
  curl -s -X POST "$base/eventos" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"${id}\",\"user\":\"u1\",\"canais\":[\"email\",\"push\",\"sms\"]}" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print('202 aceito', d.get('canais_enfileirados'))"
  now="$before"
  local i
  for i in $(seq 1 60); do
    now="$(curl -s "$base/status" | python3 -c "import json,sys; print(json.load(sys.stdin)['enviados'].get('push',0))")"
    if [[ "$now" -gt "$before" ]]; then
      break
    fi
    sleep 0.15
  done
  t1="$(date +%s%N)"
  echo "tempo_ate_push_ms≈$(( (t1 - t0) / 1000000 )) enviados_push=$now"
  curl -s "$base/status" | python3 -c "import json,sys; print('enviados', json.load(sys.stdin)['enviados'])"
  echo
}

compare "unico" "http://127.0.0.1:8170"
compare "canais" "http://127.0.0.1:8171"

echo "Observe: UNICO push ~≥2000 ms; CANAIS push << email."
echo "Interprete: um SMTP lento na fila única segura o push — Mock 1 / ficha Notification."
