# Bloco 3 — Exercícios Resolvidos (Automação e Toil)

---

## Exercício 1 — Classificar toil

**Enunciado:** Classifique como **toil** ou **não toil** (e justifique): (a) Revisar código em Pull Request. (b) Rodar 15 comandos manualmente toda vez que sobe uma release. (c) Investigar a causa raiz de um incidente novo.

**Solução:**

| Item | Classificação | Justificativa |
|------|----------------|---------------|
| (a) Revisar código em PR | **Não toil** | Trabalho que agrega valor (qualidade, conhecimento), não é puramente repetitivo nem ideal para ser totalmente automatizado. |
| (b) 15 comandos manuais por release | **Toil** | Repetitivo, manual, escalável via script/pipeline; não agrega valor contínuo fazer a mesma sequência à mão. |
| (c) Investigar causa raiz de incidente novo | **Não toil** | Trabalho de diagnóstico, único por incidente; pode gerar automação depois (runbook), mas o ato de investigar não é toil. |

---

## Exercício 2 — Automação reativa vs estruturante

**Enunciado:** A DevPay hoje faz deploy copiando JAR por SCP e reiniciando o serviço à mão. O time criou um script que faz exatamente isso. Isso é automação reativa ou estruturante? O que seria um exemplo de automação estruturante nesse contexto?

**Solução:**

- **Script que substitui os passos manuais** = **automação reativa**: o processo já existia (deploy manual); a automação apenas replica esse processo. Reduz toil, mas o “desenho” do processo continua o mesmo.
- **Automação estruturante** seria um **pipeline de deploy** integrado ao fluxo: após o CI passar, um pipeline (ex.: GitHub Actions, GitLab CI, CodePipeline) faz build → publica artefato → dispara deploy em ambiente definido (ex.: staging/produção), com rollback possível. O processo de entrega já nasce desenhado como pipeline, não como “script que imita o que o João fazia”.

---

## Exercício 3 — Comando único “CI local”

**Enunciado:** Escreva um comando (uma linha) que, em um projeto Maven, execute na ordem: limpar, compilar, rodar testes e gerar o JAR. Qual a vantagem de rodar isso localmente antes de dar push?

**Solução:**

```bash
mvn clean verify && mvn package -DskipTests
```

Ou, se o objetivo for apenas “o que o CI faz” (incluindo testes no pacote):

```bash
mvn clean package
```

(`package` já inclui as fases anteriores, incluindo `test`.)

**Vantagem:** Se o comando passar localmente, é bem provável que o pipeline de CI também passe. Reduz falhas no CI por “esquecer de rodar os testes” e dá feedback rápido sem depender do servidor de CI.

---

## Exercício 4 — Etapa que elimina toil

**Enunciado:** Antes do CI, um desenvolvedor da DevPay rodava `npm run lint`, `npm test` e `npm run build` manualmente antes de abrir o PR. Agora o pipeline faz isso. Explique em uma frase por que isso é “eliminação de toil” no sentido SRE.

**Solução:**

O trabalho manual, repetitivo e propenso a falha (esquecer um passo ou rodar em ordem errada) foi substituído por uma execução padronizada e automática no pipeline; o esforço humano deixa de ser gasto nessa repetição e pode ser direcionado a atividades que agregam valor (design, revisão, investigação). Isso caracteriza eliminação de toil no sentido SRE.

---

## Exercício 5 — GitHub Actions vs GitLab CI

**Enunciado:** Indique uma semelhança e uma diferença entre GitHub Actions e GitLab CI do ponto de vista de quem escreve o pipeline.

**Solução (sugestão):**

- **Semelhança:** Ambos definem o pipeline em YAML no repositório (`.github/workflows/*.yml` vs `.gitlab-ci.yml`); ambos têm conceitos de jobs/stages, execução em runner, artefatos e integração com eventos (push, PR/MR).
- **Diferença:** GitHub Actions usa “workflows” e “actions” (reuso de passos); GitLab CI usa “stages” e “jobs” com `script` por job. A sintaxe e os nomes das chaves diferem (ex.: `on:` vs `only:`/`rules:`), mas a ideia (evento → jobs → passos) é equivalente.

---

**Próximo:** [Bloco 4 — Métricas e impacto](../bloco-4/04-metricas-impacto.md) e [exercícios do Bloco 4](../bloco-4/04-exercicios-resolvidos.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Automação como Redução de Toil](03-automacao-toil.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 4 — Métricas e Impacto](../bloco-4/04-metricas-impacto.md) |

<!-- nav:end -->
