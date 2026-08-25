-- Boletim — lab cache distribuído (Postgres)
CREATE TABLE IF NOT EXISTS boletim (
    aluno_id VARCHAR(64) PRIMARY KEY,
    disciplina_id VARCHAR(64) NOT NULL,
    nota NUMERIC(4, 2) NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO boletim (aluno_id, disciplina_id, nota) VALUES
    ('aluno-01', 'SD-101', 7.50),
    ('aluno-02', 'SD-101', 8.00),
    ('aluno-03', 'BD-201', 6.50)
ON CONFLICT (aluno_id) DO NOTHING;
