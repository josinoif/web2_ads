# Parte 2 — Dockerfile do Runner Python

**Duração:** 90 a 120 minutos
**Pré-requisitos:** Parte 1 concluída, Bloco 2 ([Dockerfile e Boas Práticas](../bloco-2/02-dockerfile-boas-praticas.md)) estudado.

---

## Contexto

Com o diagnóstico feito, você escolheu o **runner Python** como primeira peça (ou outra, desde que justificada). Agora vai construir a imagem **de verdade** — idiomática, pequena, segura.

---

## Tarefas

### 1. Código mínimo do runner

Crie o esqueleto do runner em `src/codelab/runners/python/run.py`:

```python
"""Runner Python da CodeLab — executa uma submissão de aluno e retorna veredito.

Este é um esqueleto. Em produção há sandboxing adicional, logging, timeout, etc.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Veredito:
    status: str            # "AC", "WA", "RE", "TLE"
    stdout: str
    stderr: str
    duracao_ms: int


def executar(codigo: Path, entrada: str, timeout_s: float = 5.0) -> Veredito:
    inicio = time.perf_counter()
    try:
        r = subprocess.run(
            [sys.executable, str(codigo)],
            input=entrada,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        duracao = int((time.perf_counter() - inicio) * 1000)
        if r.returncode != 0:
            return Veredito("RE", r.stdout, r.stderr, duracao)
        return Veredito("AC", r.stdout, r.stderr, duracao)
    except subprocess.TimeoutExpired as e:
        duracao = int((time.perf_counter() - inicio) * 1000)
        return Veredito("TLE", e.stdout or "", e.stderr or "", duracao)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--codigo", required=True, type=Path)
    p.add_argument("--entrada", default="")
    p.add_argument("--timeout", type=float, default=5.0)
    args = p.parse_args(argv)

    v = executar(args.codigo, args.entrada, args.timeout)
    print(f"status={v.status} duracao_ms={v.duracao_ms}")
    print("--- stdout ---")
    print(v.stdout, end="")
    print("--- stderr ---")
    print(v.stderr, end="")
    return 0 if v.status == "AC" else 1


if __name__ == "__main__":
    sys.exit(main())
```

Não precisa implementar nada além disso — o foco é a imagem.

### 2. `requirements.txt` do runner

Mínimo:

```
# sem dependências externas no runner Python; usar só stdlib
```

Arquivo vazio (ou só com um comentário) está certo. Mostra que o runner é enxuto.

### 3. `.dockerignore`

Crie `.dockerignore` na raiz com, no mínimo, o recomendado no Bloco 2 (VCS, cache Python, envs, segredos, docs, IDE).

### 4. `docker/runner-python.Dockerfile`

Escreva um Dockerfile **multi-stage** que atenda a **todos** estes requisitos:

- `FROM python:3.12.Z-slim-bookworm` (com Z fixo).
- Argumentos `GIT_SHA` e `VERSION` + labels OCI.
- Usuário não-root `runner` com UID/GID 10001.
- Working directory `/runner`.
- Copia o código para dentro com `chown`.
- `ENTRYPOINT` em forma exec.
- Sem `curl`, `git` ou `gcc` na imagem final.
- Tamanho final **≤ 200 MB**.

Use o Dockerfile do Bloco 2 como guia, mas **não copie** — adapte ao runner.

### 5. Build e inspeção

```bash
docker build \
  --build-arg GIT_SHA=$(git rev-parse --short HEAD) \
  --build-arg VERSION=0.1.0 \
  -t codelab/runner-python:0.1.0 \
  -f docker/runner-python.Dockerfile \
  .

docker images codelab/runner-python:0.1.0
```

Meça o tamanho. Se > 200 MB, **volte e otimize**. Investigue com:

```bash
dive codelab/runner-python:0.1.0
```

(ou `docker history --no-trunc codelab/runner-python:0.1.0` se não tiver `dive`).

### 6. Análise estática

Rode o `analyze_dockerfile.py` do Bloco 2 contra o seu Dockerfile. Tratamento mínimo:

- **Zero ERROs**.
- Avisos restantes devem ter justificativa em comentário (no próprio Dockerfile ou no ADR — próximo passo).

Alternativa: `hadolint docker/runner-python.Dockerfile` — aceitar se o resultado for só warnings conhecidos.

### 7. Rodar e observar

```bash
# Montar um código de teste
mkdir -p /tmp/sub-1
cat > /tmp/sub-1/main.py << 'EOF'
n = int(input())
print(sum(range(1, n + 1)))
EOF

# Rodar o runner com proteções mínimas
docker run --rm \
  --network=none --read-only \
  --tmpfs /tmp:rw,size=32m,mode=1777 \
  --user 10001:10001 \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  --pids-limit=30 \
  --memory=128m --memory-swap=128m --cpus=0.5 \
  -v "/tmp/sub-1:/submissao:ro" \
  codelab/runner-python:0.1.0 \
  --codigo=/submissao/main.py --entrada=10
```

Saída esperada (abreviada):

```
status=AC duracao_ms=...
--- stdout ---
55
--- stderr ---
```

### 8. ADR-001 — imagem base

Crie `docs/adr/001-imagem-base.md`:

```markdown
# ADR-001: Imagem base do runner Python

## Status
Aprovado em 2026-05-XX.

## Contexto
...

## Decisão
Adotamos `python:3.12.7-slim-bookworm` como base dos runners Python.

## Alternativas consideradas
- `python:3.12` — ~1 GB, desnecessário.
- `python:3.12-alpine` — musl libc quebra alguns wheels; benefício marginal.
- `gcr.io/distroless/python3` — sem shell; dificulta debug e exige que a imagem empacote tudo. Reavaliar no futuro.

## Consequências
- Tamanho final ~170 MB.
- Mantemos `apt` para eventual troubleshooting em staging.
- Aceitamos superfície de ataque levemente maior em troca de ergonomia.
```

---

## O que entregar

1. **Código:**
   - `src/codelab/runners/python/run.py`
   - `docker/runner-python.Dockerfile`
   - `.dockerignore`
2. **Evidências:**
   - Saída de `docker images` mostrando tamanho.
   - Saída do `analyze_dockerfile.py` (ou `hadolint`) com 0 ERROs.
   - Captura de execução bem-sucedida do container com flags de isolamento.
3. **Documentação:**
   - `docs/adr/001-imagem-base.md` justificando a base.

## Critérios de aceitação

- Dockerfile **multi-stage** com builder stage enxuto (sem dependências externas, ainda assim separa camadas).
- Labels OCI presentes e parametrizadas.
- Tamanho final ≤ 200 MB.
- Usuário não-root (`USER 10001:10001` ou nominal).
- `ENTRYPOINT` forma exec.
- `HEALTHCHECK` presente (ou ADR justificando ausência — runner efêmero, sem endpoint).
- Execução com flags do exercício 7 **funciona** e produz veredito correto (AC para soma).

---

## Dicas e armadilhas

- Não tente colocar `curl` na imagem só para healthcheck. Se precisar, use `python -c "import urllib.request..."`.
- Se o `chown` não funciona porque o binário é builder-stage copiado, ajuste para copiar com `--chown=runner:runner` OU faça o `chown -R` num `RUN` final.
- `--read-only` quebra se o Python tentar criar `__pycache__` — por isso `tmpfs /tmp` e `ENV PYTHONDONTWRITEBYTECODE=1`.
- Builder stage vazio (sem `pip install`) é aceitável aqui — runner não tem deps. Se preferir single-stage enxuto, documente no ADR.

---

## Próximo passo

Avance para a **[Parte 3 — Compose stack](parte-3-compose-stack.md)** para subir API + Worker + Redis + Postgres + Runner juntos.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Diagnóstico da CodeLab](parte-1-diagnostico.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Parte 3 — Stack Local com Docker Compose](parte-3-compose-stack.md) |

<!-- nav:end -->
