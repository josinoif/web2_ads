# Parte 4 — Quebra Controlada (1h)

**Objetivo:** Vivenciar uma falha proposital no pipeline (teste, lint ou build), interpretar os logs, corrigir o erro e refletir sobre o impacto no processo.

---

## Dinâmica

O professor (ou um colega) **introduz um erro proposital** no repositório usado na Parte 3. Os alunos devem:

1. **Interpretar os logs** do pipeline (identificar etapa que falhou e causa).
2. **Corrigir o erro** (código, teste ou configuração).
3. **Explicar o impacto da falha** no processo (feedback rápido, custo de correção, confiança no pipeline).

---

## Tipos de quebra sugeridos

### A — Teste quebrando

- Alterar **expectativa** de um teste (ex.: esperava `100`, mudar para `95` no assert) **sem** alterar o código de produção.
- Ou alterar o **código de produção** de forma que um teste existente falhe (ex.: mudar fórmula de cálculo).

**O que observar:** mensagem do test runner (AssertionError, expected vs actual), nome do arquivo e do teste. O pipeline deve falhar na etapa “Test”.

---

### B — Lint falhando

- Inserir uma **violação** que o linter detecta (ex.: variável não usada, indentação incorreta, regra de estilo).
- Ou **desativar temporariamente** uma regra e reintroduzir código que a viole.

**O que observar:** saída do linter (arquivo, linha, regra). O pipeline deve falhar na etapa “Lint”.

---

### C — Build falhando

- **Erro de sintaxe** (ex.: parêntese faltando, vírgula a mais em JSON).
- Ou **dependência inexistente** (import de módulo que não existe).

**O que observar:** mensagem do compilador ou do runtime (arquivo, linha). O pipeline deve falhar na etapa “Build” (ou na de install se for erro de dependência).

---

## Passos para o aluno

1. **Rodar o pipeline** (push ou PR) e ver a falha.
2. **Abrir os logs** da etapa que falhou e anotar:
   - Nome da etapa (Lint / Build / Test)
   - Mensagem de erro principal
   - Arquivo e linha (se houver)
3. **Corrigir** o código (ou o teste, ou a configuração) de forma que o pipeline volte a passar.
4. **Documentar** (em 3–5 linhas):
   - O que quebrou e por quê (resumo)
   - Como a falha foi detectada (onde apareceu)
   - Por que isso seria pior se fosse descoberto só em homologação ou produção

---

## Reflexão (conectar com o módulo)

- **Feedback rápido:** a falha foi detectada em minutos no CI, não dias depois em homologação.
- **Custo de correção:** corrigir no mesmo ciclo (minutos) é mais barato que corrigir em outro ambiente (horas/dias, rollback, hotfix).
- **Confiança:** o pipeline que “pegou” o erro demonstra que ele cumpre o papel de gate de qualidade.

Se quiser, relacione com as métricas do Bloco 4 (lead time, change failure rate).

---

## Próximo passo

Na **Parte 5 — Reflexão final** ([parte-5-reflexao.md](parte-5-reflexao.md)) você responde a perguntas provocativas sobre CI, automação e responsabilidade.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Construção de Pipeline CI (2h)](parte-3-pipeline-ci.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Parte 5 — Reflexão Final (30 min)](parte-5-reflexao.md) |

<!-- nav:end -->
