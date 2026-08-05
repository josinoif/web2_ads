# Bloco 2 — Integração Contínua (CI)

Integração Contínua (CI) é a prática de **integrar código à linha principal várias vezes ao dia**, com **build automatizado** e **testes automáticos**. Este bloco apresenta a definição clássica, os pilares (pipeline, build reprodutível, testes, feedback rápido) e exemplos práticos com GitHub Actions.

---

## 1. Definição clássica

**Integração Contínua** = integrar o código ao *mainline* (branch principal) com frequência (várias vezes ao dia), com:

- **Build automatizado** — cada integração dispara um build.
- **Testes automatizados** — o build inclui a execução de testes.
- **Feedback rápido** — o time sabe em minutos se a integração quebrou algo.

Humble & Farley estruturam a CI como **base da Entrega Contínua**: sem integração contínua, não há como ter deploy contínuo de forma segura. O pipeline de build e testes é a “linha de produção” do software.

> **Referência:** Humble, J.; Farley, D. *Entrega Contínua*. Capítulos sobre integração contínua e build e deploy.

---

## 2. Pilares conceituais


| Pilar                     | Descrição                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Pipeline automatizado** | Sequência de etapas (checkout, build, test, lint, artefato) executada automaticamente a cada push/PR. |
| **Build reprodutível**    | Mesmo código-fonte gera o mesmo resultado; ambiente controlado (versões de runtime, dependências).    |
| **Testes automatizados**  | Testes unitários e, quando possível, de integração rodam no pipeline; falha = pipeline falha.         |
| **Feedback rápido**       | Resultado em poucos minutos; quem fez o commit pode corrigir logo.                                    |


---

## 3. Pipeline de CI: etapas típicas

Um pipeline de CI costuma ter:

1. **Checkout** — obter o código do repositório na ref (branch/commit) desejada.
2. **Setup** — instalar runtime (Node, Java, Python), dependências (npm, Maven, pip).
3. **Build** — compilar/transpilar o projeto.
4. **Testes** — executar testes automatizados.
5. **Lint** — análise estática de código (estilo, boas práticas).
6. **Artefato** — gerar pacote (JAR, ZIP, imagem) para uso em etapas posteriores (ex.: deploy).

Se qualquer etapa falhar, o pipeline falha e o merge pode ser bloqueado (conforme política).

---

## 4. Como criar um pipeline no GitHub Actions

O pipeline de CI no GitHub é definido em arquivos **YAML** dentro do repositório. Esta seção descreve a estrutura do arquivo e as principais diretivas para você montar ou adaptar um `ci.yml`.

### Onde colocar o workflow

- Caminho fixo: **`.github/workflows/`**
- Nome do arquivo: qualquer um com extensão `.yml` ou `.yaml` (ex.: `ci.yml`, `test.yml`)
- Cada arquivo define um ou mais **workflows** (pipelines) que aparecem na aba *Actions* do repositório

### Estrutura geral do arquivo

Um workflow é composto por:

| Diretiva | Obrigatória? | Descrição |
| -------- | ------------ | --------- |
| `name` | Não | Nome exibido na aba Actions (ex.: "CI", "Deploy") |
| `on` | Sim | Define **quando** o pipeline roda (gatilhos) |
| `jobs` | Sim | Conjunto de **jobs**; cada job é uma unidade de execução (um “bloco” do pipeline) |

### Gatilhos (`on`)

O `on` define em quais eventos o workflow é disparado. Os mais usados em CI:

- **`push`** — ao dar push em certas branches (ex.: `branches: [main]`)
- **`pull_request`** — ao abrir ou atualizar um PR para certas branches
- **`workflow_dispatch`** — permite rodar manualmente pela interface do GitHub
- **`schedule`** — cron (ex.: todo dia à meia-noite)

Exemplo combinando push e PR:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

### Jobs e steps

Dentro de `jobs`, cada job tem um **identificador** (ex.: `build`, `test`) e contém:

| Diretiva | Descrição |
| -------- | --------- |
| `runs-on` | Sistema onde o job roda (ex.: `ubuntu-latest`, `windows-latest`) |
| `steps` | Lista de **passos** executados em ordem |
| `needs` | (Opcional) Lista de jobs que precisam terminar antes (ex.: `needs: [lint]`) |

Cada **step** pode usar:

| Diretiva | Descrição |
| -------- | --------- |
| `name` | Nome exibido no log do GitHub (recomendado para clareza) |
| `uses` | Chama uma **ação** (reutilizável), ex.: `actions/checkout@v4` |
| `run` | Comando(s) executados no shell (ex.: `npm test`) |
| `with` | Parâmetros passados para a ação usada em `uses` |
| `env` | Variáveis de ambiente para aquele step |

Exemplo de step com ação e parâmetros:

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
```

### Recursos úteis para CI

- **`actions/checkout@v4`** — faz o checkout do código do repositório no runner; quase todo workflow de CI começa com isso.
- **`actions/setup-node@v4`** — instala Node.js; use `with.node-version` e `cache: 'npm'` para versão fixa e cache de dependências.
- **`actions/setup-python@v5`** — instala Python; use `cache: 'pip'` quando aplicável.
- **`actions/setup-java@v4`** — instala JDK; use `cache: maven` ou `cache: gradle` conforme o projeto.
- **Cache** — as ações de setup costumam aceitar `cache: 'npm'`, `'pip'`, `maven`, etc., para acelerar instalação de dependências em execuções seguintes.

### Ordem de execução e paralelismo

- **Jobs sem `needs`** rodam em **paralelo**.
- Se um job declara `needs: [outro-job]`, ele só começa quando `outro-job` terminar com sucesso.
- Dentro de um job, os **steps** rodam **em sequência**; se um step falhar, os seguintes não executam e o job falha.

Assim, você pode organizar o pipeline em jobs separados (lint, build, test) para rodar em paralelo, ou em um único job com vários steps para garantir ordem (ex.: lint → build → test).

### Documentação oficial

Para consultar todas as opções e ações disponíveis: [GitHub Actions – Documentação](https://docs.github.com/en/actions).

---

## 5. Exemplo: projeto Node.js com npm

Estrutura mínima para um projeto Node com testes (ex.: Jest) e ESLint:

```text
devpay-api/
├── package.json
├── src/
│   └── index.js
├── test/
│   └── index.test.js
├── .eslintrc.js
└── .github/
    └── workflows/
        └── ci.yml
```

**package.json** (exemplo mínimo):

```json
{
  "name": "devpay-api",
  "version": "1.0.0",
  "scripts": {
    "test": "jest",
    "lint": "eslint src/",
    "build": "node -e \"console.log('Build OK')\""
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
```

**Pipeline GitHub Actions** (`.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Build
        run: npm run build

      - name: Test
        run: npm test
```

- `**npm ci**` — instala dependências a partir do `package-lock.json` (reprodutível).
- **Ordem** — lint → build → test; se lint falhar, build e test não rodam (feedback rápido).



Codigo de exemplo: [https://github.com/josinoif/devpay-api-js](https://github.com/josinoif/devpay-api-js)

---

## 6. Exemplo: projeto Python com pytest

**Estrutura:**

```text
devpay-calc/
├── requirements.txt
├── pyproject.toml
├── src/
│   └── calc.py
├── tests/
│   └── test_calc.py
└── .github/workflows/ci.yml
```

**requirements.txt:**

```text
pytest>=7.0.0
ruff>=0.1.0
```

**ci.yml (GitHub Actions):**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint (Ruff)
        run: ruff check src/

      - name: Test
        run: pytest tests/ -v
```

---

## 7. Exemplo: projeto Java com Maven

**Comandos locais equivalentes ao pipeline:**

```bash
# Build e testes (uma vez)
mvn clean verify

# Apenas testes
mvn test
```

**GitHub Actions (ci.yml):**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven

      - name: Build and test
        run: mvn clean verify -B

      - name: Package
        run: mvn package -DskipTests -B
        # Artefato em target/*.jar
```

`verify` inclui testes; `package` gera o JAR. Em cenários reais pode-se publicar o JAR como artefato do job com `actions/upload-artifact`.

---

## 8. Build reprodutível

**Reprodutibilidade** significa: mesmo código + mesmo ambiente = mesmo resultado.

Práticas:

- **Dependências fixas** — `package-lock.json` (npm), `pip freeze`/`requirements.txt` com versões, Maven com versões definidas no POM.
- **Runtime fixo no CI** — por exemplo `node-version: '20'`, `python-version: '3.11'`, `java-version: '17'`.
- **Sem “instalar última versão”** — evitar `npm install lodash` sem lockfile ou `pip install pytest` sem fixar versão em CI.

Isso reduz “na minha máquina funciona” e facilita investigar falhas.

---

## 9. Feedback rápido

- **Tempo de pipeline** — idealmente alguns minutos; se passar de ~10 min, o time tende a não esperar e pode fazer merge sem CI verde.
- **Falhar cedo** — lint e build antes de testes longos; assim um erro de sintaxe ou de compilação aparece em 1–2 min.
- **Paralelização** — jobs independentes (ex.: lint e test) podem rodar em paralelo para reduzir tempo total.

---

## 10. CI e risco

- **Sem CI:** bugs e quebras aparecem na homologação ou em produção; correção cara e estresse.
- **Com CI:** quebra detectada no commit/PR; correção no mesmo ciclo, custo menor.

Isso se conecta ao cenário DevPay: “bugs só aparecem em homologação” é exatamente o que a CI pretende evitar, trazendo o feedback para o momento do desenvolvimento.

---

## Referências

### Livros

- **Humble, J.; Farley, D.** *Entrega Contínua: entrega de software confiável por meio de build, teste e implantação automatizados*. Rio de Janeiro: Alta Books (ou ed. em inglês: *Continuous Delivery*, Addison-Wesley).  
  Capítulos mais relacionados a CI: integração contínua; build e deploy; testes automatizados; gerenciamento de dependências e configuração.

- **Forsgren, N.; Humble, J.; Kim, G.** *Acelerar: a ciência do DevOps*. São Paulo: Editora Évora (ou *Accelerate*, IT Revolution).  
  Capítulos sobre práticas técnicas (CI, deploy frequente) e métricas de desempenho; fundamentação em pesquisa para as práticas de CI/CD.

- **Freeman, S.; Pryce, N.** *Desenvolvimento orientado a testes*. Porto Alegre: Bookman (ou *Growing Object-Oriented Software, Guided by Tests*, Addison-Wesley).  
  Capítulos sobre testes automatizados e ciclo TDD; complementa o uso de testes no pipeline de CI.

### Artigos e sites

- **Fowler, M.** *Continuous Integration* (2006). Disponível em: [martinfowler.com/articles/continuousIntegration.html](https://martinfowler.com/articles/continuousIntegration.html).  
  Definição clássica de CI, práticas e checklist; referência muito citada.

- **GitHub.** *Documentação do GitHub Actions*. Disponível em: [docs.github.com/en/actions](https://docs.github.com/en/actions).  
  Referência oficial para workflows, sintaxe do YAML, ações built-in e do marketplace.

- **Duvall, P. M. et al.** *Continuous Integration: Improving Software Quality and Reducing Risk*. Addison-Wesley (livro da série Martin Fowler).  
  Foco em implementação de CI; capítulos sobre build, testes, feedback e boas práticas no pipeline.

### Aprofundamento

Para ir além do conteúdo do bloco: leia os capítulos de integração contínua e build em *Entrega Contínua* (Humble & Farley) e o artigo do Fowler; use a documentação do GitHub Actions para montar e ajustar seu `ci.yml`.

---

## Resumo do bloco

- **CI** = integrar frequentemente ao mainline com build e testes automatizados.
- **Pipeline** = checkout → setup → lint → build → test → (opcional) artefato.
- **Build reprodutível** = dependências e runtime controlados.
- **Feedback rápido** = pipeline em poucos minutos e falhar cedo.

No próximo bloco: **Automação como redução de toil** (SRE) e como CI se encaixa nessa visão.

**Próximo:** [Bloco 3 — Automação como redução de toil](../bloco-3/03-automacao-toil.md)  
**Exercícios deste bloco:** [02-exercicios-resolvidos.md](02-exercicios-resolvidos.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Exercícios Resolvidos (Versionamento)](../bloco-1/01-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 2 — Exercícios Resolvidos (Integração Contínua)](02-exercicios-resolvidos.md) |

<!-- nav:end -->
