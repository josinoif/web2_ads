# Bloco 2 — Exercícios Resolvidos (Integração Contínua)

---

## Exercício 1 — Ordem das etapas

**Enunciado:** Por que faz sentido rodar **lint** antes de **testes** no pipeline?

**Solução:**

- **Lint** é rápido e detecta erros de sintaxe e estilo.
- Se o código nem passa no lint, **testes podem falhar por motivo errado** (ex.: erro de sintaxe) ou nem rodar direito.
- **Falhar cedo** economiza tempo: em 30 segundos você sabe que há problema, em vez de esperar vários minutos de testes para falhar no primeiro arquivo com erro.

---

## Exercício 2 — Interpretar falha de pipeline

**Enunciado:** O pipeline falhou na etapa "Test". O log mostra: `AssertionError: expected 100, got 95`. O que isso indica? Onde o desenvolvedor deve atuar?

**Solução:**

- Indica que **um teste automatizado falhou**: o valor esperado era `100` e o obtido foi `95`.
- O desenvolvedor deve:
  1. **Localizar o teste** que falhou (nome do arquivo e teste no log).
  2. **Decidir** se o código está errado (corrigir a lógica para retornar 100) ou se a expectativa do teste está desatualizada (corrigir o teste para 95, se for o novo comportamento correto).
  3. Corrigir, commitar e deixar o pipeline passar antes de fazer merge.

---

## Exercício 3 — npm ci vs npm install

**Enunciado:** No CI, por que usar `npm ci` em vez de `npm install`?

**Solução:**

- **`npm ci`** usa **apenas** o `package-lock.json`, não altera o lockfile e remove `node_modules` antes de instalar → **instalação determinística**.
- **`npm install`** pode atualizar o lockfile e instalar versões diferentes em diferentes ambientes → risco de “na minha máquina funciona”.
- No CI queremos **reprodutibilidade**: mesma árvore de dependências a cada run. Por isso `npm ci` é a recomendação para pipelines.

---

## Exercício 4 — Escrever um passo de pipeline

**Enunciado:** Adicione um passo ao pipeline Node que **gere um artefato** (arquivo ZIP do diretório `dist/`) e o disponibilize como artefato do job no GitHub Actions. Considere que o `npm run build` já gera `dist/`.

**Solução:**

No mesmo job, após o passo "Test", adicionar:

```yaml
      - name: Build production bundle
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist-zip
          path: dist/
```

Se quiser realmente um ZIP (e o `path` aceitar diretório, o Actions já empacota), o acima basta. Para gerar um ZIP explícito:

```yaml
      - name: Create ZIP
        run: zip -r dist.zip dist/

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist-zip
          path: dist.zip
```

---

## Exercício 5 — Conexão com o cenário DevPay (PBL)

**Enunciado:** “Bugs só aparecem no ambiente de homologação.” Como a introdução de um pipeline de CI ajuda a DevPay nesse problema?

**Solução:**

- **Antes:** código era integrado e só testado de fato em homologação; bugs descobertos tarde.
- **Com CI:** a cada push/PR o pipeline roda **build + testes** no ambiente do CI. Falhas são detectadas **antes** do merge e antes de subir para homologação.
- Assim, só sobe para homologação código que **já passou** em build e testes automatizados. Isso não elimina 100% dos bugs (há cenários que só aparecem em homolog/produção), mas **reduz muito** os que são capturáveis por testes automatizados e **aumenta a previsibilidade** das entregas.

---

**Próximo:** [Bloco 3 — Automação como redução de toil](../bloco-3/03-automacao-toil.md) e [exercícios do Bloco 3](../bloco-3/03-exercicios-resolvidos.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Integração Contínua (CI)](02-integracao-continua.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 3 — Automação como Redução de Toil](../bloco-3/03-automacao-toil.md) |

<!-- nav:end -->
