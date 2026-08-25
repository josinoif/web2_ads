# Lab C — Rate limiter (janela fixa; fail-closed vs fail-open)

**Módulo:** [11 — System Design](../README.md) · **Tutorial:** [tutorial-rate-limiter.md](../tutorial-rate-limiter.md)

**Pergunta:** Redis do limiter caiu — a API deixa passar ou responde erro?

> Contador por chave em **janela fixa** (`INCR` + TTL). **Não** é token bucket nem gateway de produção.

| Modo | Porta | Comportamento se Redis down |
|------|-------|-----------------------------|
| Fail-closed | `8160` | **503** — não atende |
| Fail-open | `8161` | **200** — deixa passar |
| Redis | `6394` | Contadores (DB 0 = closed, DB 1 = open) |

Cota ok → **200**; estourou → **429**. Ver tabela 2×2 no tutorial.

```bash
./scripts/up.sh
./scripts/provar-cota.sh closed
./scripts/provar-redis-down.sh
```

`docker compose down -v` ao terminar. Ver [troubleshooting](../troubleshooting.md).
