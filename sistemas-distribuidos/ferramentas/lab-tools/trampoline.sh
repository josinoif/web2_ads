#!/usr/bin/env bash
# Encaminha para sistemas-distribuidos/lab.sh. Igual em todos os labs — não edite.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
while [[ -n "$DIR" && "$DIR" != "/" ]]; do
  if [[ -f "$DIR/ferramentas/lab-tools/Dockerfile" && -f "$DIR/lab.sh" ]]; then
    exec "$DIR/lab.sh" "$@"
  fi
  PARENT="$(dirname "$DIR")"
  [[ "$PARENT" == "$DIR" ]] && break
  DIR="$PARENT"
done
echo "não achei sistemas-distribuidos/lab.sh (pasta com ferramentas/lab-tools)." >&2
exit 2
