# Bloco 2 — Exercícios resolvidos

> Leia [02-chaos-engineering.md](./02-chaos-engineering.md) antes.

---

## Exercício 1 — Identificar se é Chaos Engineering

**Enunciado.** Classifique cada cenário como *chaos engineering*, *teste tradicional*, ou *irresponsável*:

1. QA derruba manualmente um Pod em staging para ver o que acontece.
2. Game Day trimestral onde o on-call responde a uma falha simulada com briefing e critérios de abortar.
3. Dev faz `kubectl delete pod` em produção "para ver se vai reiniciar".
4. Pipeline de CI roda testes de carga contra `/pix/enviar` com 500 tps.
5. Semanalmente, um `Schedule` do Chaos Mesh reinicia 1 pod de `pix-core` em staging, com dashboard monitorado.

**Resposta.**

1. **Teste manual** (não-chaos). Falta hipótese e registro. Útil informalmente mas não disciplina.
2. **Chaos engineering** clássico — tem hipótese, blast radius, abort, aprendizado.
3. **Irresponsável.** Sem hipótese, sem aviso, sem controle — sabotagem.
4. **Teste de carga** (performance). Útil, mas não é chaos (não injeta falha).
5. **Chaos engineering** — automatizado, contínuo, observado. Exatamente o princípio #4 de Rosenthal.

---

## Exercício 2 — Escrever hipótese

**Enunciado.** Para PagoraPay, proponha 3 hipóteses de experimento, em formato "se X então Y deve continuar", cada uma citando SLI mensurável.

**Resposta.**

1. **Kafka consumer lag**: "Se pausamos o consumer de eventos PIX por 30 segundos, o lag sobe para < 30k mensagens, e após liberar o consumer, o lag retorna a zero em <= 2 minutos, sem perda de eventos."
2. **Redis fora**: "Se terminamos o pod Redis (sem backup em cluster), o `pix-core` degrada para idempotência via Postgres sem retornar erro ao cliente; p99 sobe no máximo 300 ms por até 60 s; SLI 2xx permanece >= 99%."
3. **Latência extra DB**: "Se injetamos 100 ms de latência em 50% das conexões Postgres do `ledger`, o p95 de `/pix/enviar` fica <= 700 ms (SLO 500 ms com headroom) e o pool de conexões não satura (utilização <= 80%)."

Cada uma refutável: eu sei **como medir** o resultado.

---

## Exercício 3 — Validar plano com `chaos_plan.py`

**Enunciado.** Escreva um plano intencionalmente **incompleto** (sem abort e sem duration) e rode `chaos_plan.py`. Depois corrija.

**Plano ruim (`chaos/bad.yaml`):**

```yaml
apiVersion: chaos.pagora/v1
kind: Plan
spec:
  hipotese: "Sistema aguenta."
  blastRadius:
    componente: pix-core
  steadyState: []
  responsavel: "alice"
---
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pix
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces: [pagora]
```

**Saída esperada:**

```
Validacao de chaos/bad.yaml
severidade  regra                   mensagem
high        ABORT-EMPTY             abort: sem criterios de parada, experimento nao e seguro.
medium      BLAST-ESCALA            blastRadius precisa do campo 'escala'
medium      BLAST-JANELA            blastRadius precisa do campo 'janela'
medium      STEADY-EMPTY            steadyState vazio: nenhum SLI para verificar.
medium      CHAOS-DURATION          Chaos sem 'duration' pode ficar preso. Adicione.
low         RESP-INVALID            responsavel deve ser um contato (email).
```

Exit code 1 (HIGH). Correções:

- Adicionar `abort: ["SLI 2xx < 98% por 30s"]`.
- Adicionar `escala: "1 replica"` e `janela: "5m"`.
- Preencher `steadyState` com 2 SLIs.
- No manifesto, adicionar `duration: "5m"`.
- `responsavel: "alice@pagora.example"`.

Re-rodar: 0 achados, exit 0.

---

## Exercício 4 — NetworkChaos de latência

**Enunciado.** Escreva um `NetworkChaos` que adiciona 200 ms de latência **apenas** nos pacotes do `pix-core` para `ledger`, por 5 minutos, no namespace `pagora`. Explique como você confirmaria se a hipótese "retry idempotente absorve bem" foi confirmada.

**Resposta.**

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: pix-to-ledger-latency-200
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

**Confirmação da hipótese** — observar 3 coisas no dashboard durante/após:

1. **SLI 2xx `/pix/enviar`** permanece ≥ 99,5% → resiliência do retry.
2. **Nenhum aumento de "transações duplicadas"** na métrica `ledger_duplicatas_total` → idempotência funcionou.
3. **p95 sobe, mas controlado** (< 700 ms conforme hipótese) — aceitável.

Se qualquer um violar: hipótese **refutada**, e você tem evidência clara (dashboard + logs) de onde ajustar (timeout, circuit breaker, backoff).

---

## Exercício 5 — Desenhar Game Day

**Enunciado.** Desenhe, em formato de agenda, um Game Day de 2h com o cenário "partição de rede entre zonas A e B do cluster que hospeda Postgres primary (A) e replica (B)".

**Resposta.**

```markdown
# Game Day: particao A-B do cluster PagoraPay

## Objetivo
Validar: hipotese "sistema degrada para operacao apenas em Zona A; detecta; alerta em <3 min; nao promove replica por engano".

## Participantes
- IC: alice (SRE lead)
- Operador hipotetico on-call: bob (dev pagamentos)
- Observador seguro: carla (platform lead, com kill switch)
- Scribe: daniel (registra timeline)

## Agenda (2h)
### 14:00-14:20 — Briefing (20 min)
- Revisar hipotese, metricas-alvo, abort criteria.
- Confirmar kill switch funcional (`kubectl delete netchaos particao-a-b`).
- Garantir canais #chaos e #game-day abertos.

### 14:20-14:30 — Baseline (10 min)
- Print do dashboard: SLI 2xx, p99, lag de replicacao, alertas ativos.
- Estado documentado no doc compartilhado.

### 14:30-15:00 — Injecao (30 min)
- 14:30 Aplicar NetworkChaos: partition entre ns zona-a e zona-b.
- Observar:
  - Replicacao Postgres: deveria parar (lag crescer).
  - Alerta "replicacao defasada" deveria disparar em <3 min.
  - `pix-core` deveria continuar operando (DB primary ativo em A).
  - Se alguem tentar failover manual → STOP.
- Bob (on-call hipotetico) executa o runbook "replica atrasada" **sem ajuda**.

### 15:00-15:15 — Recuperacao (15 min)
- Remover NetworkChaos.
- Confirmar que replicacao volta a zero lag.
- Executar runbook de pos-partition (validacao de dados).

### 15:15-16:00 — Debrief (45 min)
- O que funcionou? (alertas? runbook? comunicacao?)
- O que surpreendeu?
- Gaps do runbook → tickets.
- Ate 3 acoes com owner e prazo.

## Abortar se
- SLI 2xx < 97% por 1 min.
- Qualquer paging fora do plano.
- Confusao real no time (parar, nao virar caos de verdade).

## Resultado esperado
Ata publicada em <24h em docs/game-days/2026-04-20.md. Tickets abertos.
```

---

## Exercício 6 — Reconhecer anti-padrões

**Enunciado.** Comente cada afirmação de gestores num projeto:

1. *"Vamos rodar chaos em todas as ferramentas uma vez por mês e declarar resiliência anual."*
2. *"Não podemos rodar chaos em produção por risco."*
3. *"Se um experimento mostrou problema, é culpa de quem fez o experimento."*
4. *"Não medimos nada de observabilidade específica para chaos; é só rodar e ver."*

**Respostas.**

1. **Anti-padrão.** "Resiliência anual" não existe; mudanças introduzem regressões semanalmente. O correto é **chaos contínuo** (Schedule, CI noturno). Mensal = teatro.
2. **Parcialmente válido, parcialmente anti-padrão.** Produção total sem preparo é risco. Mas "não em prod" pode significar nunca ter certeza que ele é resiliente. Caminho: **graduar** — staging → canary 1% → 10% → completo, com observabilidade.
3. **Anti-padrão cultural.** Experimento **revelou** falha preexistente; ele não causou a falha. Culpar quem rodou estraga cultura de aprendizado e garante que ninguém mais vai propor experimento.
4. **Anti-padrão.** Sem observabilidade para chaos: dashboards dedicados, alertas de SLI, snapshots pré/pós, logs com tag do experimento, aprendizado fica raso e não-reprodutível. Antes de começar, **instrumente**.

---

## Autoavaliação

- [ ] Articulo os 4 princípios e identifico Chaos vs. "quebrar sem plano".
- [ ] Escrevo hipótese falsificável baseada em SLI.
- [ ] Uso Chaos Mesh para PodChaos e NetworkChaos.
- [ ] Valido plano com `chaos_plan.py` antes de aplicar.
- [ ] Conduzo Game Day com briefing, baseline, injeção, debrief.
- [ ] Reconheço anti-padrões de cultura (punir experimentador, "anual").
- [ ] Planejo chaos **contínuo** no ecossistema, não evento isolado.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Chaos Engineering: descobrir fragilidades antes do cliente](02-chaos-engineering.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Bloco 3 — Disaster Recovery: a capacidade que você só descobre se tem ao usar](../bloco-3/03-disaster-recovery.md) |

<!-- nav:end -->
