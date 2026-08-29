# Lab — timeout / retry / idempotência (Postgres)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Tutorial:** [tutorial-timeout-postgres.md](../tutorial-timeout-postgres.md)  
**Portas:** API `8092` · Postgres `5440`

## Subir

```bash
cd sistemas-distribuidos/06-falhas-timeout/lab-timeout-postgres
./scripts/up.sh
```

## Comandos rápidos

| Ação | Comando |
|------|---------|
| Status | `./scripts/status.sh` |
| Store lento | `./scripts/provocar-lento.sh 5000` |
| Erros injetados | `./scripts/provocar-erros.sh 80` |
| Sem `--max-time` | `NO_MAX_TIME=1 ./scripts/matricular.sh SD-101 aluno-1` |
| Timeout curto | `MAX_TIME=1 ./scripts/matricular.sh SD-101 aluno-1` |
| Retry sem chave (+ backoff) | `HOLD_MS=3000 MAX_TIME=1 ./scripts/matricular-com-retry.sh SD-101 aluno-x` |
| Retry idempotente (+ 4b) | `HOLD_MS=3000 MAX_TIME=1 ./scripts/matricular-idempotente.sh SD-101 aluno-y` |
| Status deste aluno | `./scripts/status.sh SD-101 aluno-x` |
| Comparar | `./scripts/comparar-idempotencia.sh` |
| Key + corpo diferente (422) | `./scripts/provar-idempotency-mismatch.sh` |
| TTL da Idempotency-Key | `./scripts/provar-idempotency-ttl.sh` |
| Deadline propagation | `./scripts/provar-deadline.sh` |
| Amplificação (ponte 05) | `./scripts/amplificar-carga.sh` (N=4) · `JITTER=0 …` · `N=8 …` |

**Lembrete Exp. 3:** conte **por aluno** (`matriculas=1` + `auditoria>1` **deste** aluno). Total da disciplina engana.  
**Exp. 4:** o script inclui **4b** (`idempotent_replay: true`).  
**Retry:** só timeout/503/504; **não** repete em 409/422.  
**Schema/API novos:** `docker compose down -v && ./scripts/up.sh`.

## Encerrar

```bash
docker compose down -v
```
