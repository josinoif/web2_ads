# Lab — partição Postgres + matrícula CP

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Tutorial:** [tutorial-particao-postgres.md](../tutorial-particao-postgres.md)  
**Porta API:** `8085` · Postgres host: `5436` (primary) / `5437` (réplica)

## Subir

```bash
./scripts/up.sh    # compose up + ativar-sync + verificar-modo-cp
```

Equivalente manual: `docker compose up -d --build` → `./scripts/ativar-sync.sh` → `./scripts/verificar-modo-cp.sh`.

> `sync_state` pode ser **`sync`** ou **`quorum`** (ANY 1) — ambos contam como CP ativo.

## Comandos rápidos

| Ação | Comando |
|------|---------|
| Matricular | `./scripts/matricular.sh SD-101 aluno-1` |
| Disputa última vaga | `./scripts/provocar-disputa-vaga.sh` |
| Simular partição | `./scripts/particionar.sh` |
| Curar partição | `./scripts/curar-particao.sh` |
| Status sync | `curl -s localhost:8085/consistencia/status \| python3 -m json.tool` |
| Disciplina (primary/réplica) | `curl -s 'localhost:8085/disciplinas/SD-101?dest=replica'` |

## Encerrar

```bash
docker compose down -v
```

## Redes

- `app_net` — API ↔ primary  
- `repl_net` — primary ↔ réplica; API também está aqui para `GET ?dest=replica`  
- `particionar.sh` desconecta a réplica de `repl_net` **e** encerra walsenders no primary (evita ACK fantasma)  
- sob partição: `sync_ativo=false` → `POST /matricular` **503**; `GET ?dest=replica` falha (sem DNS/rede)
