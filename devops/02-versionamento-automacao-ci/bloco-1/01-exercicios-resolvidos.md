# Bloco 1 — Exercícios Resolvidos (Versionamento)

Estes exercícios fixam os conceitos de versionamento, branching e Pull Requests. **Devem ser realizados em dupla**, simulando um time de desenvolvimento.

**Importante — não alterar o repositório original:** Todo o trabalho será feito em um **fork** do repositório base. O repositório [devpay-api](https://github.com/josinoif/devpay-api) serve apenas como ponto de partida do código; **não faça push nem alterações diretamente nele**. Um integrante da dupla deve criar um fork desse repositório na **própria conta no GitHub**; a dupla clona e opera apenas nesse fork (commits, branches e PRs acontecem no fork). Resolva os exercícios praticando no fork antes de conferir a solução.

---

## Exercício 1 — Comandos Git básicos

**Enunciado:** A dupla configurou o trabalho assim: um integrante fez um **fork** do repositório [devpay-api](https://github.com/josinoif/devpay-api) na conta dele no GitHub; o outro (ou ambos) clonou o **repositório do fork** — não o original. A partir desse clone do fork, descreva os comandos para: (a) criar uma branch `feature/login`, (b) fazer um commit com a mensagem "feat: adiciona validação de email", (c) enviar a branch para o remoto do fork.

**Solução:**

```bash
# No diretório do clone do fork (ex.: cd devpay-api)
cd devpay-api

# (a) Criar e mudar para a branch feature/login
git checkout -b feature/login

# (b) Adicionar alterações e commitar
git add .
git commit -m "feat: adiciona validação de email"

# (c) Enviar a branch para o remoto do fork (primeira vez com -u)
git push -u origin feature/login
```

**Observação:** O `origin` do clone aponta para o fork (não para o repositório original). O `-u` (ou `--set-upstream`) associa a branch local à remota do fork; nos próximos `git push` não é necessário informar `origin feature/login`.

---

## Exercício 2 — Interpretar estratégia

**Enunciado:** No fork da DevPay, a dupla combina usar apenas a branch `main` e branches `feature/XXX` com vida de 1–3 dias, sempre mergeando em `main`. Qual estratégia de fluxo está mais próxima dessa escolha? Que vantagem isso traz em relação a “branch por semanas”?

**Solução:**

- Está mais próximo de **GitHub Flow** (ou Trunk-Based, se as branches forem muito curtas e o merge for várias vezes ao dia).
- **Vantagem:** integração frequente com `main`, então:
  - Conflitos tendem a ser menores e mais fáceis de resolver.
  - Bugs são descobertos mais cedo (tudo integra em `main` rápido).
  - Reduz o “risco acumulado” que Humble & Farley atribuem a branches longas.

---

## Exercício 3 — Semantic Versioning

**Enunciado:** No projeto que a dupla está versionando no fork (código da API DevPay), a API está na versão `2.3.1`. Indique o número de versão após: (a) correção de bug no cálculo de taxa; (b) nova operação “consultar saldo” mantendo compatibilidade; (c) remoção do endpoint antigo `/v1/payments`.

**Solução:**


| Mudança                                | Tipo  | Nova versão |
| -------------------------------------- | ----- | ----------- |
| (a) Correção de bug                    | PATCH | **2.3.2**   |
| (b) Nova funcionalidade compatível     | MINOR | **2.4.0**   |
| (c) Remoção de endpoint (incompatível) | MAJOR | **3.0.0**   |


---

## Exercício 4 — Conflito de merge (conceitual)

**Enunciado:** Durante o trabalho da dupla no fork, duas branches alteraram o mesmo trecho do arquivo `PaymentService.java`. Ao rodar `git merge`, o Git reporta conflito. O que a dupla deve fazer para resolver?

**Solução:**

1. **Abrir os arquivos marcados como em conflito** — o Git insere marcadores `<<<<<<<`, `=======`, `>>>>>>>`.
2. **Decidir o conteúdo final** — manter uma versão, combinar as duas ou reescrever, removendo os marcadores (a dupla pode discutir qual versão faz mais sentido).
3. **Marcar como resolvido** — `git add <arquivo>`.
4. **Concluir o merge** — `git commit` (a mensagem de merge pode ser editada). O merge fica no histórico do fork.

Exemplo de trecho em conflito:

```java
<<<<<<< HEAD
    return rate * 1.02; // taxa vigente
=======
    return rate * 1.01; // promoção
>>>>>>> feature/promocao
```

Após resolver (ex.: decidir usar a taxa 1.02 e remover os marcadores), faça `git add PaymentService.java` e `git commit`.

---

## Exercício 5 — Política de PR (PBL DevPay)

**Enunciado:** Pensando no cenário DevPay (conflitos enormes, bugs em homologação) e no fluxo que a dupla adota no fork — com Pull Requests entre branches do próprio fork —, que políticas de Pull Request a dupla deveria adotar? Justifique com base no texto do bloco.

**Solução (sugestão):**

1. **Branches curtas e PRs pequenos** — reduz tamanho dos merges e da revisão; integração mais frequente.
2. **Revisão obrigatória** — pelo menos um aprovador; melhora qualidade e compartilhamento de conhecimento.
3. **CI obrigatório no PR** — build e testes devem passar antes de permitir merge; evita que código quebrado entre na `main` e chegue à homologação.
4. **Manter `main` sempre “verde”** — quem faz merge garante que a branch está atualizada com `main` (reduz conflitos) e que o pipeline passou.

Justificativa: os problemas da DevPay (conflitos enormes, bugs em homologação) estão ligados a integração tardia e falta de feedback automático. No fork, a dupla pode praticar PRs pequenos + CI + revisão (um integra, o outro revisa), atacando exatamente isso, alinhados à ideia de Humble & Farley de “integrar frequentemente” e “feedback rápido”.

---

**Próximo:** [Bloco 2 — Integração Contínua](../bloco-2/02-integracao-continua.md) e [exercícios do Bloco 2](../bloco-2/02-exercicios-resolvidos.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Versionamento como Controle de Complexidade](01-versionamento.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 2 — Integração Contínua (CI)](../bloco-2/02-integracao-continua.md) |

<!-- nav:end -->
