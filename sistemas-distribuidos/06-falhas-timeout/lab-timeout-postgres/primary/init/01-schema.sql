-- Matrícula + idempotência — lab falhas/timeout
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

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(128) PRIMARY KEY,
    -- Escopo didático: mesma key + corpo diferente → rejeitar (não replay).
    request_fingerprint VARCHAR(256) NOT NULL,
    response_json TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Cada tentativa de escrita (mesmo retry) gera uma linha — mede efeito colateral.
CREATE TABLE IF NOT EXISTS auditoria_tentativas (
    id BIGSERIAL PRIMARY KEY,
    disciplina_id VARCHAR(64) NOT NULL,
    aluno_id VARCHAR(64) NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO disciplinas (id, nome, vagas_restantes) VALUES
    ('SD-101', 'Sistemas Distribuídos', 30),
    ('BD-201', 'Banco de Dados', 30),
    ('RC-301', 'Redes', 30)
ON CONFLICT (id) DO NOTHING;
