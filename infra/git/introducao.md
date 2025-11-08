## Introdução ao Controle de Versão com Git

Este material apresenta uma visão prática e atual do controle de versão com Git, conectando conceitos fundamentais às necessidades de projetos modernos no mercado (times distribuídos, CI/CD, code review, segurança e governança).

### Objetivos de aprendizagem

- Entender por que controle de versão é imprescindível em projetos profissionais.
- Compreender os conceitos-chave do Git e seu fluxo básico de trabalho.
- Escolher e aplicar estratégias de branches adequadas (GitHub Flow, Git Flow, Trunk-Based).
- Integrar Git com práticas de mercado: CI/CD, code review, versionamento semântico, convenções de commit.
- Aplicar segurança e governança: branches protegidos, assinaturas de commit, revisão obrigatória, secrets.
- Dominar comandos essenciais do dia a dia e lidar com situações comuns (conflitos, revert, bisect).

---

## 1. Por que controle de versão?

Em times e produtos reais, código muda continuamente. Sem controle de versão, é quase impossível:

- Colaborar de forma segura (evitar sobrescrever trabalho alheio).
- Rastrear histórico, comparar mudanças e identificar regressões.
- Revisar código (code review) e garantir qualidade.
- Automatizar pipelines (build, teste, deploy) e gerar releases confiáveis.
- Auditar quem mudou o quê e quando, atendendo requisitos de compliance.

Git é o sistema de controle de versão distribuído mais usado no mercado. Ele permite que cada desenvolvedor tenha um repositório completo localmente (incluindo histórico), tornando operações como commits, branches e diffs muito rápidas e resilientes.

Comparativo rápido:

- Centralizado (ex.: Subversion): simples, porém dependente do servidor e menos flexível para branches.
- Distribuído (Git): autonomia local, branches baratos, fluxos modernos de colaboração e CI/CD.

---

## 2. Conceitos essenciais do Git

- Repositório (repo): diretório versionado que armazena histórico e metadados.
- Working directory: seus arquivos no disco, editáveis.
- Staging area (index): área de preparação para o próximo commit.
- Commit: snapshot atômico das mudanças com autor, data e mensagem.
- Branch: ponteiro móvel para uma linha de desenvolvimento (ex.: main, develop, feature/x).
- Merge: une históricos de branches (pode criar commit de merge).
- Rebase: reaplica commits “por cima” de outra base, mantendo histórico linear.
- Tag: marcador imutável de um ponto do histórico (usado em releases).
- Remote: cópia do repositório em um servidor (ex.: GitHub, GitLab, Bitbucket).

Fluxo básico (local e remoto):

1) editar arquivos → 2) adicionar ao staging → 3) commit → 4) sincronizar com remoto (pull/push) → 5) abrir PR/MR para revisão.

---

## 3. Fluxos de trabalho modernos (branches e colaboração)

Escolher a estratégia depende do tamanho do time, criticidade do produto e cadência de release.

### 3.1 GitHub Flow (simples e contínuo)

- Branch principal: `main` (sempre deployável).
- Para cada mudança: criar branch curta a partir de `main` → abrir Pull Request → revisão e CI → merge em `main` → deploy.
- Indicado para produtos SaaS e times com deploy contínuo.

### 3.2 Git Flow (lançamentos programados)

- Branches: `main` (releases), `develop` (integração), `feature/*`, `release/*`, `hotfix/*`.
- Bom para produtos com janelas de release e necessidade de estabilização.
- Cuidado com complexidade e tempo de ciclo mais longo.

### 3.3 Trunk-Based Development (TBD)

- Um tronco principal (geralmente `main`) com integrações frequentes (múltiplos merges por dia).
- Branches muito curtas (horas/dias) e feature toggles para habilitar/desabilitar funcionalidades em produção.
- Favorece fluxo rápido, evita grandes divergências e reduz conflitos.

Recomendações gerais:

- Branches curtas, commits pequenos e frequentes; CI rápido e obrigatório.
- Proteja `main`/`develop`: revisão obrigatória, status checks (CI verde), proibição de pushes diretos.
- Use PRs com descrição clara, escopo pequeno e checklist de revisão.

---

## 4. Integração com práticas de mercado

### 4.1 CI/CD

- CI (Continuous Integration): a cada PR/commit, builda, testa, linta e verifica segurança automaticamente.
- CD (Continuous Delivery/Deployment): após merge/tag, gera artefatos e publica em ambientes (staging/prod).
- Benefícios: feedback rápido, qualidade consistente, releases previsíveis.

### 4.2 Mensagens de commit e Conventional Commits

- Mensagens claras e curtas no título; corpo explica “o porquê”.
- Conventional Commits padroniza tipo/escopo: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:` etc.
- Exemplos:
  - `feat(auth): suporta login via OAuth2`
  - `fix(cart): corrige cálculo de frete`

### 4.3 Versionamento Semântico (SemVer)

- Formato: MAJOR.MINOR.PATCH (ex.: 2.5.1).
- Regras:
  - MAJOR: mudanças incompatíveis.
  - MINOR: novas funcionalidades compatíveis.
  - PATCH: correções compatíveis.
- Combine com tags Git (ex.: `v2.5.1`) e changelogs automáticos.

### 4.4 Changelog e releases

- Gere changelog por tags/commits (pode integrar com Conventional Commits).
- Crie releases no provedor git com notas, artefatos e checks.

### 4.5 Governança e qualidade

- CODEOWNERS para revisar áreas do código.
- Templates de PR/issue para guiar contribuições.
- Branches protegidas e políticas de merge (squash/merge/rebase) padronizadas.

### 4.6 Segurança e compliance

- Assine commits e tags (GPG/SSH) para garantir autoria.
- Habilite secret scanning e verificação de dependências.
- Nunca comitar segredos; use variáveis de ambiente, cofres (ex.: Vault, SOPS), ou `git-crypt` quando aplicável.
- Audite histórico e permissões; evite força de push em branches protegidas.

### 4.7 Arquivos binários e repositórios grandes

- Evite binários no repo; prefira artefatos em registries/storage.
- Se inevitável, use Git LFS para rastrear binários grandes.

---

## 5. Guia de comandos essenciais (Linux/Bash)

Observação: execute os comandos no terminal dentro do diretório do projeto.

### 5.1 Inicialização e clonagem

```bash
# iniciar um repositório local
git init

# clonar repositório remoto
git clone https://example.com/usuario/projeto.git

# adicionar remoto a um repo já iniciado
git remote add origin https://example.com/usuario/projeto.git
```

### 5.2 Ciclo básico

```bash
# ver status do diretório de trabalho e staging
git status

# adicionar mudanças ao staging (seletivo ou tudo)
git add caminho/arquivo
git add .

# criar commit
git commit -m "feat: descrição curta do que mudou"

# visualizar histórico
git log --oneline --graph --decorate --all

# comparar diferenças
git diff                # working ↔ staging
git diff --staged       # staging ↔ último commit
```

### 5.3 Branches e navegação

```bash
# listar e criar branches
git branch
git switch -c feature/minha-feature    # ou: git checkout -b feature/minha-feature

# mudar de branch
git switch main                        # ou: git checkout main

# excluir branch já mesclada
git branch -d feature/minha-feature
```

### 5.4 Sincronização com remoto

```bash
git pull --rebase origin main   # atualiza sua branch mantendo histórico linear
git push -u origin main         # envia commits e define upstream
```

### 5.5 Merge e rebase

```bash
# realizar merge da branch de funcionalidade em main
git switch main
git pull --rebase origin main
git merge feature/minha-feature

# rebase (reaplicar commits por cima da base mais nova)
git switch feature/minha-feature
git rebase main
```

### 5.6 Tags e releases

```bash
# criar tag anotada (recomendada para releases)
git tag -a v1.2.0 -m "Release 1.2.0"
git push origin v1.2.0
```

### 5.7 Conflitos e resolução

```bash
# após aparecerem marcadores de conflito <<<<<<<, edite arquivos e
# marque como resolvidos adicionando ao staging
git add caminho/arquivo
git commit   # conclui o merge/rebase
```

### 5.8 Recuperação e inspeção

```bash
git reflog                 # histórico de movimentos de HEAD (salva-vidas)
git stash                  # guarda mudanças locais temporariamente
git stash pop              # reaplica mudanças guardadas
git revert <hash>          # cria commit que desfaz outro (seguro para remoto)
git cherry-pick <hash>     # aplica commit específico na sua branch
git bisect start           # busca binária para encontrar commit que quebrou algo
```

---

## 6. Boas práticas para equipes

- Commits pequenos, focados e frequentes; PRs curtos facilitam revisão.
- Mensagens de commit padronizadas (Conventional Commits) + descrição do porquê.
- CI obrigatório e rápido; não faça merge com build/testes falhando.
- Padronize política de merge (squash para histórico mais limpo em projetos de produto).
- Proteja branches principais; exija pelo menos 1–2 aprovações em PRs.
- Use `.gitignore` para evitar arquivos temporários e segredos.
- Evite reescrever histórico público (não use `push --force` em branches compartilhadas).
- Documente o fluxo no repositório (README, CONTRIBUTING, templates de PR/issue, CODEOWNERS).

Exemplo mínimo de `.gitignore` para projetos Node (ajuste ao seu stack):

```gitignore
node_modules/
dist/
.env
.DS_Store
*.log
```

Assinatura de commits (opcional, recomendado):

```bash
# configurar key GPG/SSH e assinar automaticamente
git config --global user.signingkey <ID_DA_CHAVE>
git config --global commit.gpgsign true
```

---

## 7. Exercícios práticos (para sala)

1) Inicialização e primeiro commit
	- Crie um diretório e um repo (`git init`), adicione `README.md`, faça commit.
	- Edite o README, use `git diff`, `git add -p` para stage seletivo e `git commit`.

2) Branch de funcionalidade e PR (simulado)
	- Crie `feature/calc-imposto`, implemente função e teste.
	- Abra PR no seu provedor (GitHub/GitLab) ou simule revisão pedindo colega para revisar o diff local.

3) Conflito intencional
	- Em duas branches, altere a mesma linha; tente fazer merge e resolva o conflito.

4) Rebase e histórico linear
	- Atualize sua branch com `git rebase main`, resolva conflitos e finalize.

5) Release e tag
	- Gere uma tag `v0.1.0`, escreva notas de release (changelog curto) e envie a tag.

6) Recuperação rápida
	- Use `git reflog` para encontrar um ponto anterior e criar uma branch de recuperação.

Desafio opcional:
- Configure um pipeline CI mínimo (ex.: lint + testes) que rode em cada PR.

---

## 8. Quando usar merge, rebase, revert, cherry-pick?

- Merge: integração de branches com preservação de histórico paralelo (bom para PRs).
- Rebase: manter histórico linear em branches de curta duração (use antes do PR).
- Revert: desfazer um commit de forma segura no histórico público.
- Cherry-pick: portar um fix específico para outra branch (ex.: hotfix para release).

Erros comuns:

- “Detached HEAD”: crie uma branch em cima do commit atual (`git switch -c hotfix/tmp`).
- `push --force` em branch compartilhada: evite; prefira `--force-with-lease` e somente quando necessário.
- Conflitos recorrentes: integrar cedo e frequentemente; reduzir tempo de vida das branches.

---

## 9. Monorepo, submódulos e alternativas

- Monorepo: um repositório para vários pacotes/módulos (prático para coordenação e atomic commits). Requer ferramentas (Nx, Turborepo, Lerna) e CI escalável.
- Multirepo: um repo por serviço; isola responsabilidades, mas pode complicar coordenação de versões.
- Submódulos/Subtree: integram outro repo como dependência; use com parcimônia (aumentam complexidade).

Escolha de arquitetura deve considerar tamanho do time, acoplamento entre componentes e maturidade da infraestrutura.

---

## 10. Checklist rápido para projetos no mercado

- [ ] Estratégia de branches definida (e documentada).
- [ ] Branches protegidas e revisão obrigatória.
- [ ] CI obrigatório (build, teste, lint, segurança).
- [ ] Padrão de commits (Conventional Commits) e SemVer.
- [ ] Geração de changelog e releases por tag.
- [ ] `.gitignore` adequado ao stack; segredos fora do repo.
- [ ] Secret scanning e dependabot/sast ativados.
- [ ] CODEOWNERS, templates de PR/issue, CONTRIBUTING.
- [ ] Assinatura de commits/tags para auditoria (se necessário).

---

## 11. Referências para aprofundamento

- Documentação oficial do Git: https://git-scm.com/doc
- Livro Pro Git (gratuito): https://git-scm.com/book
- Conventional Commits: https://www.conventionalcommits.org/
- Semantic Versioning: https://semver.org/

---

Com estas bases, você está pronto para conduzir aulas e aplicar Git de forma profissional, alinhado às práticas de mercado e às demandas de produtos modernos.

