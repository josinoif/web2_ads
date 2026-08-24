-- Matrícula com vagas limitadas (lab CP / partição)
CREATE TABLE IF NOT EXISTS disciplinas (
    id VARCHAR(64) PRIMARY KEY,
    nome VARCHAR(128) NOT NULL,
    vagas_restantes INT NOT NULL CHECK (vagas_restantes >= 0)
);

CREATE TABLE IF NOT EXISTS matriculas (
    disciplina_id VARCHAR(64) NOT NULL REFERENCES disciplinas (id),
    aluno_id VARCHAR(64) NOT NULL,
    matriculado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (disciplina_id, aluno_id)
);

INSERT INTO disciplinas (id, nome, vagas_restantes) VALUES
    ('SD-101', 'Sistemas Distribuídos', 1),
    ('BD-201', 'Banco de Dados', 30)
ON CONFLICT (id) DO NOTHING;
