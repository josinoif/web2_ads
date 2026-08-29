# Lab A — Logs agregados (Loki)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


Gateway **:8100** · Grafana **:3100** (`admin`/`admin`) · Loki **:3101**

```bash
./scripts/up.sh
./scripts/enviar.sh aluno-01
./scripts/provar-erro.sh
./scripts/provar-log-texto.sh
./scripts/provar-ssh-vs-loki.sh
```

Tutorial: [../tutorial-logs-agregados.md](../tutorial-logs-agregados.md)
