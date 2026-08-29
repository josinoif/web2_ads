# Lab B — News feed: fan-out on write vs on read

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Módulo:** [11 — System Design](../README.md) · **Tutorial:** [tutorial-feed-fanout.md](../tutorial-feed-fanout.md)

**Pergunta:** o que quebra quando 1 celebridade posta para N seguidores?

> Aproximação didática: Redis + delay por seguidor/followee. **Não** é Twitter (sem ranking, sem Kafka).

| Modo | Porta | O que sobe |
|------|-------|------------|
| Fan-out on write | `8150` | POST preenche inbox (inline ou worker) |
| Fan-out on read | `8151` | GET junta `following` |
| Redis | `6393` | DB 0 = write; DB 1 = read |
| Worker | — | Só a fila do write (`fanout_q`) |

```bash
./scripts/up.sh
./scripts/seed.sh
./scripts/provar-celebridade.sh
./scripts/provar-leitura.sh
./scripts/provar-worker.sh
```

`docker compose down -v` ao terminar. Ver [troubleshooting](../troubleshooting.md).
