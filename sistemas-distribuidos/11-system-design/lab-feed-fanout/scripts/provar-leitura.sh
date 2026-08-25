#!/usr/bin/env bash
# GET do leitor (muitos following) vs u1 — write (inbox) vs read (merge).
set -euo pipefail

# Garante alguns posts para o merge não vir vazio
curl -s -X POST http://127.0.0.1:8150/posts -H "Content-Type: application/json" \
  -d '{"author":"u5","text":"para inbox write"}' >/dev/null
curl -s -X POST http://127.0.0.1:8151/posts -H "Content-Type: application/json" \
  -d '{"author":"u5","text":"para merge read"}' >/dev/null

echo "=== WRITE GET (inbox) ==="
echo "-- u1 --"
curl -s http://127.0.0.1:8150/feed/u1 | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:d[k] for k in ('user','origem','tempo_ms','n')})"
echo "-- leitor --"
curl -s http://127.0.0.1:8150/feed/leitor | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:d[k] for k in ('user','origem','tempo_ms','n')})"

echo
echo "=== READ GET (merge) ==="
echo "-- u1 --"
curl -s http://127.0.0.1:8151/feed/u1 | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:d[k] for k in ('user','origem','tempo_ms','n')})"
echo "-- leitor --"
curl -s http://127.0.0.1:8151/feed/leitor | python3 -c "import json,sys; d=json.load(sys.stdin); print({k:d[k] for k in ('user','origem','tempo_ms','n')})"

echo
echo "Observe: no READ, tempo_ms do leitor deve ser ≫ u1 (N followees × delay). No WRITE, os dois GETs são inbox O(página)."
echo "Interprete: fan-out on read empurra o custo para a *leitura*. Híbrido na entrevista: celebridade = pull; comum = push."
