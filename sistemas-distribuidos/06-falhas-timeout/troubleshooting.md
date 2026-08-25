# Troubleshooting — Labs do módulo 06

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v
```

Encerre labs 02–05 se as portas conflitarem.

---

## Portas deste módulo

| Serviço | Host |
|---------|------|
| API Postgres | **8092** |
| Postgres | **5440** |
| API Mongo | **8093** |
| Mongo | **27121** |

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| `Cannot connect to Docker daemon` | Suba Docker Desktop **ou** Podman: `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock` |
| Porta em uso | `docker ps`; `down -v` no outro lab; confira 8092/8093/5440/27121 |
| API 503 no boot | Store ainda subindo — espere health; `./scripts/status.sh` |
| `COMPOSE_FILE` / projeto errado | `unset COMPOSE_FILE COMPOSE_PROJECT_NAME` |
| Scripts `compose: command not found` | Use scripts do lab (`_compose.sh` já encapsula) |
| `Expecting value: line 1…` no `json.tool` | Timeout agora vira JSON `erro: cliente` / `curl_exit: 28` |
| Exit codes dos scripts | `0`=2xx · `49`=409 · `42`=422 · `53`=503 · `54`=504 · `28`=timeout curl |
| Schema / coluna `request_fingerprint` missing | `docker compose down -v && ./scripts/up.sh` (rebuild da API) |

---

## Lab Postgres (`lab-timeout-postgres`, :8092)

| Sintoma | O que tentar |
|---------|----------------|
| Exp. lento não atrasa | `./scripts/provocar-lento.sh 5000` e confira `GET /admin/config` |
| Acho que Exp. 3 falhou (`matriculas=1`) | **Esperado** — unique; olhe `auditoria_tentativas > 1` (≈ e-mails) |
| Retry “não sobe auditoria” | Use **aluno novo**; hold ≥ 2× `MAX_TIME`; veja backoff nos logs |
| Hold ficou ligado | Scripts de retry agora resetam hold no `EXIT`; ou `./scripts/provocar-lento.sh 0` |
| Idempotência “não bate” | Mesma `Idempotency-Key` **e** mesmo corpo |
| 2 auditorias com a mesma chave | Corrida: dois retries sobrepostos antes do commit da chave — raro; anote e siga |
| Circuit não abre | `./scripts/provocar-erros.sh 100` + várias chamadas; **rebuild** da API se imagem antiga |
| Quero meio-aberto | Espere ~8 s **sem** `cb_reset`; depois `FAIL_RATE=0` e **uma** matrícula (1 sonda) |
| Exp. 3 “matriculas=3” | Você olhou o **total** da disciplina — use `./scripts/status.sh SD-101 aluno-exp3` |
| Exp. 4 sem replay | Script serializa + 4b; na 2ª tentativa já costuma vir `idempotent_replay` |
| Exp. 3 sem 409 | Após timeout o script zera o hold — 2ª tentativa deve ser 409 rápido |
| curl_exit 7 | API fora — `./scripts/up.sh` (não é o timeout do Exp. 2) |
| Amplificação sem diferença | Suba `N` (padrão sala=4); compare `JITTER=0` vs `1`; confira `stats.requests` |
| 422 inesperado / mismatch | Mesma `Idempotency-Key` com `aluno_id`/`disciplina_id` diferente — esperado; demo: `provar-idempotency-mismatch.sh` |
| Replay após “muito tempo” | TTL (`idem_ttl_sec`); demo: `provar-idempotency-ttl.sh`; stats `idem_expired` |
| Amplificação sem latência | Rebuild API; confira `latencia.p50_ms` / `p95_ms` em `/admin/config` |
| Deadline não aborta | Envie `DEADLINE_MS=1000` com hold > deadline; demo `provar-deadline.sh`; stats `deadline_abort` |
| CB abre com falhas velhas | Janela `cb_window_sec` (padrão 60); confira `cb_falhas_na_janela` |

---

## Lab Mongo (`lab-timeout-mongodb`, :8093)

| Sintoma | O que tentar |
|---------|----------------|
| Contagem não sobe | `./scripts/status.sh`; espere 3 s após hold |
| Upsert não deduplica | Mesmo `AVISO_ID`; `UNIQUE=1` (limpa a coleção) |
| Majority “igual” a w:1 | Esperado em **1 nó** — revisão opcional do 03 |
| pymongo timeout | Store down — `compose ps` |

---

## Checklist professor

- [ ] Postgres Exp. 1–4 OK (sem max-time → timeout → auditoria>1 → idempotente)  
- [ ] (Completo) CB + meio-aberto (1 sonda) + Exp. 6 amplificação + lab Mongo  
- [ ] Validação local preenchida  

**Validação local:**

```text
2026-08-25 — polish final —
  Exp.3: timeout→409 por aluno; Exp.4: replay no loop + 4b;
  JSON cliente com ensure_ascii=False (sem \\u2014)
```
