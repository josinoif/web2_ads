# Lab — Escala na camada de aplicação

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Tutorial:** [tutorial-escala-aplicacao.md](../tutorial-escala-aplicacao.md)  
**Porta:** `8089` (nginx · 3 APIs) · `8091` (api1 direta) · Postgres `5439`

## Subir

```bash
docker compose up -d --build
./scripts/status.sh
```

## Endpoints

- `GET /boletim?aluno_id=aluno-1`
- `GET /escala/status`
- `POST /admin/delay` `{"ms": 80}` (por instância)
- `POST /admin/work_ms` `{"ms": 5}`
- `POST /admin/db_slots` `{"slots": 2}` (`0` = ilimitado)

## Scripts

| Script | Uso |
|--------|-----|
| `medir-rps.sh` | RPS / p50 / p99 |
| `comparar-escala.sh` | 1 API vs 3 APIs + `ganho_aprox` (`LIGHT=1` se notebook fraco) |
| `worker-lento.sh 120` | Delay só em api2 (compare p99 antes/depois) |
| `aproximar-teto.sh` | App-bound vs store-bound (`DB_SLOTS`+`STORE_HOLD`) |

**Piloto completo do módulo (app + dados → tabela Validação):** [`../scripts/piloto-validacao.sh`](../scripts/piloto-validacao.sh)

## Encerrar

```bash
docker compose down -v
```
