-- Schema do portal acadêmico (lab sync vs async)
CREATE TABLE IF NOT EXISTS notas (
    id SERIAL PRIMARY KEY,
    aluno_id VARCHAR(64) NOT NULL,
    disciplina VARCHAR(128) NOT NULL,
    valor NUMERIC(4, 1) NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (aluno_id, disciplina)
);

CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas (aluno_id);
