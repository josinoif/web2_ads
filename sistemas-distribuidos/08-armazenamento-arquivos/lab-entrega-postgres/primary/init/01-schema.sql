CREATE TABLE IF NOT EXISTS entregas (
  id            SERIAL PRIMARY KEY,
  aluno_id      TEXT NOT NULL,
  disciplina    TEXT NOT NULL,
  nome_arquivo  TEXT NOT NULL,
  object_key    TEXT NOT NULL,
  sha256        TEXT NOT NULL,
  tamanho_bytes INTEGER NOT NULL,
  storage       TEXT NOT NULL DEFAULT 'minio',
  status        TEXT NOT NULL DEFAULT 'entregue',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entregas_aluno ON entregas (aluno_id);
CREATE INDEX IF NOT EXISTS idx_entregas_key ON entregas (object_key);
