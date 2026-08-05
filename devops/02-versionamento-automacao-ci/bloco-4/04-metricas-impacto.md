# Bloco 4 — Métricas e Impacto

CI e automação não são fins em si mesmos: servem para **reduzir risco**, **acelerar entrega** e **aumentar confiabilidade**. Este bloco relaciona CI com métricas clássicas de entrega e confiabilidade, preparando o terreno para indicadores como os do DORA (módulos posteriores).

---

## 1. Por que medir?

Sem métricas, não dá para saber se as mudanças (versionamento, CI, automação) estão **melhorando** o processo. As métricas ajudam a:

- **Tomar decisões** baseadas em dados (ex.: “o lead time caiu após o CI”).
- **Comunicar** com a organização (“deploy frequency subiu”).
- **Priorizar** melhorias (ex.: focar em MTTR se incidentes demoram a ser resolvidos).

---

## 2. Métricas ligadas ao CI e à entrega

Abaixo, quatro métricas centrais. CI impacta diretamente **lead time** e **deployment frequency**, e indiretamente **change failure rate** e **MTTR**.

---

### 2.1 Lead Time

**Definição:** Tempo desde o **commit** (ou início do trabalho) até o **código estar em produção** (ou até o deploy estar disponível).

- **Sem CI:** integração manual, testes manuais, deploy manual → lead time longo e variável.
- **Com CI:** integração e testes automatizados reduzem o tempo até o código “estar pronto” para deploy; deploys automatizados podem reduzir ainda mais o lead time.

CI **reduz** o tempo gasto em integração e em “será que quebrou?” — portanto tende a **reduzir lead time**.

---

### 2.2 Deployment Frequency

**Definição:** Com que **frequência** o time faz deploy (em produção ou em ambiente relevante).

- Pipelines estáveis e rápidos permitem **deploys mais frequentes** sem aumentar risco descontrolado.
- CI garante que cada deploy parte de um build e testes conhecidos, o que facilita confiar em releases pequenas e frequentes.

---

### 2.3 Change Failure Rate

**Definição:** Proporção de **deploys que resultam em falha** (rollback, hotfix, incidente) em relação ao total de deploys.

- CI **não elimina** essa taxa (bugs podem escapar dos testes), mas tende a **reduzi-la**: menos código quebrado entra em produção quando build e testes passam antes do merge e do deploy.
- Testes automatizados e lint são “gates” que evitam parte das mudanças ruins.

---

### 2.4 MTTR (Mean Time to Restore)

**Definição:** Tempo **médio para restaurar** o serviço após uma falha (ex.: rollback, hotfix, correção).

- CI e pipeline de deploy bem definidos facilitam **rollback** (reverter para versão anterior) e **hotfix** (correção rápida + novo deploy). Assim, o MTTR pode **diminuir** quando o processo de “colocar uma correção em produção” é rápido e automatizado.

---

## 3. Resumo do impacto do CI

| Métrica | Efeito típico do CI |
|---------|----------------------|
| **Lead Time** | Redução (menos tempo em integração e validação manual). |
| **Deployment Frequency** | Aumento possível (mais confiança para fazer deploy com frequência). |
| **Change Failure Rate** | Redução (menos mudanças quebradas entram em produção). |
| **MTTR** | Redução possível (deploy e rollback mais rápidos). |

Essas quatro métricas aparecem no **DORA (DevOps Research and Assessment)** e serão aprofundadas em módulos posteriores. Aqui, o foco é **relacionar** CI com elas em nível conceitual.

---

## 4. Exemplo qualitativo (DevPay)

**Antes (cenário PBL):**

- Lead time alto (semanas em branch, integração manual, deploy manual).
- Deployment frequency baixa (release “grande” e rara).
- Change failure rate alta (bugs em homologação/produção).
- MTTR alto (corrigir e subir de novo é lento e manual).

**Depois de versionamento + CI + automação:**

- Lead time menor (branches curtas, CI rápido, integração frequente).
- Possibilidade de deployment frequency maior (releases pequenas, pipeline confiável).
- Change failure rate tende a cair (testes e lint no pipeline).
- MTTR pode cair (pipeline de deploy e rollback definidos).

---

## 5. O que o pipeline errado pode causar

Se o **pipeline estiver mal configurado** (ex.: testes não rodam, lint desatualizado, build frágil):

- **Falsos positivos** — pipeline passa com código quebrado → aumento de change failure rate.
- **Falsos negativos** — pipeline falha sem motivo real → atraso e frustração, lead time e confiança pioram.
- **Lentidão** — pipeline muito lento desincentiva o uso; o time pode fazer merge sem esperar o CI.

Por isso, manter o pipeline **correto**, **rápido** e **confiável** é parte da prática de CI.

---

## Resumo do bloco

- **Lead time**, **deployment frequency**, **change failure rate** e **MTTR** são métricas ligadas à entrega e à confiabilidade.
- **CI** tende a melhorar lead time, deployment frequency e change failure rate, e pode ajudar no MTTR (rollback/hotfix).
- Um **pipeline mal configurado** pode piorar essas métricas (falsos positivos/negativos, lentidão).

Com isso você termina a base teórica do módulo. Em seguida vêm os **exercícios progressivos** (diagnóstico, estratégia, pipeline, quebra controlada, reflexão) e a **entrega avaliativa**.

**Próximo:** [Exercícios progressivos — Parte 1](../exercicios-progressivos/parte-1-diagnostico.md)  
**Exercícios deste bloco:** [04-exercicios-resolvidos.md](04-exercicios-resolvidos.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Exercícios Resolvidos (Automação e Toil)](../bloco-3/03-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 4 — Exercícios Resolvidos (Métricas e Impacto)](04-exercicios-resolvidos.md) |

<!-- nav:end -->
