# Bloco 4 — Exercícios resolvidos

> Leia [04-incidentes-escala.md](./04-incidentes-escala.md) antes.

---

## Exercício 1 — Atribuir papéis

**Enunciado.** Seu time tem 3 pessoas disponíveis para um Sev-1 em curso. Você é IC. Como distribuir os papéis? E se houver só 2 pessoas?

**Resposta.**

**Com 3 pessoas:**

- Pessoa A (você) = **IC**.
- Pessoa B = **Ops Lead** (quem conhece mais o serviço afetado).
- Pessoa C = **Comms + Scribe** (pode acumular em Sev-1 pequeno; avisar que acumula).

Se incidente escalar: chamar 4ª pessoa e separar Comms/Scribe.

**Com 2 pessoas:**

- Pessoa A (você) = **IC + Scribe** (evite digitar em terminal; só registra).
- Pessoa B = **Ops + Comms** (prioriza técnico; Comms só atualiza status page cada 20 min).

Regra: **IC nunca mexe em terminal de produção** se puder evitar. Se violar, busque ajuda já para devolver papel.

---

## Exercício 2 — Definir severidade

**Enunciado.** Classifique em Sev-1, 2, 3 ou 4:

1. `POST /pix/enviar` retornando 500 em 8% das requisições, há 3 min.
2. Dashboard de conciliação interna fora do ar há 2h.
3. Vazamento de log contendo PII de 3 usuários.
4. Latência p99 de busca por extrato subiu de 200 ms para 350 ms, estável.
5. Cluster de staging totalmente fora.

**Respostas.**

1. **Sev-1.** 8% é acima do limite; afeta produto crítico; cada minuto perde dinheiro.
2. **Sev-3.** Afeta operação interna; workaround existe (acessar DB diretamente ou esperar); sem cliente impactado.
3. **Sev-1** (ou "privacy incident" categoria paralela). Vazamento de PII **sempre** escala; LGPD dá até 72h para comunicar ANPD.
4. **Sev-4 ou não-incidente.** Não ultrapassa SLO; é "ruído" a monitorar, não incidente.
5. **Sev-3.** Staging não afeta cliente; mas bloqueia produtividade → squads de infra tratam no horário.

---

## Exercício 3 — Construir timeline

**Enunciado.** Use o `incident.csv` do bloco, rode `incident_timeline.py`, e identifique: (a) MTTA, MTTR; (b) qual fase mais demorou; (c) 1 ação concreta para reduzir MTTR em 50% no próximo incidente similar.

**Resposta esperada.**

Saída:

```
MTTA: 00:03:00  (detect 14:18 → ack 14:21)  ← se usar detect CI
        ou 00:01:30 se detect do monitor (14:19:30) → ack 14:21
MTTM: 00:37:00  (detect → mitigate 14:55)
MTTR: 00:42:00  (detect → resolve 15:00)
```

(a) MTTA ≈ 1m30s (bom, detecção automática rápida); MTTR ≈ 42 min.

(b) Fase mais longa: **ack → mitigate (33 min)**, dentro da qual a investigação consumiu 15 min (do 14:23 ack até 14:38 descoberta). Tentativas infrutíferas (`pg_cancel`) mais 9 min.

(c) Ação: **runbook pré-escrito** para "migração presa em tabela grande" com a sequência correta (`pg_terminate_backend` diretamente, ou cancelamento do pod do migrator se aplicável). Teria economizado ~15 min. Adicional: **gate DBA** em migrações DDL pesadas → preveniria o próprio evento.

---

## Exercício 4 — Postmortem blameless

**Enunciado.** Reescreva este trecho de postmortem para torná-lo blameless:

> *"O incidente foi causado porque a Alice subiu a migração sem revisar. O Bob demorou para responder porque não estava atento ao pager. Deveriam ter sido mais cuidadosos."*

**Reescrita blameless:**

> *"O incidente envolveu a execução de uma migração de schema contra uma tabela de 180 GB, com bloqueio de escrita. Fatores contribuintes:*
>
> 1. *O pipeline de CI permite push direto para produção para migrações; não há gate exigindo aprovação de DBA para operações DDL em tabelas acima de 10 GB.*
> 2. *O canary de staging executou a migração com sucesso — a tabela de staging tinha 200 MB, portanto o lock foi imperceptível e não revelou o risco.*
> 3. *O runbook para "migração em curso causando lock" não existia; o on-call de plantão não tinha sequência pré-definida para agir.*
> 4. *Os canais de comunicação estavam fragmentados — duas pessoas tentaram mitigações contraditórias nos primeiros 10 minutos.*
>
> *Ações: (a) adicionar gate DBA em CI para migrações em tabelas > 10 GB; (b) expandir ambiente de staging com cópia sampled da tabela grande; (c) criar runbook "schema lock em produção" com comandos numerados; (d) treinar time no ICS para declaração de IC clara desde o primeiro minuto."*

**Diferenças-chave:**

- Nenhum nome pessoal.
- Foco em **sistemas** (pipeline, runbook, comunicação) que permitiram o erro.
- Ações **estruturais** com dono/prazo possível — não "Alice e Bob serão mais cuidadosos".

---

## Exercício 5 — On-call saudável?

**Enunciado.** Diagnostique a saúde deste on-call e proponha 3 ajustes:

- Serviço `pix-core`, 2 pessoas no pool de on-call.
- Últimos 30 dias: engenheiro A foi paginado 18×, B foi paginado 5×.
- 40% dos pagings foram resolvidos "limpando fila de Redis" (limpeza manual).
- Nenhum game day foi feito neste ano.

**Diagnóstico:**

- **Pool insuficiente** (2 pessoas → queda de qualquer uma = pane).
- **Distribuição desigual** (A paginado 3,6× mais que B — risco de burnout de A).
- **40% de toil** em limpeza de Redis é automação esquecida.
- **Sem game day** = confiança no on-call é baseada em fé.

**Ajustes:**

1. **Pool de 4 pessoas** em rotação; turno de 1 semana; peer de backup. Evita concentração.
2. **Automatizar limpeza de Redis**: job CronJob com critério e alerta **se** a limpeza falhar; remove toil e alerta quando algo **não-esperado** acontece.
3. **Game day trimestral** a partir de agora; cenário inicial = "Redis fora" já que é recorrente; medir quanto o time conhece o sistema fora do trivial.

Bônus: investigar **por que** Redis enche — pode ser bug (TTL errado) que não precisa nem de auto-clean, apenas de correção.

---

## Exercício 6 — Tabletop

**Enunciado.** Você é facilitador de um tabletop de 45 min. Escreva o cenário inicial em 1 parágrafo e 4 "injeções" (complicações) para fazer o time pensar.

**Resposta.**

```markdown
# Tabletop: "PIX silencioso"

## Cenario inicial (5 min)
"Terca, 16:40 BRT. Voce esta no seu home office. O monitor nao disparou alerta
nenhum. Um cliente grande liga: 'nenhum PIX esta sendo recebido, desde 16:30'.
Voce checa o dashboard: nao ha 5xx, nada parece errado. Requisicoes estao
sendo processadas com 200 OK. O que voce faz no primeiro minuto?"

## Injecao 1 (12 min)
"Voce descobre: pix-core retorna 200 para todas as requisicoes, mas as mensagens
nao estao sendo gravadas em ledger. Alguem mudou o dispatcher para 'noop' em
um dry-run e esqueceu de reverter. Como voce coordena investigacao + comms?"

## Injecao 2 (22 min)
"Enquanto voce investiga, a imprensa liga para o CEO. Ele passa no telefone
para voce, agora. Voce e IC e o CEO pergunta: 'volta em quanto tempo?'. O que
voce responde?"

## Injecao 3 (30 min)
"Descoberto: a mudanca foi feita via kubectl direto em producao as 16:28 por
um membro novo do time, que achou que estava em staging. Como registrar no
postmortem sem culpar a pessoa? Que acoes estruturais propor?"

## Injecao 4 (38 min)
"BACEN percebe que PagoraPay nao esta confirmando PIX recebidos. Liga. Exige
explicacao formal em 24h. Como Comms conduz? Que template voce usa?"

## Debrief (45 min)
- O que funcionou na simulacao?
- Que runbook existiu/faltou?
- Top 3 acoes concretas (com dono).
```

**Por que essa estrutura funciona:**

- Cenário inicial é **silencioso** (SLI clássico não pega) — mostra limite de monitoramento.
- Injeção 1 força decisão técnica + processual.
- Injeção 2 força o IC a **dizer 'não sei ainda'** ao CEO — treino duro.
- Injeção 3 exercita Just Culture (culpa fácil vs. análise estrutural).
- Injeção 4 exercita compliance.

---

## Autoavaliação

- [ ] Distribuo papéis ICS (IC, Ops, Comms, Scribe) com critério.
- [ ] Classifico severidade por SLI e duração.
- [ ] Separo canais técnico, status, suporte.
- [ ] Escrevo postmortem blameless com fatores contribuintes.
- [ ] Aplico Just Culture (erro/at-risk/reckless).
- [ ] Conduzo Learning Review trimestral.
- [ ] Desenho política de on-call sustentável.
- [ ] Facilito tabletop de 45 min.
- [ ] Uso `incident_timeline.py` para MTTA/MTTM/MTTR e para identificar fase-gargalo.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Gestão de Incidentes em Escala: papéis, comunicação e aprendizado](04-incidentes-escala.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Exercícios progressivos — Módulo 10 (SRE e Operações)](../exercicios-progressivos/README.md) |

<!-- nav:end -->
