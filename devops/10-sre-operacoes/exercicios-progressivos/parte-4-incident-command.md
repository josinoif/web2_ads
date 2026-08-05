# Parte 4 — Incident Command System + Tabletop

> **Meta.** Estabelecer o processo humano para incidentes: papéis, severidades, canais, comunicação, runbooks vivos. Exercitar com tabletop.

---

## Contexto

Do PBL, achados #7 (sem comando), #8 (comunicação caótica), #2 (runbooks mortos). Agora vamos costurar a operação humana.

---

## Passo 1 — `docs/incident-command.md`

Escreva documento com:

1. **Visão geral** e quando adotar (Sev-1, Sev-2).
2. **Papéis** com responsabilidades e limites:
   - IC, Ops Lead, Comms Lead, Scribe.
   - Regra: IC não digita no terminal.
3. **Severidades** — tabela com critérios objetivos (SLI, duração).
4. **Canais** — técnico, status, suporte.
5. **Fluxo de incidente**:
   - Declaração (quem, como).
   - Paging automático (quem é acordado).
   - Canal `#incident-YYYYMMDD-<slug>` criado automaticamente (documentar mesmo se manual).
   - Status page atualizada a cada 15-30 min.
   - Encerramento (critério).
6. **Pós-incidente** — postmortem obrigatório para Sev-1/2 em até 72h.

Use [Bloco 4](../bloco-4/04-incidentes-escala.md) como base e adapte ao contexto PagoraPay.

## Passo 2 — Runbooks vivos

Crie (ou atualize) `docs/runbooks/` com **pelo menos 5** runbooks, cada um com:

- Cenário + pré-condições.
- Passos numerados com comando e output esperado.
- Critério de sucesso objetivo.
- Plano B.
- "Última execução".

Sugestões (use o cenário):

| Arquivo | Cenário |
|---------|---------|
| `runbooks/pix-latencia-alta.md` | p95 de `/pix/enviar` > 1 s |
| `runbooks/ledger-db-lock.md` | DB com query bloqueando > 60s |
| `runbooks/redis-full.md` | Redis > 90% memória |
| `runbooks/kafka-lag.md` | consumer lag > 30k |
| `runbooks/dr-cluster-lost.md` | (já feita na Parte 3) |

## Passo 3 — Tabletop

Conduza (mesmo sozinho, "escrevendo o que cada papel faria") um **tabletop de 45 min** com o cenário da escolha. Sugestão: reuse o Exercício 6 do Bloco 4 ("PIX silencioso").

Registre em `docs/tabletops/2026-05-XX.md`:

- **Cenário inicial** (1 parágrafo).
- **Participantes** e papéis.
- **Timeline** (injeções do facilitador + respostas).
- **Aprendizado**: o que funcionou, o que faltou, top 3 ações com dono.

Exemplo:

```markdown
# Tabletop: PIX silencioso - 2026-05-15

## Cenario
Sexta 16:40, cliente liga relatando que nenhum PIX recebido desde 16:30.
Dashboards nao alertam (tudo 200 OK, mas mensagens nao gravam em ledger).

## Participantes
- IC: voce
- Ops Lead: Bob (simulado)
- Comms Lead: Carla (simulada)
- Scribe: Daniel (simulado)
- Facilitador: Alice

## Timeline
16:40 - Alice injeta cenario.
16:41 - IC declara Sev-2 (aguardando confirmacao de impacto).
16:43 - Ops identifica logs: dispatcher em modo 'noop'.
16:44 - Comms posta em status page "investigando".
16:48 - Ops reverte config, servico retoma.
16:50 - Alice injeta: "CEO liga pedindo tempo de volta".
  IC responde: "Servico ja voltou, estimado impacto 20 min...".
16:55 - Alice injeta: "BACEN liga".
  Comms usa template "comunicacao-regulada".
17:10 - Debrief.

## Aprendizado
- Faltava alerta para "mensagens gravadas em ledger" (metric gap).
- Template BACEN esta no wiki, mas Comms levou 3 min para achar.
- Papel Scribe foi essencial: timeline saiu pronta.

## Top 3 acoes
| Acao | Dono | Prazo |
|------|------|-------|
| Adicionar metrica ledger_writes_total + alerta | Alice | 2026-05-22 |
| Mover templates de comunicacao regulada para repo runbooks/ | Carla | 2026-05-20 |
| Incluir treino "injecao silenciosa" no proximo tabletop | IC | 2026-06-01 |
```

## Passo 4 — Simulação de incidente real com `incident_timeline.py`

Use o `incident_timeline.py` (copie do Bloco 4 para `scripts/`) para montar uma timeline fictícia do incidente de 09/03 (do PBL) ou do tabletop. Arquivo `data/incident-20260309.csv`:

```csv
timestamp,ator,fase,evento
2026-03-09T14:18:00,CI,detect,deploy com migracao inicia
2026-03-09T14:19:30,monitor,detect,alerta p99 dispara
2026-03-09T14:23:00,bob,ack,on-call reconhece
2026-03-09T14:38:00,alice,investigate,CTO chama dev da migracao
2026-03-09T14:46:00,dev,investigate,pg_cancel_backend sem efeito
2026-03-09T14:55:00,bob,mitigate,pg_terminate_backend executado
2026-03-09T15:00:00,monitor,resolve,SLI volta ao normal
```

```bash
python scripts/incident_timeline.py data/incident-20260309.csv
```

Cole saída em `docs/postmortems/ph-2026-03-09.md` (já preparando para Parte 5).

## Passo 5 — Makefile

```makefile
.PHONY: tabletop incident-timeline

tabletop:
	@echo "Consulte docs/tabletops/. Proximo em <data>."

incident-timeline:
	python scripts/incident_timeline.py $(CSV)
```

Uso: `make incident-timeline CSV=data/incident-20260309.csv`.

Commit:

```bash
git add -A && git commit -m "feat(sre-p4): incident command + runbooks vivos + tabletop + timeline"
```

---

## Entrega

- `docs/incident-command.md` completo.
- `docs/runbooks/` com 5+ runbooks com critério de sucesso.
- `docs/tabletops/<data>.md` com ata do tabletop.
- `data/incident-20260309.csv` + saída do `incident_timeline.py`.
- Makefile com `incident-timeline`.

## Critérios de aceitação

- [ ] Documento de IC cita papéis, severidades, canais, encerramento.
- [ ] 5 runbooks com comando + output + critério.
- [ ] Tabletop tem ata com papéis, injeções, aprendizado, top-3 ações.
- [ ] `incident_timeline.py` roda e identifica MTTA/MTTM/MTTR.
- [ ] Ao menos 3 dos runbooks têm "Última execução" preenchida.

## Bônus

- Criar bot Slack que cria canal automático `#incident-YYYYMMDD-<slug>` ao disparar slash command `/incident declare`.
- Template Jira/GitHub Issue para "declaração de incidente" com campos obrigatórios.
- Integração com PagerDuty (trial) para rotação real.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Disaster Recovery real com Velero](parte-3-dr-velero.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Parte 5 — Postmortem Blameless e Learning Review](parte-5-postmortem-learning.md) |

<!-- nav:end -->
