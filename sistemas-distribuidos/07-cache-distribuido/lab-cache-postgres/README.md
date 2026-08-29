# Lab — Cache boletim (Postgres + Redis)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Módulo:** [07 — Cache distribuído](../README.md)  
**Tutorial:** [tutorial-cache-postgres.md](../tutorial-cache-postgres.md)

| Serviço | Host |
|---------|------|
| API | `http://127.0.0.1:8094` |
| Postgres | `5441` |
| Redis | `6381` |

```bash
./scripts/up.sh
./scripts/status.sh
```

Scripts: `ler.sh` · `atualizar.sh` · `benchmark.sh` · `provocar-lento.sh` · `set-invalidate.sh` · `provar-stampede.sh` · `set-jitter.sh` · `provar-redis-spof.sh` · `flush.sh`
