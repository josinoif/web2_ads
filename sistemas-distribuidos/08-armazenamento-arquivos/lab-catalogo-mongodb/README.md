# Catálogo de entregas — MongoDB + MinIO (dedup)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Módulo:** [08](../README.md) · Tutorial: [tutorial-catalogo-mongodb.md](../tutorial-catalogo-mongodb.md)

| Serviço | Porta host |
|---------|------------|
| API | **8092** |
| Mongo | **27123** |
| MinIO API / console | **9020** / **9021** |

Enfatiza: **dedup CAS na app**, refcount, catálogo atrasado (simulação), **RPO** (perda de volume + backup/restore). Download: soft verify ou **409** (`set-reject-integrity.sh`).

> **Integridade com corrupção didática (`mc pipe`):** experimento completo no [lab Postgres](../lab-entrega-postgres/) (`provar-integridade-falha.sh`). Aqui o flag só espelha soft vs 409.

```bash
./scripts/up.sh
./scripts/status.sh
```

Console MinIO: http://127.0.0.1:9021 (`minioadmin` / `minioadmin`).
