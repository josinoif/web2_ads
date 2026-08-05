# Exercícios Resolvidos — Bloco 1

Exercícios do Bloco 1 ([CI vs. Continuous Delivery vs. Continuous Deployment](01-ci-cd-deployment.md)). Tente **resolver antes de ler a resposta**.

---

## Exercício 1 — Classificar a maturidade

A tabela lista 4 empresas fictícias. Classifique cada uma em **CI-only**, **Continuous Delivery** ou **Continuous Deployment**.

| Empresa | Descrição |
|---------|-----------|
| **Alpha** | Pipeline roda a cada push; artefato é recompilado quando vai para staging e novamente para prod; deploy em produção é manual, agendado mensalmente. |
| **Beta** | Pipeline roda a cada push; artefato único passa por staging automaticamente; deploy em prod precisa de 1 aprovação humana e então é automático. Cerca de 4 deploys/semana. |
| **Gamma** | Cada commit verde em `main` vai para produção automaticamente, protegido por feature flag e canary. ~50 deploys/dia. |
| **Delta** | Equipe usa Git, mas não tem pipeline; testes rodam "quando alguém lembra"; deploy é 1 SRE via SSH. |

### Solução

| Empresa | Classificação | Justificativa |
|---------|----------------|---------------|
| **Alpha** | **CI** | Tem pipeline a cada push. Mas não entrega continuamente: deploy manual mensal, artefato recompilado (viola "build once"), longa lead time. Não alcança CDelivery. |
| **Beta** | **Continuous Delivery** | Artefato único promovido, ambientes encadeados, prod aprovado por humano. Decisão humana é aceitável em CDelivery — o software **está pronto**. |
| **Gamma** | **Continuous Deployment** | Cada commit verde vai automaticamente para prod, com mecanismos de segurança (flag, canary). Clássico CDeployment. |
| **Delta** | **Nem CI** | Sem pipeline; não integra continuamente. Está no "nível zero". |

**Insight:** a LogiTrack hoje se parece com a **Alpha**. A meta é chegar em **Beta** em 6 meses — e em serviços maduros (ex.: Consulta) caminhar para **Gamma** em 12 a 24 meses.

---

## Exercício 2 — Interpretar métricas DORA

Um time reporta:

- Deploys no último mês: **22**.
- Lead time mediano: **6 horas**.
- % de deploys que causaram incidente: **22%**.
- MTTR médio: **40 minutos**.

a) Qual o tier DORA em cada métrica?
b) Qual é a principal **tensão** nos resultados?
c) Qual intervenção você priorizaria?

### Solução

**a) Tiers:**

| Métrica | Valor | Tier |
|---------|-------|------|
| DF | 22/mês ≈ 0,73/dia | **High** (entre 1/dia e 1/semana) |
| LT | 6h | **High** (1 dia a 1 semana) — próximo de Elite |
| CFR | 22% | **Medium** (16-30%) |
| MTTR | 40 min | **Elite** (< 1 hora) |

**b) Tensão principal:** o time deploya **rápido** (DF/LT ≈ High) e recupera **muito rápido** (MTTR Elite), mas **falha muito** (CFR Medium). Em termos da DORA, falta **estabilidade proporcional à velocidade**.

Hipóteses comuns:

- Testes automatizados insuficientes (pirâmide invertida ou sem E2E).
- Falta de **canary** ou liberação gradual — deploys vão direto para 100%.
- Ausência de feature flags para desativar comportamento problemático sem novo deploy.

**c) Intervenção prioritária:** atacar **CFR**. Duas possibilidades:

1. **Canary** (ou feature flag % de usuários) → problemas aparecem em fração pequena antes de atingir 100%.
2. **Smoke tests mais rigorosos pós-deploy** → bloqueia promoção automaticamente se rota crítica quebrar.

O MTTR baixo é sinal de que o time **sabe** apagar fogo; o gargalo é **evitar fogo**.

---

## Exercício 3 — Diagnosticar a LogiTrack sobre DF e LT

A LogiTrack reporta:

- DF: 1 a cada 4 semanas.
- LT: 25 dias.
- CFR: 18%.
- MTTR: 90 min.

Há correlação forte entre **DF baixa** e **LT alto**? Por quê?

### Solução

Sim, correlação **causal**, não apenas estatística.

**Mecanismo:** quando DF é baixa, cada release acumula **muitas mudanças** (big-bang). Isso:

1. **Aumenta o risco** (muitas mudanças = mais superfície de bug).
2. **Aumenta o tamanho da fila** (LT sobe — um commit espera 25 dias porque a release é mensal).
3. **Reduz ainda mais DF** (releases são perigosas, então "vamos fazer menos").

É o ciclo descrito por Humble & Farley: **"se dói, faça com mais frequência"**. Lotes pequenos são **menos arriscados**, não mais arriscados — a intuição é inversa.

**Implicação para LogiTrack:** atacar **DF** **automaticamente derruba LT**. O inverso não vale: tentar "reduzir LT" sem aumentar frequência de deploy não funciona — LT é **consequência** de DF.

---

## Exercício 4 — Identificar anti-padrões

Leia cada afirmação e identifique qual **anti-padrão do Bloco 1** ela representa.

a) *"A gente faz release na última sexta do mês porque acumula as entregas."*
b) *"Staging parece produção, mas nunca reproduz o bug que acontece em produção — só aparece com o dataset real."*
c) *"A VP de Operações é quem dá o GO de deploy, mas ela não conhece a feature; só olha se tem relatório de teste."*
d) *"A gente nunca deploya sexta — então empurra tudo para a primeira segunda do mês, que vira release de 120 commits."*
e) *"A versão 3.0 tem 8 meses de mudança. Todo mundo está nervoso."*

### Solução

| Item | Anti-padrão | Explicação |
|------|-------------|------------|
| a | **Release train** | Todos empurrados para mesma janela; lentos e rápidos pagam o mesmo custo. |
| b | **Staging que mente** | Ambiente parece igual mas tem diferenças de dados/tráfego que mascaram bugs. |
| c | **Aprovação por quem não tem contexto** | Gate burocrático que não adiciona segurança real. |
| d | **Friday deploy freeze mal-entendido** | Proibir sexta sem resolver causa (deploy inseguro) só desloca o problema. |
| e | **Big-bang release** | Muitos meses de mudanças num só deploy; difícil diagnosticar falha; alto CFR previsível. |

---

## Exercício 5 — Separar deploy de release

Em CDelivery maduro, diz-se que **deploy** e **release** são **atos diferentes**. Explique a diferença e dê um exemplo concreto para a LogiTrack.

### Solução

**Deploy:** ato **técnico** de colocar código em produção. Os binários estão rodando no servidor.

**Release:** ato **de negócio/produto** de **expor** uma funcionalidade ao usuário.

**Por que separar?**

- Permite **deploy frequente** sem que cada deploy exponha features inacabadas.
- Permite **release gradual** (ativar para 5% dos clientes, depois 20%, depois 100%) **sem novo deploy**.
- Permite **kill switch**: se algo quebra, **desligar** a feature (release) sem **reverter** o código (deploy).

**Mecanismo que separa:** **feature flags** (Bloco 3).

**Exemplo LogiTrack:** a nova feature "estimativa inteligente de entrega" usa ML. O código é deployado em prod na segunda, **desligado** (flag `estimativa_ml=false`). Na terça, produto liga para **5% das transportadoras pequenas** (`estimativa_ml=true` apenas para esse segmento). Na quarta, se as métricas estão OK, liga para 30%. Na sexta, 100%.

Nenhum deploy novo entre segunda e sexta. **Release** progrediu; **deploy** foi único.

---

## Exercício 6 — Checklist de maturidade

Monte um **checklist de 8 perguntas objetivas** que permita a qualquer time se auto-avaliar em qual dos três estágios ele está (CI / CDelivery / CDeployment).

### Solução

Proposta de checklist. Cada resposta SIM conta 1 ponto.

| # | Pergunta | Se SIM, então... |
|---|----------|-------------------|
| 1 | A cada push em `main` roda um pipeline automatizado? | CI |
| 2 | O pipeline executa testes automatizados bloqueantes? | CI |
| 3 | O artefato que vai para staging é o **mesmo** que vai para produção? | CDelivery |
| 4 | Há ambientes encadeados com promoção automática até staging? | CDelivery |
| 5 | Qualquer commit em `main` pode ir para produção **hoje**, sem esperar janela? | CDelivery |
| 6 | Deploy em produção é executado por um comando único (não por checklist manual)? | CDelivery |
| 7 | Todo commit verde em `main` é deployado automaticamente em produção **sem aprovação humana**? | CDeployment |
| 8 | A decisão de "rollback" é automatizada por métricas (5xx, latência, erro de smoke)? | CDeployment |

**Leitura:**

- **0 a 2 SIM:** pré-CI. Construa pipeline básico.
- **3 a 4 SIM:** CI saudável.
- **5 a 6 SIM:** Continuous Delivery real.
- **7 a 8 SIM:** Continuous Deployment.

**Aplicando à LogiTrack:** SIM 1, SIM 2. Provavelmente NÃO em 3 (artefato recompilado), NÃO em 5 (fila mensal), NÃO em 6 (87 passos manuais). Pontuação: **2** → **pré-CDelivery**. Confirma diagnóstico do bloco.

---

## Próximo passo

- Retome o **[Bloco 1](01-ci-cd-deployment.md)** se algum exercício foi difícil.
- Siga para o **[Bloco 2 — Deployment Pipeline](../bloco-2/02-deployment-pipeline.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — CI vs. Continuous Delivery vs. Continuous Deployment](01-ci-cd-deployment.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Bloco 2 — Deployment Pipeline e Promoção de Artefatos](../bloco-2/02-deployment-pipeline.md) |

<!-- nav:end -->
