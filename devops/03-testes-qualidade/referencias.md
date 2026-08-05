# Referências Bibliográficas — Módulo 3

Material de apoio ao Módulo 3 — Testes Automatizados e Qualidade de Software.

---

## Livros centrais do módulo

### 1. Continuous Delivery (Entrega Contínua)

- **Autores:** Jez Humble, David Farley
- **Título em português:** *Entrega Contínua: como entregar software de forma confiável e rápida*
- **Arquivo de referência:** `devops/books/Entrega Contínua - Como Entregar Software de Forma Rápida e Confiável - Auto (Jez Humble).pdf`

**Uso no módulo:**

- **Capítulo 4 — Implementando uma estratégia de testes** — referência canônica da pirâmide de testes em contexto de CI/CD.
- Papel do teste automatizado como **gate** do pipeline.
- Fundamentos de testes de aceitação automatizados.

**Capítulos sugeridos:** Cap. 4 (Estratégia de testes); Cap. 8 (Testes de aceitação automatizados).

---

### 2. The DevOps Handbook

- **Autores:** Gene Kim, Jez Humble, Patrick Debois, John Willis
- **Arquivo de referência:** `devops/books/DevOps_Handbook_Intro_Part1_Part2.pdf`

**Uso no módulo:**

- Cap. 9 (*Create the Foundations of Our Deployment Pipeline*) — testes automatizados como pilar do pipeline.
- Cap. 10 (*Enable Fast and Reliable Automated Testing*) — estratégia de testes rápidos.
- Cap. 11 (*Enable and Practice Continuous Integration*) — testes no CI.

---

### 3. DevOps na Prática (Casa do Código)

- **Arquivo:** `devops/books/DevOps na Prática - Entrega de Software Confiável e Automatizada - Autor (Casa do Código).pdf`

**Uso no módulo:**

- Conteúdo em português sobre pipeline, testes automatizados em Python/Ruby.
- Exemplos práticos de integração testes + CI.

---

### 4. Métricas Ágeis

- **Arquivo:** `devops/books/Métricas ágeis - Obtenha melhores resultados em sua equipe - Autor (Casa do Código).pdf`

**Uso no módulo:**

- Discussão sobre cobertura como **métrica** — armadilhas (Lei de Goodhart).
- Métricas complementares: mutation score, defect density, escape rate.

---

## Obras complementares (recomendadas, fora da pasta `books/`)

### 5. Test-Driven Development: By Example — Kent Beck

- **Editora:** Addison-Wesley, 2002
- **Uso:** texto fundador do TDD. Caps. 1–6 são leitura obrigatória para entender Red-Green-Refactor.
- Versão em português: *TDD — Desenvolvimento Guiado por Testes* (Bookman, 2010).

### 6. Growing Object-Oriented Software, Guided by Tests — Steve Freeman & Nat Pryce

- **Editora:** Addison-Wesley, 2009
- **Uso:** evolução do TDD para projetos reais (não só katas). Origem do termo "mockist TDD".

### 7. xUnit Test Patterns — Gerard Meszaros

- **Editora:** Addison-Wesley, 2007
- **Uso:** referência definitiva de **test doubles** (dummy/stub/fake/spy/mock). Catálogo de padrões e anti-padrões.

### 8. Specification by Example — Gojko Adzic

- **Editora:** Manning, 2011
- **Uso:** BDD/ATDD em contexto organizacional. Como a especificação vira teste executável.

### 9. "Test Pyramid" — Martin Fowler

- **Link:** [martinfowler.com/bliki/TestPyramid.html](https://martinfowler.com/bliki/TestPyramid.html)
- **Uso:** formalização textual do conceito proposto originalmente por Mike Cohn (*Succeeding with Agile*, 2009).

### 10. "TestDouble" — Martin Fowler

- **Link:** [martinfowler.com/bliki/TestDouble.html](https://martinfowler.com/bliki/TestDouble.html)
- **Uso:** glossário canônico de test doubles, com diferenças entre mocks e stubs.

---

## Documentação oficial de ferramentas

### pytest

- **Site:** [docs.pytest.org](https://docs.pytest.org/)
- **Uso:** framework central dos exemplos do módulo. Veja especialmente *Fixtures*, *Parametrize*, *Markers* e *Monkeypatch*.

### Coverage.py / pytest-cov

- **Site:** [coverage.readthedocs.io](https://coverage.readthedocs.io/) e [pytest-cov.readthedocs.io](https://pytest-cov.readthedocs.io/)
- **Uso:** medição de cobertura de linhas e branches.

### Ruff

- **Site:** [docs.astral.sh/ruff](https://docs.astral.sh/ruff/)
- **Uso:** linter Python de última geração; usado nos quality gates do Bloco 3.

### Testcontainers (Python)

- **Site:** [testcontainers.com/guides/getting-started-with-testcontainers-for-python](https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/)
- **Uso:** contêineres efêmeros para testes de integração (PostgreSQL, Redis).

### pytest-bdd

- **Site:** [pytest-bdd.readthedocs.io](https://pytest-bdd.readthedocs.io/)
- **Uso:** BDD em pytest usando sintaxe Gherkin.

### Playwright for Python

- **Site:** [playwright.dev/python](https://playwright.dev/python/)
- **Uso:** E2E em navegador, estável e moderno (substituto do Selenium em muitos cenários).

### Mutation testing — `mutmut`

- **Site:** [mutmut.readthedocs.io](https://mutmut.readthedocs.io/)
- **Uso:** mede **qualidade** dos testes, não só cobertura.

---

## Como citar nas suas entregas

Exemplos aceitos na disciplina:

> Conforme Humble e Farley (2014), o teste automatizado é o mecanismo que permite integrar com frequência mantendo a qualidade.

> Fowler (2018), em *TestPyramid*, formaliza que a **proporção** entre níveis de teste importa tanto quanto a **existência** dos testes.

> Meszaros (2007), em *xUnit Test Patterns*, distingue cinco tipos de test double: dummy, stub, fake, spy e mock.

---

## Referências rápidas na web

- **Pirâmide de testes (Fowler):** [martinfowler.com/bliki/TestPyramid.html](https://martinfowler.com/bliki/TestPyramid.html)
- **Test Doubles (Fowler):** [martinfowler.com/bliki/TestDouble.html](https://martinfowler.com/bliki/TestDouble.html)
- **"Integrated Tests Are a Scam" (J.B. Rainsberger, 2011):** [blog.thecodewhisperer.com/permalink/integrated-tests-are-a-scam](https://blog.thecodewhisperer.com/permalink/integrated-tests-are-a-scam)
- **FIRST principles (Robert C. Martin):** *Clean Code*, Cap. 9 — "Clean Tests".
- **Google Testing Blog:** [testing.googleblog.com](https://testing.googleblog.com/)

---

*Use estas referências para fundamentar suas decisões na estratégia de testes da MediQuick e na entrega avaliativa.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega Avaliativa do Módulo 3](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](README.md) | **Próximo →**<br>[Módulo 4 — Entrega Contínua (Continuous Delivery)](../04-entrega-continua/README.md) |

<!-- nav:end -->
