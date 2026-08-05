# Exercícios Resolvidos — Bloco 4

**Tempo estimado:** 25 a 35 minutos.

Estes exercícios exigem leitura prévia do [Bloco 4 — Cultura em prática e anti-padrões](04-cultura-pratica-antipadroes.md).

---

## Exercício 1 — Reescreva frases de forma blameless

**Enunciado:**

Reescreva cada frase abaixo **em estilo blameless** — removendo foco na pessoa e destacando a causa sistêmica:

1. "O João subiu a config errada em produção."
2. "A Maria clicou em 'Deletar' no painel e apagou os dados."
3. "O time de QA esqueceu de testar o fluxo de carrinho."
4. "O Roberto (que estava de férias) era o único que sabia resolver isso."
5. "O Pedro não seguiu o runbook."

### Resolução (exemplos válidos)

| # | Original | Versão blameless |
|---|----------|------------------|
| 1 | "O João subiu a config errada em produção." | "A alteração de config para o ambiente de produção não passou por validação automática antes de entrar em vigor; a pipeline não detectou o conflito de arquivos." |
| 2 | "A Maria clicou em 'Deletar' e apagou os dados." | "O painel permitia delete de produção em um clique, sem confirmação adicional; não havia backup snapshot das últimas 24h." |
| 3 | "O time de QA esqueceu de testar o fluxo de carrinho." | "A suíte de testes automatizados não cobre o fluxo de carrinho; a validação manual dependia de memória do testador, sem checklist formal." |
| 4 | "O Roberto (de férias) era o único que sabia resolver isso." | "O conhecimento operacional do serviço de pagamento estava concentrado em uma pessoa; não havia runbook, pair rotation ou documentação adequada." |
| 5 | "O Pedro não seguiu o runbook." | "O runbook atual estava desatualizado em relação à versão do serviço; não havia mecanismo automático para detectar desvio entre documentação e sistema real." |

**Padrão**: cada versão blameless aponta para **um item de ação** (automatizar validação, adicionar confirmação, cobrir teste, documentar/distribuir conhecimento, atualizar runbook). **Pessoas não são item de ação.**

---

## Exercício 2 — Os 5 Porquês em ação

**Enunciado:**

Aplique os "5 Porquês" ao seguinte incidente hipotético da CloudStore:

> *Uma instância EC2 de produção ficou sem espaço em disco, derrubando o serviço de catálogo por 25 minutos.*

### Resolução (exemplo)

1. **Por que ficou sem espaço?** Porque os logs da aplicação enchiam o disco em ritmo muito maior que o esperado.
2. **Por que os logs enchiam tão rápido?** Porque o nível de log estava em `DEBUG` em produção.
3. **Por que estava em `DEBUG` em produção?** Porque alguém setou `DEBUG` para investigar um bug dias antes e esqueceu de reverter.
4. **Por que foi possível deixar `DEBUG` esquecido?** Porque a configuração é aplicada manualmente por SSH em cada máquina, sem versionamento ou alerta.
5. **Por que configuração é feita por SSH manual?** Porque a empresa ainda não adotou **Infrastructure as Code** para configs de runtime, e nada **monitora drift**.

**Causa-raiz sistêmica:** configs de produção são gerenciadas manualmente, sem IaC e sem monitoramento de drift.

**Ações (blameless):**

- [ ] Adotar IaC para configs de runtime (Módulo 7 da disciplina).
- [ ] Adicionar alerta quando nível de log está em `DEBUG` em produção.
- [ ] Configurar rotação/compressão de logs com retenção definida.
- [ ] Adicionar alerta de disco a 70% (não 95%) para ter tempo de reação.

Nenhuma ação menciona a pessoa que mudou o log. É o **sistema** que precisou mudar.

---

## Exercício 3 — Classificação DORA

**Enunciado:**

Classifique em **Elite / High / Medium / Low** os seguintes times hipotéticos:

| Time | DF | Lead Time | CFR | MTTR |
|------|-----|-----------|-----|-------|
| **A** | 15 deploys/dia | 2h | 4% | 45 min |
| **B** | 3 deploys/semana | 3 dias | 18% | 4h |
| **C** | 1 deploy/mês | 3 semanas | 35% | 2 dias |
| **D** | 1 deploy a cada 2 meses | 2 meses | 50% | 1 semana |

### Resolução

| Time | Classificação | Justificativa |
|------|--------------|---------------|
| **A** | **Elite** | Deploys sob demanda múltiplos por dia; LT < 1h; CFR baixo; MTTR < 1h. |
| **B** | **High** | Deploys múltiplos por semana; LT em dias; CFR na fronteira; MTTR < 1 dia. |
| **C** | **Medium/Low** | Deploys mensais, LT em semanas; CFR moderado-alto; MTTR de dias. |
| **D** | **Low** | Todos os indicadores abaixo de medium. |

**Observação:** nenhum time é "um pouco Elite". A classificação exige **todos os 4 indicadores** no patamar Elite. Muitos times têm **velocidade** (DF/LT) Elite mas **estabilidade** (CFR/MTTR) Low — o famoso "fast but broken" — e saem da classificação Elite.

**CloudStore hoje** se enquadra em **Low** nos 4 indicadores (quando medidos).

---

## Exercício 4 — Identificação de anti-padrões

**Enunciado:**

Para cada situação, identifique o anti-padrão e sugira a correção:

1. A CloudStore contratou um "DevOps Lead" que foi posto entre os times de Dev e Ops e agora "recebe pedidos de ambos os lados".
2. Um gestor anuncia em reunião: "A partir de agora fazemos postmortems blameless". Mas na primeira oportunidade, após incidente, diz em voz alta na sala: "e o João que fez o merge, hein?".
3. A CloudStore investiu R$ 2 milhões em uma plataforma K8s e vai "fazer DevOps com ela". Nenhum outro investimento em cultura ou processo foi feito.
4. A CloudStore começou a medir "deploys por dev por semana" e vincular bônus individual a esse número.

### Resolução

| # | Anti-padrão | Correção proposta |
|---|-------------|-------------------|
| 1 | **"Criar Time DevOps"** (virou silo intermediário) | Dissolver a posição de ponte; fazer Ops virar **Platform Team** que provisiona self-service; responsabilidade de runtime volta para times de produto (Dev + parte de Ops integrados). |
| 2 | **"Postmortem teatral"** | Líderes precisam **praticar o que pregam** — ou a cultura morre. Sugestão: treinar líderes em linguagem blameless, instituir facilitador externo nos postmortems iniciais, pedir que liderança admita falha própria publicamente antes de pedir ao time. |
| 3 | **"Comprar a stack mágica"** | Parar investimento em mais ferramenta; focar em cultura (daily compartilhada, postmortem blameless, on-call rotativo) e processo (CI real no Módulo 2). Ferramenta passa a ser consequência, não causa. |
| 4 | **"Métrica como meta"** (Lei de Goodhart) | Remover bônus individual atrelado a métrica técnica. Se medir DF, que seja **do time** (não individual), combinado com **CFR** (para não incentivar deploy ruim). Inspirações em DORA (sempre as 4 juntas). |

---

## Exercício 5 — Rituais para a CloudStore

**Enunciado:**

Proponha **3 rituais de curto prazo** (primeiros 30 dias de transformação) que:

- Custam pouco.
- Atacam diretamente 1 ou mais sintomas do cenário.
- Não exigem compra de ferramenta.
- Promovem colaboração Dev × Ops.

Para cada ritual, indique: o que é, com que frequência, quem participa, qual sintoma atacado.

### Resolução (exemplo)

**Ritual 1 — Daily cruzada de 15 min**

- **O que:** daily curta às 9h30, com 2 reps de Dev e 2 de Ops, sempre rotativos.
- **Pauta:** o que está em produção agora, o que vai entrar hoje/amanhã, algum alerta ou risco.
- **Frequência:** diária, 2ª a 6ª.
- **Sintomas atacados:** 1 (silos), 2 (jogar por cima do muro), 4 (bugs sem raiz), 8 (métricas — alguém passa a perguntar).

**Ritual 2 — Postmortem blameless para **todo** incidente S2 ou maior**

- **O que:** reunião de até 60 min, em até 5 dias úteis após o incidente, seguindo template (como o `gerar_postmortem.py`).
- **Quem:** respondedores + líder técnico + facilitador rotativo (cada sprint, alguém novo facilita).
- **Regra dura:** sem nomes nos enunciados de causa; sem punição de participante.
- **Frequência:** um por incidente qualificado.
- **Sintomas atacados:** 4, 6 (caça às bruxas), 10 (conhecimento concentrado vira documento público).

**Ritual 3 — "Demo de operação" quinzenal**

- **O que:** a cada 2 semanas, Ops apresenta para Dev (30 min) um tour pelos dashboards, alertas mais comuns, 1 incidente recente e o que aprendeu. Dev pergunta à vontade.
- **Frequência:** quinzenal.
- **Custo:** zero, só tempo.
- **Sintomas atacados:** 1, 2, 7 (visibilidade compartilhada), 10 (conhecimento distribui).

**Bônus — Ritual 4 (opcional): "shadow day"**

- Dev passa 1 dia observando um engenheiro de Ops de plantão. No mês seguinte, inverso.

---

## Exercício 6 — Desafiador (opcional)

**Enunciado:**

A CTO da CloudStore quer adotar o modelo Netflix integral: liberdade total, sem aprovações, "contexto, não controle", pacote salarial top 10% e keeper test. Avalie **criticamente** se esse transplante funcionaria **agora** na CloudStore.

### Resolução (exemplo)

**Não funcionaria** transplantar o modelo integral **agora**. Motivos:

1. **Pré-condições ausentes:**
   - **Densidade de talento top 10%** exige pacotes salariais que a CloudStore provavelmente não tem; sem isso, o modelo "sem regras" não produz performance, produz caos.
   - **Maturidade técnica**: Netflix tem observabilidade avançada, chaos engineering, microsserviços maduros. A CloudStore ainda está em deploy manual de sexta — dar liberdade total em produção seria perigoso.

2. **Contexto cultural:**
   - Candor radical da Netflix é culturalmente americano; em culturas organizacionais brasileiras, o feedback direto sem adaptação pode ser percebido como hostilidade e corroer confiança.
   - "Keeper Test" (demitir quem "não seria contratado hoje") destrói segurança psicológica em uma cultura que ainda não sabe fazer postmortem blameless — pode piorar, não melhorar.

3. **Mudança em ondas é mais segura:**
   - Onda 1 (imediata): rituais e cultura blameless; descentralização pequena.
   - Onda 2 (6 meses): maturidade técnica (CI/CD, observabilidade).
   - Onda 3 (12+ meses): reduzir aprovações formais em classes de mudança baixo-risco.
   - Onda 4 (24 meses): possível aproximação de "liberdade com responsabilidade", **adaptado** ao contexto.

**Princípio:** adotar **princípios** do modelo Netflix (transparência, descentralização, alta densidade de talento) é valioso. Copiar **mecânicas específicas** (keeper test, "policy-free expense reports") sem contexto adequado é **disfuncional**.

> **Leitura recomendada:** Hastings & Meyer são explícitos em *A Regra é Não Ter Regras* sobre as **pré-condições** do modelo. Eles alertam para não copiar sem considerar contexto.

---

## Próximo passo

Você concluiu os 4 blocos teóricos. Agora siga para os **[Exercícios Progressivos](../exercicios-progressivos/)** — 5 partes que aplicam tudo ao cenário da CloudStore e produzem artefatos para a entrega avaliativa.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Cultura em Prática, Anti-padrões e Introdução às Métricas DORA](04-cultura-pratica-antipadroes.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 1](../exercicios-progressivos/README.md) |

<!-- nav:end -->
