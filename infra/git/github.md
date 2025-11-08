## GitHub na prática: vantagens, funcionalidades e um mini-projeto com CI/CD

Este material ensina como usar GitHub para elevar a qualidade e a velocidade do desenvolvimento: colaboração (PRs, revisão), governança (branch protection, CODEOWNERS), automação (Actions/CI), segurança (Dependabot/CodeQL) e releases. Traz também um mini-projeto funcional para exercitar tudo isso.

---

## 1) Por que usar GitHub?

Vantagens competitivas no mercado:

- Efeito de rede e ecossistema: integração nativa com Actions, Packages, Pages, Projects, Codespaces, Copilot; marketplace vasto.
- Fluxos de colaboração maduros: Pull Requests, revisão, regras de proteção, required checks, aprovação por áreas (CODEOWNERS).
- Automação ponta a ponta: build, testes, lint, scan de segurança, release por tag, publicação de pacotes/imagens.
- Segurança e compliance: secret scanning, Dependabot, CodeQL, ambientes com aprovação, audit logs (em planos enterprise).
- Produtividade: templates, actions reusáveis, badges, insights de PRs, Projects (kanban/roadmap), Discussions e Wiki.

---

## 2) Funcionalidades-chave e como isso melhora o processo

- Repositórios e Branch Protection Rules
	- Bloqueiam push direto em `main`, exigem revisões, status checks (CI verde), políticas de merge (squash/merge/rebase) e assinaturas.
	- Benefício: qualidade consistente e histórico limpo.

- Pull Requests e Code Review
	- Conversa centralizada, diffs por commit/arquivo, sugestões em linha, drafts, required reviewers e CODEOWNERS.
	- Benefício: conhecimento compartilhado e menos bugs em produção.

- GitHub Actions (CI/CD)
	- Workflows em YAML gatilhados por push/PR/tag/schedule; runners hospedados ou self-hosted; cache/matriz/artefatos.
	- Benefício: automação confiável do ciclo build→test→release.

- Releases, Tags e Packages (GHCR)
	- Gere releases por tag (SemVer), publique artefatos e imagens Docker no GitHub Container Registry.
	- Benefício: distribuição previsível e versionada.

- Issues, Projects e Templates
	- Issues com templates (bug/feature), Projects estilo kanban/roadmap, milestones, labels e automações.
	- Benefício: organização e previsibilidade do trabalho.

- Segurança
	- Dependabot (updates e alerts), CodeQL (análise estática), secret scanning, security advisories e SECURITY.md.
	- Benefício: redução de riscos e resposta rápida a vulnerabilidades.

- Colaboração avançada
	- CODEOWNERS (aprovação por área), Discussions/Wiki para conhecimento, Pages para docs estáticas, Codespaces para dev em nuvem.

---

## 3) Mini-projeto demo (Node.js + Express) com CI/CD

Incluímos um projeto exemplo em `infra/git/demo-github-app/` com:

- API simples (Express): rotas `/health`, `/sum`, `/echo`.
- Testes com o runner nativo do Node (`node --test`) + `supertest`.
- Lint com ESLint e build com esbuild (gera `dist/`).
- Workflows GitHub Actions de CI (testes/lint/build) e Release (por tag).
- Governança e segurança: templates de PR/issue, CODEOWNERS, SECURITY.md, Dependabot e CodeQL.

Estrutura resumida:

```
infra/git/demo-github-app/
	src/app.js, src/index.js
	tests/app.test.js
	package.json, .eslintrc.json, .gitignore
	.github/
		workflows/ci.yml, workflows/release.yml, workflows/codeql.yml
		dependabot.yml
		ISSUE_TEMPLATE/bug_report.md, feature_request.md
		pull_request_template.md, CODEOWNERS
	SECURITY.md, README.md
```

Como rodar localmente (Linux/Bash):

```bash
cd infra/git/demo-github-app
npm ci
npm test
npm run lint
npm run build
npm run dev   # inicia o servidor em modo simples (porta 3000)
```

---

## 4) CI: pipeline de build, testes e artefatos

O workflow `ci.yml` (em `.github/workflows/`) faz:

- Matriz de Node (18 e 20).
- Cache do npm por lockfile.
- Passos: checkout → setup-node → npm ci → lint → test → build → upload de artefatos (`dist/`).

Você verá os checks no PR (required checks podem ser exigidos via Branch Protection) e poderá baixar artefatos na aba “Actions”.

Para usar este demo como raiz de um novo repositório, mova a pasta para o topo do repo e mantenha o `.github/` no nível raiz.

---

## 5) Releases e versionamento

- Use SemVer: `vMAJOR.MINOR.PATCH` (ex.: `v0.1.0`).
- Ao dar push de uma tag, o workflow `release.yml` faz build e cria a release com os arquivos de `dist/`.

Exemplo:

```bash
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

---

## 6) Governança: CODEOWNERS, templates e branch protection

- `CODEOWNERS`: exige aprovação automática de responsáveis por pastas/arquivos.
- Templates de PR/issue: padronizam o que avaliar e como reportar.
- Branch protection: configure em Settings → Branches (exigir reviews, checks, proibir pushes).

Resultado: revisões previsíveis, menos regressões e histórico mais limpo (squash no merge de PRs).

---

## 7) Segurança: Dependabot, CodeQL e secrets

- `dependabot.yml`: abre PRs automáticas de atualização de dependências.
- CodeQL: análise estática automática com workflow pronto.
- Secrets/Environments: guarde chaves em Settings → Secrets and variables; consuma nos workflows com `${{ secrets.MINHA_CHAVE }}`.

Práticas recomendadas:

- Nunca comite segredos; use secrets + environments (staging/prod) com aprovação.
- Ative secret scanning e alerts.

---

## 8) Passo a passo sugerido para a aula

1) Criar um repositório novo no GitHub a partir do demo (ou importar a pasta `demo-github-app/` como repositório separado).
2) Ativar Branch Protection em `main` exigindo 1 review e CI verde.
3) Criar uma branch `feat/sum-validate`, abrir PR e ver os checks do CI.
4) Simular um teste falho e observar o bloqueio do merge; depois corrigir.
5) Fazer merge (squash), criar tag `v0.1.0` e ver a release com artefatos.
6) Abrir uma Issue com template; linkar ao PR usando `Closes #N`.
7) Habilitar CodeQL e Dependabot; aceitar uma atualização automática.

Extensões opcionais:

- Publicar uma imagem Docker no GHCR a partir do Actions.
- Usar Projects para organizar backlog e milestones.
- Demonstrar Codespaces (ambiente pronto em um clique).

---

## 9) Dicas de troubleshooting no GitHub Actions

- Use `actions/setup-node@v4` com `cache: npm` e lockfile para builds mais rápidos.
- Inspecione logs de cada step; adicione `--verbose` ou `ACTIONS_STEP_DEBUG` quando preciso.
- Separe jobs por responsabilidade (lint/test/build) e reuso com composite actions.
- Para workflows em monorepo, use `paths`/`paths-ignore` e `working-directory` por serviço.

---

## 10) Próximos passos

- Expandir o demo com autenticação e testes de integração.
- Adicionar cobertura de testes (badge) e análise com `codecov`.
- Configurar ambientes (staging/prod) com aprovação manual (jobs com `environment:` e `protection rules`).

---

Com este conteúdo e o mini-projeto, seus alunos conseguem vivenciar o ciclo completo: abrir uma issue, criar branch, abrir PR, passar na esteira de CI, fazer merge com governança, gerar release versionada e manter a segurança em dia.


---

## 11) .gitignore em detalhe (como funciona de verdade)

O `.gitignore` informa ao Git quais arquivos não devem ser rastreados (untracked). Ele não apaga nem remove do histórico arquivos já rastreados; apenas evita que novos sejam adicionados por engano.

- Onde colocar: pode haver vários `.gitignore` ao longo do repo; cada um vale para sua pasta e subpastas.
- Precedência e especificidade: regras mais específicas sobrepõem genéricas. A avaliação considera todos os `.gitignore` do caminho.
- Sintaxe de padrões:
	- `#` comentários.
	- `/arquivo.log` ignora apenas na raiz do repositório.
	- `arquivo.log` ignora em qualquer pasta.
	- `pasta/` ignora a pasta toda.
	- `*.log` ignora extensões (.log em qualquer lugar).
	- `**/build/` ignora pastas `build` em qualquer profundidade.
	- `!` nega um padrão anterior (re-incluir), ex.: manter um README dentro de `dist/`:
		```
		dist/
		!dist/README.md
		```
- Arquivos já rastreados: para parar de rastrear sem apagar do disco:
	```bash
	git rm --cached caminho/arquivo
	git commit -m "chore: stop tracking arquivo"
	```
- Excludes locais e globais:
	- Local: `.git/info/exclude` (apenas no seu clone).
	- Global: `~/.config/git/ignore` (ou conforme `git config --global core.excludesfile`). Útil para ignorar arquivos de IDE.
- Depuração de regras:
	```bash
	git check-ignore -v caminho/arquivo  # mostra qual regra está casando
	```

Exemplo comentado (Node):

```gitignore
# dependências
node_modules/

# builds/bundles
dist/
build/

# logs
*.log
npm-debug.log*

# variáveis
.env
.env.local
!.env.example  # mantém um exemplo versionado

# SO/IDE
.DS_Store
*.swp
.idea/
```

Dicas:
- Ignore dependências e artefatos de build; não ignore lockfiles se a política do time exigir reprodutibilidade.
- Use também `.dockerignore` para acelerar builds de Docker (reduz o contexto enviado ao daemon).

---

## 12) GitHub Actions: anatomia do workflow (YAML)

Estrutura mínima:

```yaml
name: CI
on: [push, pull_request]     # eventos
jobs:
	build:                      # cada job roda em um runner isolado
		runs-on: ubuntu-latest
		permissions:              # reduza escopo do GITHUB_TOKEN
			contents: read
		env:
			NODE_ENV: test
		strategy:
			matrix:
				node-version: [18, 20]
		concurrency:
			group: ${{ github.workflow }}-${{ github.ref }}
			cancel-in-progress: true
		steps:
			- uses: actions/checkout@v4
			- uses: actions/setup-node@v4
				with:
					node-version: ${{ matrix.node-version }}
					cache: npm
			- run: npm ci
			- run: npm test
			- if: failure()
				run: cat logs/output.txt || true
```

Conceitos-chave:

- `on`: define gatilhos (push, pull_request, schedule, workflow_dispatch, release...).
- `jobs`: agrupam steps; podem depender de outros via `needs`.
- `steps`: execução de ações (`uses:`) ou shell (`run:`); podem ter `id:` e `working-directory`.
- `env`/`secrets`: variáveis e segredos (vide seção 14).
- `permissions`: princípio do menor privilégio para o token automático.
- `concurrency`: evita filas desnecessárias e corrida entre execuções da mesma ref.
- Cache e artefatos: `actions/cache`, `upload-artifact` e `download-artifact`.
- Reuso: workflows reutilizáveis com `workflow_call` e composite actions para compartilhar lógica.

Boas práticas:
- Nomeie jobs por responsabilidade (lint/test/build/deploy).
- Limite execução por paths em monorepos (`paths`, `paths-ignore`).
- Defina `timeout-minutes` e trate logs sensíveis (secrets são mascarados automaticamente).

---

## 13) Crie seu próprio pipeline (modelos práticos)

Node básico:
```yaml
name: node-ci
on: [push, pull_request]
jobs:
	test:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v4
			- uses: actions/setup-node@v4
				with:
					node-version: 20
					cache: npm
			- run: npm ci
			- run: npm test
```

Python (pytest):
```yaml
name: py-ci
on: [push, pull_request]
jobs:
	test:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v4
			- uses: actions/setup-python@v5
				with:
					python-version: '3.11'
					cache: 'pip'
			- run: pip install -r requirements.txt
			- run: pytest -q
```

Java (Maven):
```yaml
name: java-maven-ci
on: [push, pull_request]
jobs:
	build:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v4
			- uses: actions/setup-java@v4
				with:
					distribution: 'temurin'
					java-version: '21'
					cache: 'maven'
			- run: mvn -B -ntp verify
```

Docker + GHCR:
```yaml
name: docker
on:
	push:
		branches: [ main ]
jobs:
	build-push:
		runs-on: ubuntu-latest
		permissions:
			contents: read
			packages: write
		steps:
			- uses: actions/checkout@v4
			- uses: docker/login-action@v3
				with:
					registry: ghcr.io
					username: ${{ github.actor }}
					password: ${{ secrets.GITHUB_TOKEN }}
			- uses: docker/build-push-action@v6
				with:
					push: true
					tags: ghcr.io/${{ github.repository }}/app:latest
```

Monorepo (executar apenas quando `apps/api` mudar):
```yaml
on:
	push:
		paths:
			- 'apps/api/**'
			- '.github/workflows/api-ci.yml'
```

---

## 14) Environments, secrets e variáveis

Secrets em Settings → Secrets and variables → Actions. Exemplo de uso:

```yaml
steps:
	- run: curl -H "Authorization: Bearer $TOKEN" "$API_URL/health"
		env:
			TOKEN: ${{ secrets.API_TOKEN }}
			API_URL: https://staging.example.com
```

Ambientes com proteção e aprovadores:

```yaml
jobs:
	deploy:
		environment: production   # configure required reviewers no GitHub
		steps:
			- run: ./scripts/deploy.sh
```

---

## 15) CODEOWNERS em detalhe

Arquivo: `.github/CODEOWNERS` (ou na raiz). Regras mapeiam caminhos → proprietários.

Sintaxe e exemplos:

```
*                @org/equipe-backend
infra/**         @org/platform
docs/**          @usuario1 @usuario2
*.md             @org/time-docs
```

Notas importantes:

- Proprietários podem ser usuários ou times (`@org/time`).
- A regra mais específica vence (semelhante ao `.gitignore`).
- Para exigir aprovação de CODEOWNERS, habilite “Require review from Code Owners” em Branch Protection.
- Em monorepos, use por serviço/diretório (`apps/api/** @org/time-api`).
- Teste seus padrões abrindo PRs de exemplo e observando quem é solicitado automaticamente.

Exemplo do demo:

```
infra/git/demo-github-app/** @josinoif
```

