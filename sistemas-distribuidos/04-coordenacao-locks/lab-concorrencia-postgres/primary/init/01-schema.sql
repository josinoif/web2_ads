-- Matrícula com vagas limitadas (lab concorrência / coordenação)
CREATE TABLE IF NOT EXISTS disciplinas (
    id VARCHAR(64) PRIMARY KEY,
    nome VARCHAR(128) NOT NULL,
    vagas_restantes INT NOT NULL CHECK (vagas_restantes >= 0),
    version INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS matriculas (
    disciplina_id VARCHAR(64) NOT NULL REFERENCES disciplinas (id),
    aluno_id VARCHAR(64) NOT NULL,
    matriculado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    api_instance VARCHAR(64),
    modo VARCHAR(32) NOT NULL DEFAULT 'transaction',
    PRIMARY KEY (disciplina_id, aluno_id)
);

INSERT INTO disciplinas (id, nome, vagas_restantes, version) VALUES
    ('SD-101', 'Sistemas Distribuídos', 1, 0),
    ('BD-201', 'Banco de Dados', 30, 0)
ON CONFLICT (id) DO NOTHING;
