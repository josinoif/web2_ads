# Exercícios Resolvidos — Bloco 2

Exercícios do Bloco 2 ([Dockerfile e Boas Práticas](02-dockerfile-boas-praticas.md)).

---

## Exercício 1 — Diagnóstico de Dockerfile

Analise o Dockerfile abaixo e liste **todas** as violações de boas práticas, numeradas.

```dockerfile
FROM python:latest

ADD . /app
WORKDIR /app

RUN apt update && apt install -y gcc curl git
RUN pip install -r requirements.txt
RUN curl -fsSL https://raw.githubusercontent.com/example/install.sh | bash

ENV AWS_SECRET_ACCESS_KEY=AKIA123456ABCDEF
ENV DEBUG=1

EXPOSE 8000
CMD python app.py
```

### Solução

| # | Violação | Correção |
|---|----------|----------|
| 1 | `FROM python:latest` | pinning de versão: `python:3.12.7-slim-bookworm` |
| 2 | Imagem base completa (~1 GB) | usar `-slim` |
| 3 | `ADD . /app` (tudo + uso de ADD) | trocar por `COPY` separado, primeiro `requirements.txt` |
| 4 | Falta `.dockerignore` visível | incluir ao lado |
| 5 | `apt update` sem `apt-get`; sem `--no-install-recommends`; sem limpeza de `/var/lib/apt/lists` | `RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*` |
| 6 | 3 RUNs separados → 3 camadas desnecessárias | combinar em um (onde faz sentido), especialmente apt+limpeza na mesma linha |
| 7 | `pip install` sem `--no-cache-dir` | adicionar flag |
| 8 | `pip install` **antes** do código = OK; mas `requirements.txt` foi junto no `ADD .` → cache invalida sempre | `COPY requirements.txt .` primeiro |
| 9 | `curl ... | bash` — instalação opaca | usar gerenciador de pacotes ou pinar por hash/versão |
| 10 | `ENV AWS_SECRET_ACCESS_KEY=...` — **segredo gravado na imagem** | remover; passar em runtime ou via secret mount BuildKit |
| 11 | `ENV DEBUG=1` — vai sair em produção por acidente | usar ARG ou injetar em runtime |
| 12 | Sem `USER` — roda como root | `USER appuser` |
| 13 | Sem `HEALTHCHECK` | adicionar |
| 14 | `CMD python app.py` — forma shell, não propaga SIGTERM | forma exec: `CMD ["python", "app.py"]` |
| 15 | Single-stage — carrega `gcc`, `git`, `curl` em runtime desnecessariamente | multi-stage, builder com gcc, final enxuta |
| 16 | Sem labels OCI | `LABEL org.opencontainers.image.*` |

**Dockerfile corrigido (esboço):**

```dockerfile
# syntax=docker/dockerfile:1.6
ARG PYVER=3.12.7

FROM python:${PYVER}-slim-bookworm AS builder
ENV PIP_NO_CACHE_DIR=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:${PYVER}-slim-bookworm
LABEL org.opencontainers.image.title="codelab-app"
RUN groupadd --system app && useradd --system --gid app app
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=app:app src/ ./src/
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
ENTRYPOINT ["python", "-m", "src.app"]
```

---

## Exercício 2 — Cache efetivo

Você construiu duas versões de Dockerfile da CodeLab. Versão A e B. Em ambas, o código está em `src/`, e `requirements.txt` tem 40 libs (instalação demora 90s).

**Versão A:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
USER 1000
CMD ["python", "-m", "src.runner"]
```

**Versão B:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
USER 1000
CMD ["python", "-m", "src.runner"]
```

Uma dev faz dois tipos de mudança:

- (i) edita 1 linha em `src/runner.py`.
- (ii) adiciona 1 lib a `requirements.txt`.

Para cada combinação (Versão × mudança), quanto tempo o `docker build` leva **depois da primeira vez**? Assuma 90s de `pip install` e 2s para o resto.

### Solução

| Caso | Versão | Mudança | O que o cache reaproveita | Tempo aprox. |
|------|--------|---------|----------------------------|--------------|
| A-i | A | edita src | `COPY .` **invalida** — src mudou, logo o `COPY` inteiro muda e tudo depois dele (pip install) é refeito | ~92s |
| A-ii | A | muda requirements | mesma coisa | ~92s |
| B-i | B | edita src | `COPY requirements.txt` + `pip install` **reutilizados**; só muda `COPY src/` | ~4s |
| B-ii | B | muda requirements | `COPY requirements.txt` **invalida**; `pip install` refeito | ~92s |

**Ganho da Versão B:** para a mudança **muito mais comum** (editar código), o build cai de 92s para 4s — ganho de ~23x. Essa é a essência do ordenamento de camadas.

---

## Exercício 3 — Multi-stage para o runner C

O runner C da CodeLab compila código do aluno com `gcc` e executa o binário. Hoje o Dockerfile é single-stage com `gcc` completo (~250 MB).

Proponha um Dockerfile **multi-stage** onde:

- **Stage 1** (builder): imagem com `gcc` compila um "wrapper" em C (`runner`) que recebe código do aluno, compila em `/tmp` e executa.
- **Stage 2** (final): imagem **mínima** que roda o wrapper. Deve ter ainda o `gcc` disponível **em runtime** (para compilar código do aluno).

Justifique as escolhas.

### Solução

Nesse cenário, a decisão é **diferente** de um runner Go/Rust estaticamente linkado: **você precisa do `gcc` em runtime** (o runner compila código do aluno a cada submissão). Logo, a imagem final não pode ser distroless nem scratch.

```dockerfile
# syntax=docker/dockerfile:1.6

# ---- builder: compila o "runner" wrapper ----
FROM debian:12-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY runner.c .
RUN gcc -O2 -static -o /out/runner runner.c

# ---- final: gcc necessário para compilar código do aluno ----
FROM debian:12-slim

LABEL org.opencontainers.image.title="codelab-runner-c"

# gcc mínimo (sem libs de dev extras), limpeza de cache apt na mesma RUN
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system runner \
 && useradd --system --gid runner --home /runner --shell /sbin/nologin runner \
 && mkdir -p /runner /submissao \
 && chown -R runner:runner /runner /submissao

WORKDIR /runner
COPY --from=builder /out/runner /usr/local/bin/runner

USER runner:runner

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD [ -x /usr/local/bin/runner ] || exit 1

ENTRYPOINT ["/usr/local/bin/runner"]
```

**Justificativas:**

- **Builder em debian:12-slim** com gcc: compilamos o wrapper **estaticamente** (`-static`) para poder mover o binário sem dependências.
- **Final também com gcc**, porque precisamos compilar código-fonte do aluno **em runtime**. Não há como fugir — é o uso legítimo do runner.
- Alternativa mais enxuta: usar **Alpine + gcc** (musl libc). Funciona, mas alguns programas do aluno podem depender de glibc específica.
- Em uma arquitetura mais sofisticada, o wrapper poderia ser **externo** ao runner — compila no worker e roda no runner minimal. Aqui mantemos simplicidade.
- `--network=none` seria adicionado no `docker run` (runtime), não no Dockerfile.

---

## Exercício 4 — Verificando que não tem segredo

Você herdou um Dockerfile e suspeita que alguém deixou senha dentro. Quais **três** comandos você roda **sem** conseguir o código-fonte, apenas com a imagem no registry?

### Solução

```bash
# 1. Histórico das camadas — mostra comandos e valores literais de ENV
docker history --no-trunc ghcr.io/codelab/runner-python:0.3.0

# 2. Metadata inteira (ENV, LABELS, ENTRYPOINT, WORKDIR, etc.)
docker inspect ghcr.io/codelab/runner-python:0.3.0

# 3. Exportar FS e grep por palavras-chave
docker save ghcr.io/codelab/runner-python:0.3.0 -o /tmp/img.tar
mkdir -p /tmp/img && tar -xf /tmp/img.tar -C /tmp/img
# Cada *.tar dentro é uma layer; expanda e grep
for f in /tmp/img/*/layer.tar; do
  tar -tf "$f" | head -5   # listar conteúdo
  tar -xOf "$f" | grep -aE "PASSWORD|AKIA|SECRET" || true
done
```

Alternativas:

- **`dive`** — ferramenta interativa que mostra conteúdo por camada: `dive ghcr.io/.../runner-python:0.3.0`
- **`trivy image --security-checks secret`** — detecta segredos automaticamente.

---

## Exercício 5 — Escolha a base

Para cada serviço da CodeLab, escolha a imagem base e justifique.

| Serviço | Linguagem | Característica |
|---------|-----------|----------------|
| API | Python 3.12, FastAPI | Precisa `libpq` (psycopg2) |
| Worker | Python 3.12 | CPU-bound, lógica pura |
| Runner Python | Python | Executa código aluno |
| Runner Go | Go | Só compila + roda binário Go do aluno |
| Runner C | C, gcc runtime | Compila código aluno |

### Solução

| Serviço | Base escolhida | Justificativa |
|---------|----------------|---------------|
| API | `python:3.12.7-slim-bookworm` | `libpq` vem com `psycopg2-binary`; slim é bom default. Distroless python exigiria libpq manual. |
| Worker | `python:3.12.7-slim-bookworm` | idem, mesma base facilita cache multi-imagem |
| Runner Python | `python:3.12.7-slim-bookworm` com `USER` não-root | precisa stdlib e pip do aluno; slim é adequado |
| Runner Go | `gcr.io/distroless/static-debian12:nonroot` | binário estático; sem shell; ataque mínimo |
| Runner C | `debian:12-slim` | gcc em runtime é necessário; distroless sem gcc não serve |

**Nota de economia:** mesma base para API, Worker e Runner Python **compartilha layers** no registry → pull mais rápido no CD, menos armazenamento.

---

## Exercício 6 — Implementar o `analyze_dockerfile.py`

Considere que você quer estender o `analyze_dockerfile.py` para detectar mais um padrão:

> **Regra nova:** se um `RUN` faz `chmod 777`, emitir AVISO.

Descreva (em pseudocódigo + diff) a mudança mínima que adiciona essa regra.

### Solução

1. Acrescentar o pattern:

```python
RE_CHMOD_777 = re.compile(r"chmod\s+777", re.IGNORECASE)
```

2. Dentro do bloco `if RE_RUN.match(linha):` adicionar:

```python
if RE_CHMOD_777.search(cmd):
    a.registrar("AVISO", i, "chmod-777",
                "chmod 777 concede permissão total a qualquer usuário. Prefira 755 + chown.")
```

3. Teste mínimo (em `tests/test_analyze.py`):

```python
from pathlib import Path
import analyze_dockerfile as a

def test_chmod_777_aviso(tmp_path):
    p = tmp_path / "Dockerfile"
    p.write_text("FROM python:3.12-slim\nRUN chmod 777 /app\nUSER 1000\nHEALTHCHECK CMD true\n")
    res = a.analisar(p)
    assert any(x.regra == "chmod-777" for x in res.achados)
```

**Bom padrão pedagógico:** toda regra de linter deveria nascer de um **incidente real** (ou quase-incidente). Aqui, `chmod 777` em container já causou vazamento de dados quando alguém leu `/etc/passwd` modificado — exatamente o Sintoma 3 da CodeLab.

---

## Próximo passo

- Siga para o **[Bloco 3 — Docker Compose e ambientes multi-serviço](../bloco-3/03-compose-multi-servico.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Dockerfile e Boas Práticas](02-dockerfile-boas-praticas.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Bloco 3 — Docker Compose e Ambientes Multi-Serviço](../bloco-3/03-compose-multi-servico.md) |

<!-- nav:end -->
