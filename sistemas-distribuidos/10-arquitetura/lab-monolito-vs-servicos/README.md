# Lab A — Monólito vs pipeline de serviços

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Módulo:** [10 — Arquitetura](../README.md) · **Tutorial:** [tutorial-monolito-vs-servicos.md](../tutorial-monolito-vs-servicos.md)

**Pergunta:** se a *análise* cair, o portal inteiro some — ou só o hop do meio?

> Isto é **pipeline / isolamento de processo**, não microsserviço completo (sem DB próprio nem deploy por serviço).

| Modo | Porta | O que sobe |
|------|-------|------------|
| Monólito modular | `8120` | 1 processo · arquivos `app.py` + `analise_mod.py` + `store_mod.py` |
| Pipeline | `8121` (gateway) · `8122` (análise admin) | gateway → analise → store |

```bash
./scripts/up.sh
./scripts/enviar.sh mono
./scripts/enviar.sh servicos
./scripts/provar-isolamento.sh
# opcional:
./scripts/provar-delay-borda.sh 3000
```

`docker compose down -v` ao terminar. Ver [troubleshooting](../troubleshooting.md).
