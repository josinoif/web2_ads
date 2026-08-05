# Bloco 1 — Exercícios resolvidos

> Leia primeiro [01-sre-fundamentos.md](./01-sre-fundamentos.md).

---

## Exercício 1 — Distinguir DevOps, SRE, Ops

**Enunciado.** Em 3 parágrafos curtos, diferencie DevOps, SRE e Ops tradicional para um executivo que quer entender se "deve contratar um SRE".

**Resposta.**

**Ops tradicional** é a prática de manter o sistema de pé. Valoriza estabilidade e vê mudança como risco. Funcionava bem quando software tinha ciclos longos (trimestres), mas tornou-se gargalo na era digital: o time de produtos quer lançar várias vezes ao dia; ops quer freezar.

**DevOps** é a **cultura** que derrubou o muro entre desenvolvedores e ops. Promove responsabilidade compartilhada, automação do caminho do código até produção, e métricas comuns (lead time, MTTR). DevOps é "o que"; não prescreve "como".

**SRE** é uma forma **concreta** e engenheirada de implementar DevOps. Trata confiabilidade como feature mensurável (SLO, error budget), orça tempo operacional (toil budget), e tem autoridade sobre velocidade do produto quando o orçamento de falha é consumido. Um SRE não é um "ops moderno" — é um engenheiro de software que se especializa em operação.

Para um executivo: contrate SRE quando o sistema já está em produção, tem usuários pagantes, e o time de produto já é rápido. SRE floresce onde existe pressão de velocidade **e** pressão de qualidade. Antes disso, o investimento não paga.

---

## Exercício 2 — SLO e Error Budget Policy

**Enunciado.** Proponha um SLO + Error Budget Policy para o endpoint `POST /pix/enviar` da PagoraPay, considerando o SLA regulatório do BACEN de 99,5% mensal. A policy deve ter 3 níveis com ações executáveis.

**Resposta.**

**SLO proposto**: 99,95% de sucesso (2xx / não-5xx) em `POST /pix/enviar`, janela rolante 30 dias.

**Error budget**: 100% − 99,95% = 0,05% → em 30d ≈ **21 min 36 s** de "falha permitida".

**Racional**: SLA BACEN é 99,5%; SLO interno precisa ter **folga**. 99,95% dá ~9× mais espaço para reagir antes de violar contrato regulatório. Acima de 99,99% seria caro (custo cresce exponencialmente) sem retorno proporcional.

**Error Budget Policy:**

```markdown
# EBP — PIX Envio (SLO 99,95% / 30d)

## Verde (>= 50% do budget remanescente)
- Deploys normais com canary 5/25/100% em 1h.
- Chaos experiments em prod autorizados em horario comercial.
- SRE engaja em features; tempo de engenharia 70% features, 30% confiabilidade.

## Amarelo (10-50%)
- Deploys de feature nova requerem co-aprovacao de tech lead + SRE.
- Canary estendido a 4h em 25%.
- Reuniao semanal SRE inclui "top 3 causas de queima" com owner.
- Tempo SRE passa a 50/50 entre features e confiabilidade.

## Vermelho (< 10%)
- **Freeze de features**; apenas fixes e reducoes de risco.
- CTO e SRE lead sao notificados; daily standup de 15 min sobre budget.
- Postmortems pendentes bloqueiam features.
- Reavaliacao do SLO em 30 dias se ainda em vermelho.

## Esgotado (< 0%)
- Freeze total ate recuperacao.
- Comunicacao proativa a grandes clientes (top 20).
- Postmortem formal em <=48h com acoes datadas.
- Revisao de SLO: se reiterado >= 2 meses, capacidade/arquitetura reavaliadas.
```

**Nota prática**: gatilho avaliado **diariamente** em dashboard (ver Módulo 8); ações executam automaticamente quando possível (ex.: "freeze" liga flag que bloqueia merge de PRs marcadas como feature).

---

## Exercício 3 — Toil tracking

**Enunciado.** Pegue o CSV de exemplo do bloco e rode `toil_tracker.py`. Interprete a saída: qual categoria lidera? Qual a classificação (verde/amarelo/vermelho)? Sugira 1 ação concreta para a semana seguinte.

**Resposta esperada.**

Com o CSV do bloco e budget de 20h semanais:

```
Toil (semana) - budget 20h = 1200min
categoria         minutos  horas
incidente         150      2.5h
rotacao-segredo   45       0.8h
deploy-manual     45       0.8h
conciliacao       30       0.5h
atendimento       20       0.3h
limpeza           15       0.3h

Por autor
autor  minutos  horas
alice  165      2.8h
bob    75       1.3h
carla  65       1.1h

Total: 305 min (5.1h) | Budget: 20h | Status: verde
Facilmente automatizavel: 155 min (2.6h) - candidatos prioritarios
```

Interpretação:

- **Incidente** lidera (2.5h), o que é natural; mas a segunda/terceira posições (`rotacao-segredo` e `deploy-manual`) somam ~1.5h e são **facilmente automatizáveis** — frutos baixos.
- Classificação **verde** — saudável.
- Alice tem concentração alta (2.8h); vale distribuir.

**Ação concreta semana seguinte**: automatizar rotação de segredo (ESO + Vault ou script cron). Elimina ~45 min recorrentes por período de rotação.

---

## Exercício 4 — Classificar toil ou não

**Enunciado.** Para cada item abaixo, classifique como **toil**, **não-toil** ou **depende**, com justificativa:

1. Debug de latência intermitente num serviço crítico.
2. Abrir 12 tickets por dia para renovar certificados TLS.
3. Revisar PR de colega.
4. Escrever runbook para um cenário descoberto em incidente.
5. Responder a alerta de "disco cheio" toda semana e rodar `journalctl --vacuum-size=1G`.
6. Deployar nova versão manualmente porque o CI quebrou.

**Respostas.**

1. **Não-toil.** Trabalho **de engenharia** — gera aprendizado e, se corrigido, conhecimento persistente. Torna-se toil se nunca corrigir e repetir toda semana.
2. **Toil.** Manual, repetitivo, automatizável, sem valor persistente. Automatize via ACME/cert-manager.
3. **Não-toil.** Revisão de PR é engenharia de colaboração; deixa melhoria (qualidade do código) duradoura.
4. **Não-toil.** Documentar é valor persistente. Melhor ainda se o runbook vira automação.
5. **Toil crônico.** Cria ticket: raiz é rotação de logs mal configurada. Eliminar no sistema, não na pager.
6. **Toil ou crise.** Toil se repete (CI quebra com frequência); crise se for pontual. Em todo caso, corrigir CI — deploy manual é perigoso.

Meta: classifique como **toil** o que você **faria automaticamente com orgulho**. Debug criativo não é; rotação repetida de certificado é.

---

## Exercício 5 — Capacity planning básico

**Enunciado.** Dados (hipotéticos):

- DB Postgres: CPU média no pico 78%, cresceu 2% ao mês nos últimos 6 meses.
- Saturação crítica (CPU sustained): 95%.
- Taxa de crescimento constante.

Calcule: (a) em quantos meses chega-se a 95%? (b) com headroom de 20% (alvo máximo 76%), em quanto tempo deveria agir? (c) proponha 2 ações.

**Resposta.**

(a) Distância até saturação: 95 − 78 = 17 pontos. Taxa: 2 pts/mês. **17 / 2 = 8,5 meses.**

(b) Headroom 20% (alvo 76%). Já está 2 pontos **acima** do alvo. **Ação é hoje**; a cada mês sem ação, piora.

(c) Ações possíveis:

1. **Curto prazo (1–2 sprints)**: escalar vertical (instância maior); adicionar índices ausentes em queries quentes; cache de consultas ao `ledger` via Redis com TTL curto.
2. **Médio prazo (2–3 meses)**: leitura em réplica para relatórios; revisar schema (partitioning da tabela `movimentos` por mês); offload de jobs batch para janelas de baixo tráfego.

Não faça *nada* adicional sem antes confirmar a real gargalo (I/O? lock contention? CPU de queries ruins?). USE method + pgstatstatements ajudam.

---

## Exercício 6 — Reliability como feature priorizada

**Enunciado.** Seu PM diz: "não temos sprint para esse `retry idempotente` entre `pix-core` e `ledger`, precisamos entregar a feature nova de 'agendamento de PIX'". Como SRE, como argumentar — com dados, sem dramatizar?

**Resposta.**

Argumento estruturado:

1. **Traduzir em budget**: "nos últimos 30 dias, 68% do error budget de PIX Envio foi queimado por timeout entre `pix-core` e `ledger` (evidência: dashboard X)."
2. **Mostrar a fórmula**: "a nossa EBP estabelece que abaixo de 50% de budget, features novas exigem co-aprovação SRE. Estamos em 32%. Estamos em amarelo."
3. **Propor troca concreta**: "retry idempotente cabe em 1 sprint. Ele libera ~40% do budget mensal, o que inclusive **reduz risco** do PIX Agendado — que vai pressionar o mesmo caminho."
4. **Expor custo do não-fazer**: "se entramos em vermelho, o freeze nos custa mais do que 1 sprint de retry. Vamos entregar menos."
5. **Decisão clara**: "proponho: sprint atual faz retry (SRE lidera) e PIX Agendado começa no sprint seguinte com base mais estável. Aceitável?"

**Chave:** não é briga entre "SRE vs PM". É um orçamento compartilhado, com regras pré-acordadas na EBP. Se a EBP foi aprovada por diretoria, você está chamando a regra que todos aceitaram — não impondo opinião.

---

## Autoavaliação

- [ ] Distingo DevOps de SRE com exemplos.
- [ ] Calculo error budget a partir de SLO.
- [ ] Escrevo EBP com gatilhos e ações executáveis.
- [ ] Classifico trabalho como toil usando as 6 propriedades.
- [ ] Aplico toil budget e priorizo automação com base em dado.
- [ ] Faço previsão linear simples de capacidade e defino headroom.
- [ ] Negocio prioridade com PM usando dados, não opinião.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — SRE como disciplina: economia operacional, toil, capacidade](01-sre-fundamentos.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Bloco 2 — Chaos Engineering: descobrir fragilidades antes do cliente](../bloco-2/02-chaos-engineering.md) |

<!-- nav:end -->
