# Parte 2 — Programa de Chaos Engineering

> **Meta.** Instalar Chaos Mesh, escrever 3 experimentos com hipóteses claras, executar pelo menos 1 como **Game Day**, e tornar chaos **contínuo** (Schedule semanal em staging).

---

## Contexto

Do PBL, achados #6 (sem chaos) e #4 (staging diverge de prod). Sem experimentação, resiliência é crença.

Pré-requisito: Parte 1 concluída; um app `pix-core` rodando em namespace `pagora` (pode ser um `nginx` com 3 replicas, `ledger` com `postgres:15-alpine`, e `redis:7-alpine` para simulação).

---

## Passo 1 — Instalar Chaos Mesh

Siga instruções do [Bloco 2](../bloco-2/02-chaos-engineering.md). Valide:

```bash
kubectl -n chaos-mesh get pods
```

Exponha dashboard:

```bash
kubectl -n chaos-mesh port-forward svc/chaos-dashboard 2333:2333 &
# http://localhost:2333
```

## Passo 2 — Baseline de observabilidade

Antes de qualquer experimento:

- Dashboard Grafana "PagoraPay SLOs" ativo (reusar do Módulo 8).
- Alertas configurados (reusar do Módulo 8).
- Canal Slack `#chaos` (fictício, documentar).

Copie `chaos_plan.py` do Bloco 2 para `scripts/`.

## Passo 3 — Experimento 1: Pod Kill em `pix-core`

Arquivo `chaos/pod-kill-pix-core.yaml`:

```yaml
apiVersion: chaos.pagora/v1
kind: Plan
metadata:
  name: pix-core-pod-kill
spec:
  hipotese: "Matar 1 de 3 replicas mantem taxa 2xx >= 99,5% e p99 <= 600ms."
  blastRadius:
    componente: pagora/pix-core
    escala: "1 replica de 3"
    janela: "5m"
  steadyState:
    - { sli: "taxa 2xx POST /pix/enviar", alvo: ">= 99,5%" }
    - { sli: "p99 latencia", alvo: "<= 600ms" }
  abort:
    - "taxa 2xx < 98% por 30s"
    - "p99 > 1200ms por 30s"
  responsavel: "seu-email@pagora.example"
  dataAprovacao: "2026-04-20"
---
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pix-core-pod-kill
  namespace: pagora
spec:
  action: pod-kill
  mode: fixed
  value: "1"
  duration: "5m"
  selector:
    namespaces: [pagora]
    labelSelectors:
      app: pix-core
```

Valide e aplique:

```bash
python scripts/chaos_plan.py chaos/pod-kill-pix-core.yaml
kubectl apply -f chaos/pod-kill-pix-core.yaml
```

Observe dashboard por 10 min. Registre em `docs/chaos/experiment-1.md`:

- Hipótese.
- Baseline (print).
- Durante o experimento (print).
- Resultado: hipótese **confirmada** / **refutada** / **inconclusiva**.
- Aprendizado e ações (se houver).

## Passo 4 — Experimento 2: NetworkChaos entre `pix-core` e `ledger`

Arquivo `chaos/network-latency.yaml`:

```yaml
apiVersion: chaos.pagora/v1
kind: Plan
metadata:
  name: pix-to-ledger-latency
spec:
  hipotese: "200ms de latencia adicional entre pix-core e ledger mantem SLO 2xx >= 99,5% devido a retry idempotente; p95 <= 700ms."
  blastRadius:
    componente: pagora/pix-core -> pagora/ledger
    escala: "100% do trafego entre os dois"
    janela: "5m"
  steadyState:
    - { sli: "taxa 2xx POST /pix/enviar", alvo: ">= 99,5%" }
    - { sli: "p95 latencia", alvo: "<= 700ms" }
    - { sli: "duplicatas em ledger", alvo: "0" }
  abort:
    - "taxa 2xx < 97% por 30s"
    - "p95 > 1500ms por 30s"
    - "qualquer duplicata detectada"
  responsavel: "seu-email@pagora.example"
  dataAprovacao: "2026-04-20"
---
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: pix-to-ledger-latency
  namespace: pagora
spec:
  action: delay
  mode: all
  selector:
    namespaces: [pagora]
    labelSelectors:
      app: pix-core
  direction: to
  target:
    mode: all
    selector:
      namespaces: [pagora]
      labelSelectors:
        app: ledger
  delay:
    latency: "200ms"
    jitter: "50ms"
  duration: "5m"
```

Rode e documente em `docs/chaos/experiment-2.md`.

## Passo 5 — Experimento 3 (Game Day): Stress CPU em node

Arquivo `chaos/stress-cpu-node.yaml` — agora como **Game Day**:

```yaml
apiVersion: chaos.pagora/v1
kind: Plan
metadata:
  name: cpu-stress-node
spec:
  hipotese: "Stress CPU em 1 node dispara HPA e mantem SLO 2xx >= 99%."
  blastRadius:
    componente: "1 node de <N>"
    escala: "80% CPU por 3 min"
    janela: "3m"
  steadyState:
    - { sli: "taxa 2xx", alvo: ">= 99%" }
    - { sli: "HPA replicas", alvo: "aumenta em 3 min" }
  abort:
    - "taxa 2xx < 95% por 30s"
  responsavel: "seu-email@pagora.example"
  dataAprovacao: "2026-04-27"
---
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: cpu-stress-node
  namespace: pagora
spec:
  mode: one
  selector:
    nodes:
      - k3d-sre-pbl-agent-0
  stressors:
    cpu:
      workers: 2
      load: 80
  duration: "3m"
```

Estrutura do Game Day em `docs/game-days/2026-04-27.md`:

- Participantes e papéis (IC, Ops, Comms, Scribe).
- Briefing (hipótese, kill switch, canais).
- Baseline (print).
- Execução: timestamps, observações, decisões.
- Debrief (o que funcionou, o que surpreendeu, ações com dono).

## Passo 6 — Chaos contínuo

`chaos/schedule-weekly.yaml`:

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: pix-core-weekly-pod-kill
  namespace: pagora
spec:
  schedule: "0 14 * * 1"      # toda segunda as 14h
  historyLimit: 10
  concurrencyPolicy: "Forbid"
  type: PodChaos
  podChaos:
    action: pod-kill
    mode: one
    duration: "3m"
    selector:
      namespaces: [pagora]
      labelSelectors:
        app: pix-core
```

Documente em `docs/chaos/README.md`: política, calendário, canal de anúncio, rule de opt-out, rollback (como parar tudo).

## Passo 7 — Makefile

```makefile
.PHONY: chaos-plan chaos-run chaos-stop

chaos-plan:
	@for f in chaos/*.yaml; do python scripts/chaos_plan.py $$f; done

chaos-run:
	kubectl apply -f chaos/$(EXPERIMENT).yaml

chaos-stop:
	kubectl delete -f chaos/$(EXPERIMENT).yaml || true
```

Uso:

```bash
make chaos-plan
make chaos-run EXPERIMENT=pod-kill-pix-core
make chaos-stop EXPERIMENT=pod-kill-pix-core
```

Commit:

```bash
git add -A && git commit -m "feat(sre-p2): chaos engineering 3 experimentos + game day + schedule"
```

---

## Entrega

- Chaos Mesh instalado e dashboard acessível.
- `chaos/` com 3 experimentos (Plan + manifesto).
- `docs/chaos/experiment-{1,2,3}.md` com hipótese, baseline, resultado, aprendizado.
- `docs/game-days/2026-04-27.md` documentando game day.
- `chaos/schedule-weekly.yaml` configurando Schedule.
- Makefile com `chaos-run` e `chaos-stop`.

## Critérios de aceitação

- [ ] Cada experimento passa `chaos_plan.py`.
- [ ] Cada experimento tem hipótese **falsificável**.
- [ ] Game day tem ata com papéis declarados e aprendizado registrado.
- [ ] Schedule em staging está ativo (`kubectl get schedule -n pagora`).
- [ ] Dashboards mostram efeito (print incluído).

## Bônus

- Adicionar `HTTPChaos` para simular 503 do provedor PIX upstream.
- Integrar o Chaos Mesh API ao pipeline CI: experimento noturno em staging.
- Usar `Workflow` para encadear experimentos (pod-kill → latency → stress).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — SLOs, Error Budget Policy e Toil Tracker](parte-1-slo-toil.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Parte 3 — Disaster Recovery real com Velero](parte-3-dr-velero.md) |

<!-- nav:end -->
