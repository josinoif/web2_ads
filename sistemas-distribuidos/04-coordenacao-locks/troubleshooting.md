# Troubleshooting — Coordenação e locks

**Módulo:** [04 — Coordenação/locks](README.md)

---

## Geral

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| Porta em uso (`8087`, `8088`, `5438`, …) | Lab anterior ou outro módulo | `docker compose down -v` no lab anterior; `ss -tlnp \| grep 8087` |
| `connection refused` na API | Compose ainda subindo | Aguarde health; `docker compose ps` |
| Script sem JSON formatado | Resposta não-JSON (502 nginx) | `docker compose logs api1 api2 api3` ou `logs api` |
| Overbooking **não** aparece | Modo errado ou sequencial | Use `--paralelo` e `mode=broken` / `mode=rmw` |

**Um lab por vez.** Sempre `docker compose down -v` antes de trocar de pasta.

---

## Lab Postgres (`8087`)

### Subir

```bash
cd sistemas-distribuidos/04-coordenacao-locks/lab-concorrencia-postgres
docker compose up -d --build
# Aguarde ~15–40 s (Bitnami). Poll:
for i in $(seq 1 20); do curl -sf http://localhost:8087/health && break; sleep 2; done
curl -s http://localhost:8087/health | python3 -m json.tool
```

nginx agrega **api1**, **api2**, **api3** — requisições repetidas podem cair em instâncias diferentes (veja `api_instance` na resposta).

### SD-101 já matriculada / vagas erradas

```bash
docker compose down -v && docker compose up -d --build
```

Schema inicial: SD-101 = **1 vaga**, BD-201 = 30.

### Exp. 1 (broken) não overbooka

- Confirme `?mode=broken` na URL.  
- Use `./scripts/disputa-vaga.sh --paralelo --mode broken`.  
- Verifique `RACE_DELAY_MS` (default 150 ms) — se zero, aumente no compose.  
- O modo `broken` **grava o valor stale** (`SET vagas = lido - 1`). Se o UPDATE for `vagas - 1` relativo, o `CHECK` pode abortar o segundo writer sem overbooking.

### Exp. 2 (transaction) overbooka

- Bug no código — reporte; esperado: **1×201**, **1×409**.  
- Confirme que não está usando `broken`.

### nginx 502 Bad Gateway

```bash
docker compose ps
docker compose logs api1 --tail 30
```

Postgres ainda não pronto — aguarde healthcheck.

---

## Lab Mongo + Redis (`8088`)

### Subir

```bash
cd sistemas-distribuidos/04-coordenacao-locks/lab-coordenacao-mongo
docker compose up -d --build
for i in $(seq 1 20); do curl -sf http://localhost:8088/health && break; sleep 2; done
curl -s http://localhost:8088/health | python3 -m json.tool
```

### Seed / índice

A API cria SD-101 e BD-201 no boot. Se collection vazia:

```bash
docker compose restart api
```

### Lock preso

```bash
./scripts/curar-lock.sh SD-101
# ou
docker compose exec redis redis-cli DEL lock:reserva:SD-101
```

### Exp. lock órfão

`provocar-lock-orfao.sh` imprime o curl do **terminal 2 no início**, depois bloqueia 12 s. TTL = **10 s** (não é estendido). No T2: espere **~11 s**, então reserve. Antes disso: `409 lock indisponível`. Depois: T2 `201`, holder acorda com **409** (fencing na aquisição). Observe `locks_ativos` em `/coordenacao/status`.

---

## Checklist professor (pré-aula)

- [ ] Docker Compose funciona ([00](../00-ambiente-docker/))  
- [ ] Lab Postgres: Exp. 1 overbooka, Exp. 2 não  
- [ ] Lab Mongo: rmw overbooka, atomic não  
- [ ] Portas 8087/8088 livres  
- [ ] Alunos completaram [03](../03-consistencia-cap/) (FOR UPDATE familiar)  

---

## Validação local

<!-- Preencha após piloto -->

| Campo | Valor |
|-------|-------|
| **Data** | |
| **SO / Docker** | |
| **Postgres Exp. 1–2** | |
| **Mongo Exp. 1–3** | |
| **Observações** | |

---

## Fallback sem Docker

Leia [teoria.md](teoria.md) §3–7 e [decisoes.md](decisoes.md). Desenhe timeline RMW vs `FOR UPDATE`. Objetivos 1–3 e 6–7 parcialmente atendidos sem runtime.
