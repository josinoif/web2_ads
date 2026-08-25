# Troubleshooting — Arquitetura

**Módulo:** [10 — Arquitetura](README.md)

---

## Docker / daemon

| Sintoma | Ação |
|---------|------|
| `failed to connect … docker.sock` | Suba Docker Desktop; ou Podman (abaixo) |
| `permission denied … docker.sock` | Usuário fora do grupo `docker` |
| Podman rootless | Scripts usam `_compose.sh` (mesmo padrão 09); ou `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock DOCKER_CONTEXT=default` |

**Um lab por vez.** `docker compose down -v` (ou `./scripts` via compose) antes de trocar A ↔ B.

---

## Portas

| Lab | Portas |
|-----|--------|
| A — monólito | `8120` |
| A — gateway serviços | `8121` |
| A — análise (admin delay) | `8122` |
| B — sync | `8130` |
| B — eventos | `8131` |
| B — Redis | `6381` |

Se “address already in use”: `compose down -v` no lab anterior (05/09 usam outras faixas; 01 usa `8080`/`6379`).

---

## Lab A (`8120` / `8121`)

```bash
cd sistemas-distribuidos/10-arquitetura/lab-monolito-vs-servicos
./scripts/up.sh
curl -s http://127.0.0.1:8120/health | python3 -m json.tool
curl -s http://127.0.0.1:8121/health | python3 -m json.tool
```

| Sintoma | Ação |
|---------|------|
| Só monólito sobe | `compose ps`; rebuild `./scripts/up.sh` |
| Após `stop analise`, gateway 502 no POST | Esperado — health do gateway deve continuar 200 |
| Após `stop monolito`, tudo morto | Esperado — contraste com serviços |
| Delay não aparece | `./scripts/set-delay.sh 2000` ou `./scripts/provar-delay-borda.sh 3000` |
| Exp. 3 — health mono demora | Esperado — monólito = um processo; compare com gateway :8121 no script |
| “Lab A = microsserviços?” | Não — ver box no [tutorial A](tutorial-monolito-vs-servicos.md); é pipeline / isolamento de processo |

---

## Lab B (`8130` / `8131`)

```bash
cd sistemas-distribuidos/10-arquitetura/lab-sync-vs-eventos
./scripts/up.sh
```

| Sintoma | Ação |
|---------|------|
| Sync POST falha com worker/análise parado | No modo **sync**, pare `analise-sync` — borda deve falhar |
| Eventos POST ainda 202 com worker parado | Esperado — depois `compose start worker` e consulte status |
| Fan-out sem notificação | Notificador precisa estar **up antes** do POST (Redis pub/sub não retém). `compose start notificador` e rode `./scripts/provar-fanout.sh` |
| Redis connection | Porta host `6381`; dentro da rede Compose use `redis:6379` |

---

## Checklist professor (piloto)

- [x] Lab A: health monólito vs gateway com análise down  
- [x] Lab A: `provar-isolamento.sh` mostra contraste  
- [x] Lab A (opcional): `provar-delay-borda.sh` — health :8121=200 durante POST lento  
- [x] Lab B: `time` do POST sync ≫ eventos  
- [x] Lab B: fan-out (notificador) sem mudar gateway  
- [x] Aluno distingue pipeline ≠ MS no fechamento / cenário 6  

---

## Validação local

| Campo | Valor |
|-------|-------|
| **Data** | 2026-08-25 (piloto agente; monolito modular em arquivos) |
| **SO / Docker** | Linux fc44; Podman via `DOCKER_HOST=…/podman.sock` (Desktop sock ausente) |
| **Lab A — isolamento** | análise down → gw health **200**, POST **502**; monólito down → health **000**; gw intacto |
| **Lab A — delay borda** | `provar-delay-borda.sh 2000`: gw health **200** durante POST ~2,1 s; mono POST ~2,05 s |
| **Lab A — módulos** | `/health` e `/admin/config` listam `portal_mod`/`analise_mod`/`store_mod`; arquivos no config |
| **Lab B — latência** | sync POST ~2,06 s / **201**; eventos ~4 ms / **202** |
| **Lab B — acoplamento** | miolo parado: sync **502**; eventos **202** + status `na_fila` → após worker `concluido` |
| **Lab B — fan-out** | `/notificacoes` com `prova_enfileirada` + `prova_concluida` sem gateway chamar notificador |
| **Observações** | Portas 8120–8122 / 8130–8131 / 6381. Pub/sub Redis não retém. Um Compose por vez. |

---

## Fallback sem Docker

Leia [teoria.md](teoria.md) §1–9 (sumário + cola §7/§9) e [decisoes.md](decisoes.md) (incl. síntese). Desenhe monólito (3 arquivos / 1 processo) vs pipeline e sync vs fila; anote o que acontece se a análise cair em cada desenho.
