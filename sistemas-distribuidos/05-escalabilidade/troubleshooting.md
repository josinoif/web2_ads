# Troubleshooting — Escalabilidade

**Módulo:** [05 — Escalabilidade](README.md)

---

## Docker / daemon

| Sintoma | Ação |
|---------|------|
| `failed to connect … desktop/docker.sock` | Docker Desktop parado — inicie o app; ou use Podman (abaixo) |
| `permission denied … /var/run/docker.sock` | Usuário fora do grupo `docker` |
| `bitnami/postgresql:16` → `manifest unknown` | Lab 05/`04` app: `postgres:16-alpine`. Labs 02/03 (replicação Bitnami): `bitnamilegacy/postgresql:16.6.0-debian-12-r2` |
| Bind mount `Permission denied` (Fedora/Podman) | Volumes com `,Z` (SELinux) — já no compose do lab app |
| nginx `no live upstreams` / 502 após recreate | `docker compose up -d --force-recreate nginx` (IPs mudaram) |
| Podman rootless | Scripts detectam `podman.sock`; ou: `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock DOCKER_CONTEXT=default` |

**Piloto professor (preenche Validação local):**

```bash
cd sistemas-distribuidos/05-escalabilidade
./scripts/piloto-validacao.sh
```

---

## Geral

| Sintoma | Ação |
|---------|------|
| Porta em uso (`8089`, `8090`, `8091`, `5439`…) | `docker compose down -v` no lab anterior |
| `connection refused` | Poll `/health`; `compose ps` |
| RPS 1≈3 APIs (ganho ~1×) | Use defaults `N=240 CONCURRENCY=48` (não `LIGHT=1`); confira `work_ms=15` (busy-wait) |
| Notebook lento / esquenta | `LIGHT=1 ./scripts/comparar-escala.sh` (N=120 C=24) — ganho menor, ainda costuma &gt;1,2× |
| nginx 502 | api2/api3 parados? Recreate nginx; `:8091` = 1 API, `:8089` = 3 |

**Um lab por vez.**

**Ballpark (piloto 2026-08-24, Podman rootless, Fedora):**  
`WORK_MS=15` busy-wait, `N=240`, `CONCURRENCY=48` → **ganho 1→3 ≈ 1,84×**.  
`aproximar-teto`: app-bound ~111 RPS → store-bound ~48 RPS.

---

## Lab aplicação (`8089` / `8091`)

```bash
cd sistemas-distribuidos/05-escalabilidade/lab-escala-aplicacao
docker compose up -d --build   # ou Podman via DOCKER_HOST=…/podman.sock
for i in $(seq 1 20); do curl -sf http://localhost:8089/health && break; sleep 2; done
```

### Comparar 1 vs 3

```bash
./scripts/comparar-escala.sh   # default N=240 C=48
# notebook fraco:
LIGHT=1 ./scripts/comparar-escala.sh
```

### Worker lento

```bash
API=http://localhost:8089 N=120 CONCURRENCY=24 ./scripts/medir-rps.sh   # baseline p99
./scripts/worker-lento.sh 120
API=http://localhost:8089 N=120 CONCURRENCY=24 ./scripts/medir-rps.sh   # p99 sobe
./scripts/worker-lento.sh 0
```

### Aproximar teto do store

```bash
./scripts/aproximar-teto.sh
```

Fase B (`DB_SLOTS=1` + `STORE_HOLD_MS=40`) deve mostrar RPS **menor** que fase A.

---

## Lab dados (`8090`)

```bash
cd sistemas-distribuidos/05-escalabilidade/lab-escala-dados
docker compose up -d --build
```

Evidência principal: contagens hot (B≈0) vs spread (A≈B). Fan-out: `duracao_ms` ≈ 2× single.

---

## Checklist professor

- [x] `docker`/`podman` ok neste host  
- [x] `comparar-escala` ganho &gt; 1,5×  
- [x] `aproximar-teto` RPS B &lt; A  
- [x] `medir-writes` hot B≈0; spread A≈B; fan-out ≥ single  
- [x] Validação local preenchida  

---

## Validação local

| Campo | Valor |
|-------|-------|
| **Data** | 2026-08-24T22:40-03 (piloto agente) |
| **SO / Docker** | Linux 7.0.14 fc44 x86_64; Podman 5.8.3 via `DOCKER_HOST=…/podman.sock` (Desktop sock ausente) |
| **comparar-escala (ganho)** | **1,84×** (rps 52,98 → 97,68; N=240 C=48; WORK_MS=15 busy-wait) |
| **aproximar-teto (A vs B)** | A≈110,9 RPS → B≈48,2 RPS (razão 0,43); DB_SLOTS=1 + STORE_HOLD=40ms |
| **medir-writes (shards)** | hot A=40 B=0; spread A=20 B=20; fan-out 43ms vs single 22ms |
| **worker lento (p99)** | baseline p99≈218 → com delay 80ms em api2 p99≈265 (cauda sobe) |
| **Observações** | `bitnami/postgresql:16` quebrado → `postgres:16-alpine` (04/05) e `bitnamilegacy/…@sha256:af99…` (02/03, pin). Lab 03: `ativar-sync.sh` após up. Montagens `,Z`. `LIGHT=1` no comparar 05. Piloto 02 (replica streaming) e 03 (`sync_state=quorum`, `sync_ativo=true`) OK em 2026-08-24 via Podman. |

---

## Fallback sem Docker

Leia [teoria.md](teoria.md) §1–7 e [decisoes.md](decisoes.md). Desenhe as duas camadas, os dois fluxos (boletim vs avisos) e a sequência 1 API → N APIs → réplica → partição.
