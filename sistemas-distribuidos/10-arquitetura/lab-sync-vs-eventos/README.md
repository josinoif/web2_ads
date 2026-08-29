# Lab B — Sync vs eventos

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Módulo:** [10 — Arquitetura](../README.md) · **Tutorial:** [tutorial-sync-vs-eventos.md](../tutorial-sync-vs-eventos.md)

**Pergunta:** se o miolo (análise/worker) estiver parado, a borda ainda aceita o envio?

> No [01](../../01-comunicacao/) você viu a fila; aqui o foco é **escolher topologia** (sync vs eventos) lado a lado. Pub/sub do notificador **não retém** eventos — notificador deve estar up antes do POST.

| Modo | Porta | Topologia |
|------|-------|-----------|
| Sync | `8130` | gateway → analise → store (espera) |
| Eventos | `8131` | gateway → Redis fila → worker (+ notificador pub/sub) |
| Redis | `6381` | fila + status + canal |

```bash
./scripts/up.sh
./scripts/enviar.sh sync
./scripts/enviar.sh eventos
./scripts/provar-acoplamento.sh
./scripts/provar-fanout.sh
```

`docker compose down -v` ao terminar.
