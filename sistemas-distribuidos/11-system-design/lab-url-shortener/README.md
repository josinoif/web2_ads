# Lab A — URL shortener (contador vs hash)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Módulo:** [11 — System Design](../README.md) · **Tutorial:** [tutorial-url-shortener.md](../tutorial-url-shortener.md)

**Pergunta:** na leitura, o gargalo é o hash, o banco ou o cache?

> Aproximação didática: store em memória + delay. **Não** é bit.ly de produção.

| Modo | Porta | O que sobe |
|------|-------|------------|
| Contador (INCR + base62) | `8140` | IDs sem colisão de hash |
| Hash truncado | `8141` | Colisão visível (`HASH_CHARS`) |
| Redis | `6392` | Cache do GET + sequenciador |

```bash
./scripts/up.sh
./scripts/enviar.sh contador
./scripts/enviar.sh hash
./scripts/medir-leitura.sh contador
./scripts/provar-redirect.sh contador
./scripts/provar-colisao.sh
./scripts/provar-redis-down.sh
./scripts/provar-idempotencia.sh   # opcional
```

`docker compose down -v` ao terminar. Ver [troubleshooting](../troubleshooting.md).
