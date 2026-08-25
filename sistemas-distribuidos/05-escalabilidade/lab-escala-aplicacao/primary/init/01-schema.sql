-- Notas / boletim — lab escala de aplicação
CREATE TABLE IF NOT EXISTS alunos (
    id VARCHAR(64) PRIMARY KEY,
    nome VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS notas (
    aluno_id VARCHAR(64) NOT NULL REFERENCES alunos (id),
    disciplina_id VARCHAR(64) NOT NULL,
    nota NUMERIC(4, 1) NOT NULL,
    PRIMARY KEY (aluno_id, disciplina_id)
);

INSERT INTO alunos (id, nome)
SELECT 'aluno-' || g, 'Aluno ' || g
FROM generate_series(1, 200) AS g
ON CONFLICT (id) DO NOTHING;

INSERT INTO notas (aluno_id, disciplina_id, nota)
SELECT 'aluno-' || g, d.disciplina_id, (5 + (g % 50) / 10.0)::numeric(4,1)
FROM generate_series(1, 200) AS g
CROSS JOIN (VALUES ('SD-101'), ('BD-201'), ('RC-301')) AS d(disciplina_id)
ON CONFLICT DO NOTHING;
