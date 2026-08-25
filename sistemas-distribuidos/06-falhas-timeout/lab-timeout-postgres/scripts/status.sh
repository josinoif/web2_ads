#!/usr/bin/env bash
# Status geral + dica. Para Exp. 3/4 use filtro por aluno:
#   ./scripts/status.sh
#   ./scripts/status.sh SD-101 aluno-exp3
set -euo pipefail
API="${API:-http://127.0.0.1:8092}"
DISC="${1:-}"
ALUNO="${2:-}"

if ! curl -sf "${API}/health" >/dev/null; then
  echo "API fora do ar em ${API} — rode ./scripts/up.sh" >&2
  exit 7
fi

curl -s "${API}/admin/config" | python3 -m json.tool
echo "---"
if [[ -n "${DISC}" && -n "${ALUNO}" ]]; then
  curl -sG "${API}/matriculas" \
    --data-urlencode "disciplina_id=${DISC}" \
    --data-urlencode "aluno_id=${ALUNO}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(json.dumps(d, indent=2, ensure_ascii=False))
m,a=d.get('matriculas'), d.get('auditoria_tentativas')
print()
print(f\">> DESTE aluno: matriculas={m} | auditoria_tentativas={a}\")
if m==1 and (a or 0)>1:
    print('>> Exp. 3 OK: unique salvou; side effect (e-mail) duplicou')
elif m==1 and a==1:
    print('>> 1 matrícula; auditoria=1 — se acabou o retry, talvez requests ainda em voo')
"
else
  curl -s "${API}/matriculas" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(json.dumps(d, indent=2, ensure_ascii=False))
print()
print(f\">> total disciplina/global: matriculas={d.get('matriculas')} | auditoria={d.get('auditoria_tentativas')}\")
print('>> Para Exp. 3/4: ./scripts/status.sh SD-101 <aluno>  (não use só o total)')
"
fi
