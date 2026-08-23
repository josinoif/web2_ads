#!/usr/bin/env bash
# Verifica se o hash bcrypt em seed.sql corresponde à senha secret123.
# Uso: a partir de backend/nest/ → bash seed/verify-seed.sh
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
HASH="$(grep -oE '\$2b\$10\$[[:alnum:]./]+' "$DIR/seed.sql" | head -1)"

if [[ -z "$HASH" ]]; then
  echo "FALHA: nenhum hash \$2b\$10\$ encontrado em seed.sql" >&2
  exit 1
fi

# npm exec resolve módulos a partir do cwd. Em pastas sem package.json
# (ex.: backend/nest/) o pacote não fica acessível ao `node -e` — por isso
# rodamos em um diretório temporário.
WORKDIR="$(mktemp -d)"
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

export SEED_HASH="$HASH"
(
  cd "$WORKDIR"
  npm exec --yes --package=bcryptjs -- node -e "
const bcrypt = require('bcryptjs');
bcrypt.compare('secret123', process.env.SEED_HASH).then((ok) => {
  if (!ok) {
    console.error('FALHA: hash em seed.sql não corresponde a secret123');
    process.exit(1);
  }
  console.log('OK: seed.sql verificado (ana/cli → secret123)');
});
"
)
