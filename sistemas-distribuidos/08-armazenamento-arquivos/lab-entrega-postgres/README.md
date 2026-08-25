# Entrega de trabalhos — Postgres + MinIO (2 APIs)

**Módulo:** [08](../README.md) · Tutorial: [tutorial-entrega-postgres.md](../tutorial-entrega-postgres.md)

| Serviço | Porta host |
|---------|------------|
| api1 / api2 | **8090** / **8091** |
| Postgres | **5442** |
| MinIO API / console | **9010** / **9011** |

Enfatiza: **local vs objeto**, falha parcial/órfão, **desacoplamento** (recreate da API). Download: `X-Integridade` (soft) ou **409** com `REJECT_ON_INTEGRITY_FAIL=1`.

```bash
./scripts/up.sh
./scripts/status.sh
```

Console MinIO: http://127.0.0.1:9011 (`minioadmin` / `minioadmin`).
